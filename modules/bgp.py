"""
Sopel module for BGP/RIPE database queries.
Downloads and queries RIPE database from https://ftp.ripe.net/ripe/dbase/
Uses SQLite for fast queries.
"""
import gzip
import ipaddress
import os
import sqlite3
import sys
import threading
from typing import Dict, List, Optional

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, get_command_prefix, IRCFormatter, get_module_logger

logger = get_module_logger(__name__)
http = HTTPClient(max_size=500 * 1024 * 1024)  # 500MB max for database
formatter = IRCFormatter()

# Database file paths
DB_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'
)
DB_FILE = os.path.join(DB_DIR, 'ripe.db.gz')
SQLITE_DB = os.path.join(DB_DIR, 'ripe.db.sqlite')
DB_URL = 'https://ftp.ripe.net/ripe/dbase/ripe.db.gz'

# Thread lock for database operations
db_lock = threading.Lock()


def ensure_db_dir():
    """Ensure database directory exists."""
    os.makedirs(DB_DIR, exist_ok=True)


def get_db_connection():
    """Get SQLite database connection."""
    # Use WAL mode for better concurrency
    conn = sqlite3.connect(
        SQLITE_DB, check_same_thread=False, timeout=30.0
    )
    conn.execute('PRAGMA journal_mode=WAL')
    return conn


def init_sqlite_db():
    """Initialize SQLite database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # ASN (aut-num) table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aut_num (
            asn TEXT PRIMARY KEY,
            as_name TEXT,
            org TEXT,
            country TEXT
        )
    ''')

    # ASN multi-value fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aut_num_descr (
            asn TEXT,
            descr TEXT,
            FOREIGN KEY (asn) REFERENCES aut_num(asn)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aut_num_remarks (
            asn TEXT,
            remarks TEXT,
            FOREIGN KEY (asn) REFERENCES aut_num(asn)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aut_num_admin_c (
            asn TEXT,
            admin_c TEXT,
            FOREIGN KEY (asn) REFERENCES aut_num(asn)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aut_num_tech_c (
            asn TEXT,
            tech_c TEXT,
            FOREIGN KEY (asn) REFERENCES aut_num(asn)
        )
    ''')

    # IPv4/IPv6 (inetnum/inet6num) table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inet_num (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inetnum TEXT,
            netname TEXT,
            status TEXT,
            range_start TEXT,
            range_end TEXT,
            prefix TEXT,
            prefix_len INTEGER,
            is_ipv6 INTEGER DEFAULT 0
        )
    ''')

    # Inetnum multi-value fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inet_num_descr (
            inet_num_id INTEGER,
            descr TEXT,
            FOREIGN KEY (inet_num_id) REFERENCES inet_num(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inet_num_country (
            inet_num_id INTEGER,
            country TEXT,
            FOREIGN KEY (inet_num_id) REFERENCES inet_num(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inet_num_org (
            inet_num_id INTEGER,
            org TEXT,
            FOREIGN KEY (inet_num_id) REFERENCES inet_num(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inet_num_admin_c (
            inet_num_id INTEGER,
            admin_c TEXT,
            FOREIGN KEY (inet_num_id) REFERENCES inet_num(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inet_num_tech_c (
            inet_num_id INTEGER,
            tech_c TEXT,
            FOREIGN KEY (inet_num_id) REFERENCES inet_num(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inet_num_remarks (
            inet_num_id INTEGER,
            remarks TEXT,
            FOREIGN KEY (inet_num_id) REFERENCES inet_num(id)
        )
    ''')

    # Organisation table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organisation (
            org_id TEXT PRIMARY KEY,
            org_name TEXT,
            country TEXT
        )
    ''')

    # Organisation multi-value fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organisation_descr (
            org_id TEXT,
            descr TEXT,
            FOREIGN KEY (org_id) REFERENCES organisation(org_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organisation_remarks (
            org_id TEXT,
            remarks TEXT,
            FOREIGN KEY (org_id) REFERENCES organisation(org_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organisation_admin_c (
            org_id TEXT,
            admin_c TEXT,
            FOREIGN KEY (org_id) REFERENCES organisation(org_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organisation_tech_c (
            org_id TEXT,
            tech_c TEXT,
            FOREIGN KEY (org_id) REFERENCES organisation(org_id)
        )
    ''')

    # Create indexes for fast lookups
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_aut_num_asn ON aut_num(asn)'
    )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_inet_num_org ON inet_num_org(org)'
    )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_inet_num_country '
        'ON inet_num_country(country)'
    )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_inet_num_range_start '
        'ON inet_num(range_start)'
    )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_inet_num_range_end '
        'ON inet_num(range_end)'
    )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_inet_num_prefix '
        'ON inet_num(prefix, prefix_len)'
    )
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_org_name ON organisation(org_name)'
    )

    conn.commit()
    conn.close()
    logger.info('SQLite database initialized')


def parse_ripe_object(lines: List[str]) -> Dict[str, str]:
    """Parse a RIPE database object from lines."""
    obj = {}
    current_key = None
    current_value = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if ':' in line:
            # Save previous key-value
            if current_key:
                obj[current_key] = '\n'.join(current_value).strip()

            # New key-value pair
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if key in obj:
                # Multi-value field - convert to list
                if not isinstance(obj[key], list):
                    obj[key] = [obj[key]]
                obj[key].append(value)
                current_key = None
            else:
                current_key = key
                current_value = [value]
        elif current_key and line.startswith(' '):
            # Continuation line
            current_value.append(line.strip())

    # Save last key-value
    if current_key:
        obj[current_key] = '\n'.join(current_value).strip()

    return obj


def parse_ip_range(inetnum: str) -> tuple:
    """Parse IP range from inetnum field.
    Returns (range_start, range_end, prefix, prefix_len, is_ipv6).
    """
    inetnum = inetnum.strip()
    is_ipv6 = ':' in inetnum

    if '-' in inetnum:
        # Range format: 192.0.2.0 - 192.0.2.255
        parts = inetnum.split('-', 1)
        start = parts[0].strip()
        end = parts[1].strip()
        try:
            start_ip = ipaddress.ip_address(start)
            end_ip = ipaddress.ip_address(end)
            return (str(start_ip), str(end_ip), None, None, is_ipv6)
        except ValueError:
            return (None, None, None, None, is_ipv6)
    elif '/' in inetnum:
        # CIDR format: 192.0.2.0/24
        try:
            network = ipaddress.ip_network(inetnum, strict=False)
            return (
                str(network.network_address),
                str(network.broadcast_address),
                str(network.network_address),
                network.prefixlen,
                is_ipv6
            )
        except ValueError:
            return (None, None, None, None, is_ipv6)
    else:
        # Single IP or invalid
        try:
            ip = ipaddress.ip_address(inetnum)
            return (str(ip), str(ip), None, None, is_ipv6)
        except ValueError:
            return (None, None, None, None, is_ipv6)


def build_sqlite_db():
    """Build SQLite database from RIPE database file."""
    if not os.path.exists(DB_FILE):
        logger.error('RIPE database file not found')
        return False

    logger.info('Building SQLite database from RIPE database...')
    init_sqlite_db()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute('DELETE FROM aut_num_descr')
    cursor.execute('DELETE FROM aut_num_remarks')
    cursor.execute('DELETE FROM aut_num_admin_c')
    cursor.execute('DELETE FROM aut_num_tech_c')
    cursor.execute('DELETE FROM aut_num')
    cursor.execute('DELETE FROM inet_num_descr')
    cursor.execute('DELETE FROM inet_num_country')
    cursor.execute('DELETE FROM inet_num_org')
    cursor.execute('DELETE FROM inet_num_admin_c')
    cursor.execute('DELETE FROM inet_num_tech_c')
    cursor.execute('DELETE FROM inet_num_remarks')
    cursor.execute('DELETE FROM inet_num')
    cursor.execute('DELETE FROM organisation_descr')
    cursor.execute('DELETE FROM organisation_remarks')
    cursor.execute('DELETE FROM organisation_admin_c')
    cursor.execute('DELETE FROM organisation_tech_c')
    cursor.execute('DELETE FROM organisation')
    conn.commit()

    current_object = []
    in_object = False
    object_type = None
    count = 0

    try:
        with gzip.open(
            DB_FILE, 'rt', encoding='latin-1', errors='ignore'
        ) as f:
            for line in f:
                line = line.rstrip('\n\r')

                # Check if this is the start of an object
                if line.startswith('aut-num:'):
                    if in_object and current_object:
                        _process_object(cursor, current_object, object_type)
                        count += 1
                        if count % 10000 == 0:
                            conn.commit()
                            logger.info(f'Processed {count} objects...')

                    current_object = [line]
                    in_object = True
                    object_type = 'aut-num'
                elif (line.startswith('inetnum:') or
                      line.startswith('inet6num:')):
                    if in_object and current_object:
                        _process_object(cursor, current_object, object_type)
                        count += 1
                        if count % 10000 == 0:
                            conn.commit()
                            logger.info(f'Processed {count} objects...')

                    current_object = [line]
                    in_object = True
                    object_type = (
                        'inetnum' if line.startswith('inetnum:')
                        else 'inet6num'
                    )
                elif line.startswith('organisation:'):
                    if in_object and current_object:
                        _process_object(cursor, current_object, object_type)
                        count += 1
                        if count % 10000 == 0:
                            conn.commit()
                            logger.info(f'Processed {count} objects...')

                    current_object = [line]
                    in_object = True
                    object_type = 'organisation'
                elif line == '' and in_object:
                    # End of object
                    if current_object:
                        _process_object(cursor, current_object, object_type)
                        count += 1
                        if count % 10000 == 0:
                            conn.commit()
                            logger.info(f'Processed {count} objects...')
                    current_object = []
                    in_object = False
                    object_type = None
                elif in_object:
                    current_object.append(line)

            # Process last object
            if in_object and current_object:
                _process_object(cursor, current_object, object_type)
                count += 1

        conn.commit()
        logger.info(
            f'SQLite database built successfully: {count} objects processed'
        )
        return True

    except Exception as e:
        logger.error(f'Error building SQLite database: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()


def _get_field_values(obj: Dict, key: str) -> List[str]:
    """Get field values from object, returning as list."""
    value = obj.get(key, [])
    if isinstance(value, list):
        return [str(v).strip() for v in value if v]
    elif value:
        return [str(value).strip()]
    return []


def _get_first_field_value(obj: Dict, key: str, default: str = '') -> str:
    """Get first field value from object."""
    values = _get_field_values(obj, key)
    return values[0] if values else default


def _process_object(cursor, lines: List[str], obj_type: str):
    """Process a RIPE object and insert into SQLite."""
    obj = parse_ripe_object(lines)

    if obj_type == 'aut-num':
        asn = _get_first_field_value(obj, 'aut-num', '').strip()
        if not asn:
        return

        # Insert main record
        cursor.execute('''
            INSERT OR REPLACE INTO aut_num
            (asn, as_name, org, country)
            VALUES (?, ?, ?, ?)
        ''', (
            asn,
            _get_first_field_value(obj, 'as-name'),
            _get_first_field_value(obj, 'org'),
            _get_first_field_value(obj, 'country')
        ))

        # Insert multi-value fields
        for descr in _get_field_values(obj, 'descr'):
            cursor.execute(
                'INSERT INTO aut_num_descr (asn, descr) VALUES (?, ?)',
                (asn, descr)
            )
        for remarks in _get_field_values(obj, 'remarks'):
            cursor.execute(
                'INSERT INTO aut_num_remarks (asn, remarks) VALUES (?, ?)',
                (asn, remarks)
            )
        for admin_c in _get_field_values(obj, 'admin-c'):
            cursor.execute(
                'INSERT INTO aut_num_admin_c (asn, admin_c) VALUES (?, ?)',
                (asn, admin_c)
            )
        for tech_c in _get_field_values(obj, 'tech-c'):
            cursor.execute(
                'INSERT INTO aut_num_tech_c (asn, tech_c) VALUES (?, ?)',
                (asn, tech_c)
            )

    elif obj_type in ('inetnum', 'inet6num'):
        inetnum = (_get_first_field_value(obj, 'inetnum') or
                   _get_first_field_value(obj, 'inet6num', ''))
        inetnum = inetnum.strip()
        if not inetnum:
            return

        range_start, range_end, prefix, prefix_len, is_ipv6 = (
            parse_ip_range(inetnum)
        )

        # Insert main record
        cursor.execute('''
            INSERT INTO inet_num
            (inetnum, netname, status, range_start, range_end, prefix,
             prefix_len, is_ipv6)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inetnum,
            _get_first_field_value(obj, 'netname'),
            _get_first_field_value(obj, 'status'),
            range_start,
            range_end,
            prefix,
            prefix_len,
            1 if is_ipv6 else 0
        ))

        inet_num_id = cursor.lastrowid

        # Insert multi-value fields
        for descr in _get_field_values(obj, 'descr'):
            cursor.execute(
                'INSERT INTO inet_num_descr (inet_num_id, descr) '
                'VALUES (?, ?)',
                (inet_num_id, descr)
            )
        for country in _get_field_values(obj, 'country'):
            cursor.execute(
                'INSERT INTO inet_num_country (inet_num_id, country) '
                'VALUES (?, ?)',
                (inet_num_id, country)
            )
        for org in _get_field_values(obj, 'org'):
            cursor.execute(
                'INSERT INTO inet_num_org (inet_num_id, org) VALUES (?, ?)',
                (inet_num_id, org)
            )
        for admin_c in _get_field_values(obj, 'admin-c'):
            cursor.execute(
                'INSERT INTO inet_num_admin_c (inet_num_id, admin_c) '
                'VALUES (?, ?)',
                (inet_num_id, admin_c)
            )
        for tech_c in _get_field_values(obj, 'tech-c'):
            cursor.execute(
                'INSERT INTO inet_num_tech_c (inet_num_id, tech_c) '
                'VALUES (?, ?)',
                (inet_num_id, tech_c)
            )
        for remarks in _get_field_values(obj, 'remarks'):
            cursor.execute(
                'INSERT INTO inet_num_remarks (inet_num_id, remarks) '
                'VALUES (?, ?)',
                (inet_num_id, remarks)
            )

    elif obj_type == 'organisation':
        org_id = _get_first_field_value(obj, 'organisation', '').strip()
        if not org_id:
        return

        # Insert main record
        cursor.execute('''
            INSERT OR REPLACE INTO organisation
            (org_id, org_name, country)
            VALUES (?, ?, ?)
        ''', (
            org_id,
            _get_first_field_value(obj, 'org-name'),
            _get_first_field_value(obj, 'country')
        ))

        # Insert multi-value fields
        for descr in _get_field_values(obj, 'descr'):
            cursor.execute(
                'INSERT INTO organisation_descr (org_id, descr) '
                'VALUES (?, ?)',
                (org_id, descr)
            )
        for remarks in _get_field_values(obj, 'remarks'):
            cursor.execute(
                'INSERT INTO organisation_remarks (org_id, remarks) '
                'VALUES (?, ?)',
                (org_id, remarks)
            )
        for admin_c in _get_field_values(obj, 'admin-c'):
            cursor.execute(
                'INSERT INTO organisation_admin_c (org_id, admin_c) '
                'VALUES (?, ?)',
                (org_id, admin_c)
            )
        for tech_c in _get_field_values(obj, 'tech-c'):
            cursor.execute(
                'INSERT INTO organisation_tech_c (org_id, tech_c) '
                'VALUES (?, ?)',
                (org_id, tech_c)
            )


def download_database(force: bool = False) -> bool:
    """Download RIPE database if it doesn't exist or force is True."""
    ensure_db_dir()

    if os.path.exists(DB_FILE) and not force:
        logger.info(f'RIPE database already exists: {DB_FILE}')
        return True

    logger.info(f'Downloading RIPE database from {DB_URL}')
    try:
        # Download as binary
        import urllib.request
        with urllib.request.urlopen(DB_URL) as f:
            data = f.read()
            with open(DB_FILE, 'wb') as out:
                out.write(data)

        logger.info(f'RIPE database downloaded: {DB_FILE}')
        return True
    except Exception as e:
        logger.error(f'Failed to download RIPE database: {e}')
        return False


def search_asn(asn: str) -> Optional[Dict[str, str]]:
    """Search for ASN in SQLite database."""
    if not os.path.exists(SQLITE_DB):
        logger.error('SQLite database does not exist')
        return None

    try:
        logger.debug(f'Opening database connection for ASN {asn}')
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.debug('Database connection opened')

        # Normalize ASN (remove AS prefix)
        asn_clean = asn.upper().replace('AS', '').strip()
        asn_with_prefix = f'AS{asn_clean}'

        logger.debug(
            f'Searching for ASN: clean={asn_clean}, '
            f'with_prefix={asn_with_prefix}'
        )

        # Try exact match first, then with AS prefix
        # RIPE database stores ASNs as "AS15169" format
        logger.debug('Executing SQL query')
        cursor.execute('''
            SELECT asn, as_name, org, country
            FROM aut_num
            WHERE asn = ? OR asn = ? OR asn = ?
        ''', (asn_clean, asn_with_prefix, asn.upper().strip()))
        logger.debug('SQL query executed')

        row = cursor.fetchone()
        if not row:
            logger.debug(f'ASN {asn} ({asn_clean}) not found in database')
            conn.close()
            return None

        logger.debug(f'Found ASN {row[0]} in database')

        # Get multi-value fields
        cursor.execute(
            'SELECT descr FROM aut_num_descr WHERE asn = ?', (row[0],)
        )
        descr_list = [r[0] for r in cursor.fetchall()]
        cursor.execute(
            'SELECT remarks FROM aut_num_remarks WHERE asn = ?', (row[0],)
        )
        remarks_list = [r[0] for r in cursor.fetchall()]
        cursor.execute(
            'SELECT admin_c FROM aut_num_admin_c WHERE asn = ?', (row[0],)
        )
        admin_c_list = [r[0] for r in cursor.fetchall()]
        cursor.execute(
            'SELECT tech_c FROM aut_num_tech_c WHERE asn = ?', (row[0],)
        )
        tech_c_list = [r[0] for r in cursor.fetchall()]

        conn.close()

        return {
            'asn': row[0],
            'as-name': row[1] or '',
            'descr': ' | '.join(descr_list) if descr_list else '',
            'org': row[2] or '',
            'country': row[3] or '',
            'admin-c': ' | '.join(admin_c_list) if admin_c_list else '',
            'tech-c': ' | '.join(tech_c_list) if tech_c_list else '',
            'remarks': ' | '.join(remarks_list) if remarks_list else ''
        }
    except Exception as e:
        logger.error(f'Error searching for ASN {asn}: {e}')
        logger.exception(e)
        return None


def search_ip(ip_str: str) -> Optional[Dict[str, str]]:
    """Search for IP address in SQLite database."""
    if not os.path.exists(SQLITE_DB):
        return None

    try:
        ip = ipaddress.ip_address(ip_str)
        is_ipv6 = isinstance(ip, ipaddress.IPv6Address)
    except ValueError:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    ip_str_normalized = str(ip)

    # Try to find matching range
    if is_ipv6:
        cursor.execute('''
            SELECT id, inetnum, netname, status, is_ipv6
            FROM inet_num
            WHERE is_ipv6 = 1
            AND range_start <= ?
            AND range_end >= ?
            ORDER BY prefix_len DESC
            LIMIT 1
        ''', (ip_str_normalized, ip_str_normalized))
    else:
        cursor.execute('''
            SELECT id, inetnum, netname, status, is_ipv6
            FROM inet_num
            WHERE is_ipv6 = 0
            AND range_start <= ?
            AND range_end >= ?
            ORDER BY prefix_len DESC
            LIMIT 1
        ''', (ip_str_normalized, ip_str_normalized))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    inet_num_id = row[0]

    # Get multi-value fields
    cursor.execute(
        'SELECT descr FROM inet_num_descr WHERE inet_num_id = ?',
        (inet_num_id,)
    )
    descr_list = [r[0] for r in cursor.fetchall()]
    cursor.execute(
        'SELECT country FROM inet_num_country WHERE inet_num_id = ?',
        (inet_num_id,)
    )
    country_list = [r[0] for r in cursor.fetchall()]
    cursor.execute(
        'SELECT org FROM inet_num_org WHERE inet_num_id = ?',
        (inet_num_id,)
    )
    org_list = [r[0] for r in cursor.fetchall()]
    cursor.execute(
        'SELECT admin_c FROM inet_num_admin_c WHERE inet_num_id = ?',
        (inet_num_id,)
    )
    admin_c_list = [r[0] for r in cursor.fetchall()]
    cursor.execute(
        'SELECT tech_c FROM inet_num_tech_c WHERE inet_num_id = ?',
        (inet_num_id,)
    )
    tech_c_list = [r[0] for r in cursor.fetchall()]
    cursor.execute(
        'SELECT remarks FROM inet_num_remarks WHERE inet_num_id = ?',
        (inet_num_id,)
    )
    remarks_list = [r[0] for r in cursor.fetchall()]

    conn.close()

    return {
        'inetnum': row[1] if not row[4] else None,
        'inet6num': row[1] if row[4] else None,
        'netname': row[2] or '',
        'descr': ' | '.join(descr_list) if descr_list else '',
        'country': ' | '.join(country_list) if country_list else '',
        'org': ' | '.join(org_list) if org_list else '',
        'admin-c': ' | '.join(admin_c_list) if admin_c_list else '',
        'tech-c': ' | '.join(tech_c_list) if tech_c_list else '',
        'status': row[3] or '',
        'remarks': ' | '.join(remarks_list) if remarks_list else ''
    }


def search_asn_prefixes(asn: str, limit: int = 20) -> List[Dict[str, str]]:
    """Search for IP prefixes associated with an ASN."""
    if not os.path.exists(SQLITE_DB):
        return []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Normalize ASN
        asn_clean = asn.upper().replace('AS', '').strip()
        asn_with_prefix = f'AS{asn_clean}'

        # First get the ASN's org
        cursor.execute('''
            SELECT org FROM aut_num
            WHERE asn = ? OR asn = ? OR asn = ?
        ''', (asn_clean, asn_with_prefix, asn.upper().strip()))

        asn_row = cursor.fetchone()
        if not asn_row or not asn_row[0]:
            conn.close()
            return []

        org = asn_row[0]

        # Find all prefixes for this org
        cursor.execute('''
            SELECT inetnum, netname, country, status, is_ipv6
            FROM inet_num
            WHERE id IN (
                SELECT inet_num_id FROM inet_num_org WHERE org = ?
            )
            ORDER BY prefix_len DESC, inetnum
            LIMIT ?
        ''', (org, limit))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append({
                'inetnum': row[0],
                'netname': row[1] or '',
                'country': row[2] or '',
                'status': row[3] or '',
                'is_ipv6': bool(row[4])
            })

        return results
    except Exception as e:
        logger.error(f'Error searching for ASN prefixes {asn}: {e}')
        logger.exception(e)
        return []


def search_org(org_query: str, limit: int = 3) -> List[Dict[str, str]]:
    """Search for organisation in SQLite database."""
    if not os.path.exists(SQLITE_DB):
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    org_query_lower = org_query.lower()

    cursor.execute('''
        SELECT org_id, org_name, country
        FROM organisation
        WHERE org_id LIKE ? OR org_name LIKE ?
        LIMIT ?
    ''', (f'%{org_query_lower}%', f'%{org_query_lower}%', limit))

    rows = cursor.fetchall()
    results = []

    for row in rows:
        org_id = row[0]
        # Get multi-value fields
        cursor.execute(
            'SELECT descr FROM organisation_descr WHERE org_id = ?',
            (org_id,)
        )
        descr_list = [r[0] for r in cursor.fetchall()]
        cursor.execute(
            'SELECT remarks FROM organisation_remarks WHERE org_id = ?',
            (org_id,)
        )
        remarks_list = [r[0] for r in cursor.fetchall()]
        cursor.execute(
            'SELECT admin_c FROM organisation_admin_c WHERE org_id = ?',
            (org_id,)
        )
        admin_c_list = [r[0] for r in cursor.fetchall()]
        cursor.execute(
            'SELECT tech_c FROM organisation_tech_c WHERE org_id = ?',
            (org_id,)
        )
        tech_c_list = [r[0] for r in cursor.fetchall()]

        results.append({
            'organisation': org_id,
            'org-name': row[1] or '',
            'descr': ' | '.join(descr_list) if descr_list else '',
            'country': row[2] or '',
            'admin-c': ' | '.join(admin_c_list) if admin_c_list else '',
            'tech-c': ' | '.join(tech_c_list) if tech_c_list else '',
            'remarks': ' | '.join(remarks_list) if remarks_list else ''
        })

    conn.close()
    return results


def format_autnum(obj: Dict[str, str]) -> str:
    """Format aut-num object for display."""
    asn = obj.get('asn', 'Unknown')
    as_name = obj.get('as-name', '')
    descr = obj.get('descr', '')
    org = obj.get('org', '')

    result = f"{formatter.bold(asn)}"
    if as_name:
        result += f": {formatter.italic(as_name)}"
    if descr:
        result += f" | {descr}"
    if org:
        result += f" | Org: {formatter.monospace(org)}"
    return result


def format_inetnum(obj: Dict[str, str]) -> str:
    """Format inetnum/inet6num object for display."""
    inetnum = obj.get('inetnum') or obj.get('inet6num', 'Unknown')
    netname = obj.get('netname', '')
    descr = obj.get('descr', '')
    country = obj.get('country', '')
    org = obj.get('org', '')

    result = f"{formatter.bold(inetnum)}"
    if netname:
        result += f" | {formatter.italic(netname)}"
    if descr:
        result += f" | {descr}"
    if country:
        result += f" | {formatter.monospace(country)}"
    if org:
        result += f" | Org: {formatter.monospace(org)}"
    return result


def format_organisation(obj: Dict[str, str]) -> str:
    """Format organisation object for display."""
    org_id = obj.get('organisation', 'Unknown')
    org_name = obj.get('org-name', '')
    country = obj.get('country', '')
    descr = obj.get('descr', '')

    result = f"{formatter.bold(org_id)}"
    if org_name:
        result += f": {formatter.italic(org_name)}"
    if descr:
        result += f" | {descr}"
    if country:
        result += f" | {formatter.monospace(country)}"
    return result


@plugin.command('ripe_update')
@plugin.example('`ripe_update')
def ripe_update(bot, trigger):
    """Update RIPE database and rebuild SQLite index."""
    bot.say('Downloading RIPE database...')
    if not download_database(force=True):
        bot.say('Failed to download RIPE database.')
        return

    bot.say('Building SQLite database (this may take a while)...')
    if build_sqlite_db():
        bot.say('RIPE database updated successfully.')
    else:
        bot.say('Failed to build SQLite database.')


@plugin.command('ripe_asn')
@plugin.example('`ripe_asn AS15169')
@plugin.example('`ripe_asn 15169')
def ripe_asn(bot, trigger):
    """Query RIPE database for ASN information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `ripe_asn <ASN>')
        bot.notice(trigger.nick, 'Example: `ripe_asn AS15169')
        return

    asn_input = trigger.group(2).strip().upper().replace('AS', '')
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return

    logger.info(f'RIPE ASN lookup: {asn_input}')

    if not os.path.exists(SQLITE_DB):
        bot.notice(
            trigger.nick,
            'RIPE database not found. Use {prefix}ripe_update to download it.'
        )
        return

    logger.info(f'Calling search_asn with: {asn_input}')
    try:
        import time
        start = time.time()
        obj = search_asn(asn_input)
        elapsed = time.time() - start
        logger.info(f'search_asn returned in {elapsed:.2f}s: {obj is not None}')
    except Exception as e:
        logger.error(f'Exception in search_asn: {e}')
        logger.exception(e)
        bot.notice(trigger.nick, f'Error querying database: {e}')
        return

    if not obj:
        bot.notice(
            trigger.nick,
            f'ASN {asn_input} not found in RIPE database.'
        )
        return

    logger.debug(f'Formatting result for ASN {asn_input}')
    bot.say(format_autnum(obj))


@plugin.command('ripe_asn_prefixes')
@plugin.example('`ripe_asn_prefixes AS15169')
@plugin.example('`ripe_asn_prefixes 15169')
def ripe_asn_prefixes(bot, trigger):
    """List IP prefixes for an ASN."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `ripe_asn_prefixes <ASN>')
        bot.notice(trigger.nick, 'Example: `ripe_asn_prefixes AS15169')
        return

    asn_input = trigger.group(2).strip().upper().replace('AS', '')
    if not asn_input.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number.')
        return

    logger.info(f'RIPE ASN prefixes lookup: {asn_input}')

    if not os.path.exists(SQLITE_DB):
        bot.notice(
            trigger.nick,
            'RIPE database not found. Use {prefix}ripe_update to download it.'
        )
        return

    prefixes = search_asn_prefixes(asn_input, limit=20)

    if not prefixes:
        bot.notice(
            trigger.nick,
            f'No prefixes found for ASN {asn_input}.'
        )
        return

    # Format as table
    headers = ['Prefix', 'Netname', 'Country', 'Status', 'Type']
    table_data = []
    for prefix in prefixes[:20]:
        inetnum = prefix['inetnum']
        netname = prefix['netname'] or '-'
        country = prefix['country'] or '-'
        status = prefix['status'] or '-'
        ip_type = 'IPv6' if prefix['is_ipv6'] else 'IPv4'
        table_data.append([inetnum, netname, country, status, ip_type])

    table_output = formatter.table(table_data, headers=headers, max_width=400)
    bot.say(
        f'Prefixes for ASN {formatter.bold(asn_input)} '
        f'({len(prefixes)} shown):'
    )
    for line in table_output.split('\n'):
        bot.say(line)


@plugin.command('ripe_ip')
@plugin.example('`ripe_ip 8.8.8.8')
@plugin.example('`ripe_ip 2001:4860:4860::8888')
def ripe_ip(bot, trigger):
    """Query RIPE database for IP address information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `ripe_ip <ip_address>')
        bot.notice(trigger.nick, 'Example: `ripe_ip 8.8.8.8')
        return

    ip_input = trigger.group(2).strip()

    try:
        ipaddress.ip_address(ip_input)
    except ValueError:
        bot.notice(trigger.nick, 'Invalid IP address.')
        return

    logger.info(f'RIPE IP lookup: {ip_input}')

    if not os.path.exists(SQLITE_DB):
        bot.notice(
            trigger.nick,
            'RIPE database not found. Use {prefix}ripe_update to download it.'
        )
        return

    obj = search_ip(ip_input)

    if not obj:
        bot.notice(trigger.nick, f'IP {ip_input} not found in RIPE database.')
        return

    bot.say(format_inetnum(obj))


@plugin.command('ripe_org')
@plugin.example('`ripe_org GOOGLE')
@plugin.example('`ripe_org RIPE-NCC')
def ripe_org(bot, trigger):
    """Query RIPE database for organisation information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `ripe_org <org_id or org_name>')
        bot.notice(trigger.nick, 'Example: `ripe_org GOOGLE')
        return

    org_input = trigger.group(2).strip()

    logger.info(f'RIPE org lookup: {org_input}')

    if not os.path.exists(SQLITE_DB):
        bot.notice(
            trigger.nick,
            'RIPE database not found. Use {prefix}ripe_update to download it.'
        )
        return

    results = search_org(org_input, limit=3)

    if not results:
        bot.notice(
            trigger.nick,
            f'Organisation "{org_input}" not found in RIPE database.'
        )
        return

    # Format as table
    headers = ['Org ID', 'Org Name', 'Country', 'Description']
    table_data = []
    for obj in results:
        org_id = obj.get('organisation', 'Unknown')
        org_name = obj.get('org-name', '') or '-'
        country = obj.get('country', '') or '-'
        descr = obj.get('descr', '') or '-'
        # Truncate description if too long
        if len(descr) > 40:
            descr = descr[:37] + '...'
        table_data.append([org_id, org_name, country, descr])

    table_output = formatter.table(table_data, headers=headers, max_width=400)
    bot.say(f'Found {len(results)} organisation(s):')
    for line in table_output.split('\n'):
        bot.say(line)


def setup(bot):
    """Module setup."""
    ensure_db_dir()
    init_sqlite_db()

    # Build SQLite database if RIPE file exists but SQLite doesn't
    if os.path.exists(DB_FILE) and not os.path.exists(SQLITE_DB):
        logger.info(
            'RIPE database file found but SQLite not built, building...'
        )
        build_sqlite_db()

    bot.memory['bgp_loaded'] = True
    logger.info('BGP/RIPE module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['bgp_loaded'] = False
    logger.info('BGP/RIPE module unloaded')
