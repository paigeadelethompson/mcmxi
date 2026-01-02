"""
Sopel module for PeeringDB queries.
Comprehensive PeeringDB API client covering all major endpoints.
"""
import os
import sys
from typing import Dict, List, Optional
from urllib.parse import urlencode

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_module_logger

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)  # 5MB max
formatter = IRCFormatter()

# PeeringDB API base URL
PEERINGDB_API = 'https://www.peeringdb.com/api'


def query_peeringdb(
    endpoint: str, params: Optional[Dict[str, str]] = None, depth: int = 1
) -> Optional[List[Dict]]:
    """Query PeeringDB API endpoint."""
    url = f'{PEERINGDB_API}/{endpoint}'
    if params:
        # Add depth parameter for nested data
        params_with_depth = params.copy()
        params_with_depth['depth'] = str(depth)
        query_string = urlencode(params_with_depth)
        url = f'{url}?{query_string}'
    else:
        url = f'{url}?depth={depth}'
    
    logger.info(f'Querying PeeringDB: {url}')
    response = http.get(url, timeout=30)
    
    if not response:
        logger.error(f'Failed to query PeeringDB: {endpoint}')
        return None
    
    # Response is JSON with 'data' key containing list
    if isinstance(response, dict) and 'data' in response:
        data = response['data']
        if isinstance(data, list):
            return data
        return [data] if data else []

    return None


@plugin.command('pdb_net')
@plugin.example('`pdb_net AS15169')
@plugin.example('`pdb_net Google')
def pdb_net(bot, trigger):
    """Query PeeringDB for network information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_net <ASN or network name>')
        bot.notice(trigger.nick, 'Example: `pdb_net AS15169')
        return
    
    query = trigger.group(2).strip()
    
    # Try ASN first
    if query.upper().startswith('AS'):
        asn = query.upper().replace('AS', '')
        params = {'asn': asn}
    elif query.isdigit():
        params = {'asn': query}
    else:
        # Search by name
        params = {'name__contains': query}
    
    data = query_peeringdb('net', params, depth=2)
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No network found for: {query}')
        return
    
    # Show first result
    net = data[0]
    asn = net.get('asn', 'N/A')
    name = net.get('name', 'N/A')
    website = net.get('website', '')
    info_type = net.get('info_type', 'N/A')
    org_id = net.get('org_id', '')
    
    bot.say(f"{formatter.bold(name)} (AS{asn}) - Type: {info_type}")
    if website:
        bot.say(f"Website: {website}")
    
    # Organization
    if org_id:
        org_data = query_peeringdb('org', {'id': str(org_id)}, depth=0)
        if org_data and len(org_data) > 0:
            org_name = org_data[0].get('name', '')
            if org_name:
                bot.say(f"Organization: {org_name}")
    
    # IRR AS-SET
    irr_as_set = net.get('irr_as_set', '')
    if irr_as_set:
        bot.say(f"IRR AS-SET: {irr_as_set}")
    
    # RPKI
    rpki_roa_asn = net.get('rpki_roa_asn', '')
    if rpki_roa_asn:
        bot.say(f"RPKI ROA ASN: {rpki_roa_asn}")
    
    # Stats
    fac_count = len(net.get('netfac_set', []))
    ix_count = len(net.get('netixlan_set', []))
    poc_count = len(net.get('poc_set', []))
    
    bot.say(f"Facilities: {fac_count}, IXs: {ix_count}, Contacts: {poc_count}")
    
    # Show facilities in table
    if fac_count > 0:
        netfac_set = net.get('netfac_set', [])[:10]
        if netfac_set:
            table_data = []
            for netfac in netfac_set:
                fac_id = netfac.get('fac_id')
                if fac_id:
                    fac_data = query_peeringdb('fac', {'id': str(fac_id)}, depth=0)
                    if fac_data and len(fac_data) > 0:
                        fac = fac_data[0]
                        fac_name = fac.get('name', f'Facility {fac_id}')
                        fac_city = fac.get('city', '')
                        fac_country = fac.get('country', '')
                        location = f"{fac_city}, {fac_country}" if fac_city else fac_country
                        table_data.append([fac_name, location])
            
            if table_data:
                bot.say(f"{formatter.bold('Facilities')} ({len(table_data)} shown):")
                table_output = formatter.table(table_data, headers=['Facility', 'Location'])
                for line in table_output.split('\n'):
                    bot.say(line)


@plugin.command('pdb_org')
@plugin.example('`pdb_org Google')
def pdb_org(bot, trigger):
    """Query PeeringDB for organization information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_org <organization name>')
        bot.notice(trigger.nick, 'Example: `pdb_org Google')
        return
    
    query = trigger.group(2).strip()
    params = {'name__contains': query}
    
    data = query_peeringdb('org', params, depth=1)
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No organization found for: {query}')
        return
    
    # Show first result
    org = data[0]
    name = org.get('name', 'N/A')
    website = org.get('website', '')
    
    bot.say(f"{formatter.bold(name)}")
    if website:
        bot.say(f"Website: {website}")
    
    # Show networks in table
    net_count = len(org.get('net_set', []))
    if net_count > 0:
        net_set = org.get('net_set', [])[:15]
        table_data = []
        for net in net_set:
            net_asn = net.get('asn', '')
            net_name = net.get('name', '')
            net_type = net.get('info_type', '')
            if net_asn:
                table_data.append([f"AS{net_asn}", net_name, net_type])
        
        if table_data:
            bot.say(f"{formatter.bold('Networks')} ({len(table_data)}/{net_count} shown):")
            table_output = formatter.table(table_data, headers=['ASN', 'Name', 'Type'])
            for line in table_output.split('\n'):
                bot.say(line)


@plugin.command('pdb_ix')
@plugin.example('`pdb_ix AMS-IX')
@plugin.example('`pdb_ix DE-CIX')
def pdb_ix(bot, trigger):
    """Query PeeringDB for Internet Exchange information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_ix <IX name>')
        bot.notice(trigger.nick, 'Example: `pdb_ix AMS-IX')
        return
    
    query = trigger.group(2).strip()
    params = {'name__contains': query}
    
    data = query_peeringdb('ix', params, depth=2)
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No IX found for: {query}')
        return
    
    # Show first result
    ix = data[0]
    name = ix.get('name', 'N/A')
    city = ix.get('city', 'N/A')
    country = ix.get('country', 'N/A')
    region = ix.get('region_continent', '')
    website = ix.get('website', '')
    tech_email = ix.get('tech_email', '')
    
    bot.say(f"{formatter.bold(name)} - {city}, {country}")
    if region:
        bot.say(f"Region: {region}")
    if website:
        bot.say(f"Website: {website}")
    if tech_email:
        bot.say(f"Tech: {tech_email}")
    
    # Stats
    net_count = ix.get('net_count', 0)
    fac_count = len(ix.get('ixfac_set', []))
    ixlan_count = len(ix.get('ixlan_set', []))
    
    bot.say(f"Networks: {net_count}, Facilities: {fac_count}, LANs: {ixlan_count}")
    
    # Show IX LANs in table
    ixlan_set = ix.get('ixlan_set', [])[:10]
    if ixlan_set:
        table_data = []
        for ixlan in ixlan_set:
            name = ixlan.get('name', f"LAN {ixlan.get('id', '')}")
            ipv4 = ixlan.get('ipaddr4', '')
            ipv6 = ixlan.get('ipaddr6', '')
            table_data.append([name, ipv4 or '-', ipv6 or '-'])
        
        if table_data:
            bot.say(f"{formatter.bold('IX LANs')} ({len(table_data)} shown):")
            table_output = formatter.table(table_data, headers=['LAN Name', 'IPv4', 'IPv6'])
            for line in table_output.split('\n'):
                bot.say(line)


@plugin.command('pdb_fac')
@plugin.example('`pdb_fac Equinix')
@plugin.example('`pdb_fac NY1')
def pdb_fac(bot, trigger):
    """Query PeeringDB for facility information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_fac <facility name>')
        bot.notice(trigger.nick, 'Example: `pdb_fac Equinix')
        return
    
    query = trigger.group(2).strip()
    params = {'name__contains': query}
    
    data = query_peeringdb('fac', params, depth=1)
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No facility found for: {query}')
        return
    
    # Show first result
    fac = data[0]
    name = fac.get('name', 'N/A')
    city = fac.get('city', 'N/A')
    country = fac.get('country', 'N/A')
    website = fac.get('website', '')
    
    bot.say(f"{formatter.bold(name)} - {city}, {country}")
    if website:
        bot.say(f"Website: {website}")
    
    # Stats
    net_count = fac.get('net_count', 0)
    ix_count = len(fac.get('ix_set', []))
    bot.say(f"Networks: {net_count}, Internet Exchanges: {ix_count}")


@plugin.command('pdb_ixlan')
@plugin.example('`pdb_ixlan 1')
def pdb_ixlan(bot, trigger):
    """Query PeeringDB for IX LAN information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_ixlan <IX LAN ID or name>')
        bot.notice(trigger.nick, 'Example: `pdb_ixlan 1')
        return
    
    query = trigger.group(2).strip()
    
    if query.isdigit():
        params = {'id': query}
    else:
        params = {'name__contains': query}
    
    data = query_peeringdb('ixlan', params, depth=2)
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No IX LAN found for: {query}')
        return
    
    # Show first result
    ixlan = data[0]
    name = ixlan.get('name', 'N/A')
    ipv4 = ixlan.get('ipaddr4', '')
    ipv6 = ixlan.get('ipaddr6', '')
    ix_id = ixlan.get('ix_id', '')
    
    bot.say(f"{formatter.bold(name)}")
    if ipv4:
        bot.say(f"IPv4: {ipv4}")
    if ipv6:
        bot.say(f"IPv6: {ipv6}")
    
    # Get IX info
    if ix_id:
        ix_data = query_peeringdb('ix', {'id': str(ix_id)}, depth=0)
        if ix_data and len(ix_data) > 0:
            ix_name = ix_data[0].get('name', '')
            if ix_name:
                bot.say(f"Internet Exchange: {ix_name}")
    
    # Show networks on this LAN
    net_count = len(ixlan.get('netixlan_set', []))
    bot.say(f"Networks: {net_count}")


@plugin.command('pdb_netixlan')
@plugin.example('`pdb_netixlan AS15169')
def pdb_netixlan(bot, trigger):
    """Query PeeringDB for network IX LAN connections."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_netixlan <ASN>')
        bot.notice(trigger.nick, 'Example: `pdb_netixlan AS15169')
        return
    
    query = trigger.group(2).strip().upper().replace('AS', '')
    if not query.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number')
        return
    
    # Get network first
    net_data = query_peeringdb('net', {'asn': query}, depth=0)
    if not net_data or len(net_data) == 0:
        bot.notice(trigger.nick, f'Network AS{query} not found')
        return
    
    net = net_data[0]
    net_id = net.get('id')
    net_name = net.get('name', 'N/A')
    
    # Get network IX LAN connections
    params = {'net_id': str(net_id)}
    data = query_peeringdb('netixlan', params, depth=2)
    
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No IX connections found for AS{query}')
        return
    
    bot.say(f"IX connections for {formatter.bold(net_name)} (AS{query}):")
    
    # Show connections in table
    table_data = []
    for netixlan in data[:20]:
        ixlan_id = netixlan.get('ixlan_id')
        ipaddr4 = netixlan.get('ipaddr4', '')
        ipaddr6 = netixlan.get('ipaddr6', '')
        speed = netixlan.get('speed', 0)
        
        if ixlan_id:
            ixlan_data = query_peeringdb('ixlan', {'id': str(ixlan_id)}, depth=1)
            if ixlan_data and len(ixlan_data) > 0:
                ixlan = ixlan_data[0]
                ixlan_name = ixlan.get('name', f'LAN {ixlan_id}')
                ix_id = ixlan.get('ix_id')
                
                if ix_id:
                    ix_data = query_peeringdb('ix', {'id': str(ix_id)}, depth=0)
                    if ix_data and len(ix_data) > 0:
                        ix_name = ix_data[0].get('name', '')
                        speed_str = f"{speed}Mbps" if speed else '-'
                        table_data.append([
                            ix_name,
                            ixlan_name,
                            ipaddr4 or '-',
                            ipaddr6 or '-',
                            speed_str
                        ])
    
    if table_data:
        table_output = formatter.table(
            table_data,
            headers=['IX', 'LAN', 'IPv4', 'IPv6', 'Speed']
        )
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_netfac')
@plugin.example('`pdb_netfac AS15169')
def pdb_netfac(bot, trigger):
    """Query PeeringDB for network facility connections."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_netfac <ASN>')
        bot.notice(trigger.nick, 'Example: `pdb_netfac AS15169')
        return
    
    query = trigger.group(2).strip().upper().replace('AS', '')
    if not query.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number')
        return
    
    # Get network first
    net_data = query_peeringdb('net', {'asn': query}, depth=0)
    if not net_data or len(net_data) == 0:
        bot.notice(trigger.nick, f'Network AS{query} not found')
        return
    
    net = net_data[0]
    net_id = net.get('id')
    net_name = net.get('name', 'N/A')
    
    # Get network facility connections
    params = {'net_id': str(net_id)}
    data = query_peeringdb('netfac', params, depth=1)
    
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No facility connections found for AS{query}')
        return
    
    bot.say(f"Facility connections for {formatter.bold(net_name)} (AS{query}):")
    
    # Show connections in table
    table_data = []
    for netfac in data[:20]:
        fac_id = netfac.get('fac_id')
        if fac_id:
            fac_data = query_peeringdb('fac', {'id': str(fac_id)}, depth=0)
            if fac_data and len(fac_data) > 0:
                fac = fac_data[0]
                fac_name = fac.get('name', '')
                fac_city = fac.get('city', '')
                fac_country = fac.get('country', '')
                location = f"{fac_city}, {fac_country}" if fac_city else fac_country
                table_data.append([fac_name, location])
    
    if table_data:
        table_output = formatter.table(table_data, headers=['Facility', 'Location'])
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_poc')
@plugin.example('`pdb_poc AS15169')
def pdb_poc(bot, trigger):
    """Query PeeringDB for points of contact."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_poc <ASN or network name>')
        bot.notice(trigger.nick, 'Example: `pdb_poc AS15169')
        return
    
    query = trigger.group(2).strip()
    
    # Get network first
    if query.upper().startswith('AS') or query.isdigit():
        asn = query.upper().replace('AS', '')
        net_data = query_peeringdb('net', {'asn': asn}, depth=1)
    else:
        net_data = query_peeringdb('net', {'name__contains': query}, depth=1)
    
    if not net_data or len(net_data) == 0:
        bot.notice(trigger.nick, f'Network not found: {query}')
        return
    
    net = net_data[0]
    net_name = net.get('name', 'N/A')
    poc_set = net.get('poc_set', [])
    
    if not poc_set:
        bot.notice(trigger.nick, f'No contacts found for {net_name}')
        return
    
    bot.say(f"Contacts for {formatter.bold(net_name)}:")
    
    # Show contacts in table
    table_data = []
    for poc in poc_set[:15]:
        name = poc.get('name', 'N/A')
        role = poc.get('role', '')
        email = poc.get('email', '')
        phone = poc.get('phone', '')
        table_data.append([name, role or '-', email or '-', phone or '-'])
    
    if table_data:
        table_output = formatter.table(
            table_data,
            headers=['Name', 'Role', 'Email', 'Phone']
        )
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_search')
@plugin.example('`pdb_search Google')
def pdb_search(bot, trigger):
    """Search PeeringDB across multiple object types."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_search <query>')
        bot.notice(trigger.nick, 'Example: `pdb_search Google')
        return
    
    query = trigger.group(2).strip()
    results = []
    
    # Search networks
    net_data = query_peeringdb('net', {'name__contains': query}, depth=0)
    if net_data:
        for net in net_data[:3]:
            results.append(('Network', f"AS{net.get('asn', '')}: {net.get('name', '')}"))
    
    # Search organizations
    org_data = query_peeringdb('org', {'name__contains': query}, depth=0)
    if org_data:
        for org in org_data[:3]:
            results.append(('Organization', org.get('name', '')))
    
    # Search facilities
    fac_data = query_peeringdb('fac', {'name__contains': query}, depth=0)
    if fac_data:
        for fac in fac_data[:3]:
            results.append(('Facility', fac.get('name', '')))
    
    # Search IXs
    ix_data = query_peeringdb('ix', {'name__contains': query}, depth=0)
    if ix_data:
        for ix in ix_data[:3]:
            results.append(('IX', ix.get('name', '')))
    
    if not results:
        bot.notice(trigger.nick, f'No results found for: {query}')
        return
    
    # Show results in table
    table_data = [[obj_type, name] for obj_type, name in results[:20]]
    bot.say(f"Search results for {formatter.bold(query)}:")
    table_output = formatter.table(table_data, headers=['Type', 'Name'])
    for line in table_output.split('\n'):
        bot.say(line)


@plugin.command('pdb_peers')
@plugin.example('`pdb_peers AS15169')
def pdb_peers(bot, trigger):
    """Show networks that peer with the given ASN at shared IX LANs."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_peers <ASN>')
        bot.notice(trigger.nick, 'Example: `pdb_peers AS15169')
        return

    query = trigger.group(2).strip().upper().replace('AS', '')
    if not query.isdigit():
        bot.notice(trigger.nick, 'ASN must be a number')
        return

    # Get network info
    net_data = query_peeringdb('net', {'asn': query}, depth=2)
    if not net_data or len(net_data) == 0:
        bot.notice(trigger.nick, f'Network AS{query} not found')
        return

    net = net_data[0]
    net_id = net.get('id')
    net_name = net.get('name', 'N/A')

    # Get all IX LANs this network is on
    netixlan_set = net.get('netixlan_set', [])
    if not netixlan_set:
        bot.notice(trigger.nick, f'AS{query} is not present at any IX LANs')
        return

    ixlan_ids = {netixlan.get('ixlan_id') for netixlan in netixlan_set}

    # Find all other networks on these IX LANs
    peer_networks = {}  # asn -> {name, shared_ixs: []}

    for ixlan_id in ixlan_ids:
        if not ixlan_id:
            continue

        # Get all networks on this IX LAN
        netixlan_data = query_peeringdb('netixlan', {'ixlan_id': str(ixlan_id)}, depth=1)
        if not netixlan_data:
            continue

        # Get IX info for display
        ixlan_data = query_peeringdb('ixlan', {'id': str(ixlan_id)}, depth=1)
        ix_name = ''
        if ixlan_data and len(ixlan_data) > 0:
            ix_id = ixlan_data[0].get('ix_id')
            if ix_id:
                ix_data = query_peeringdb('ix', {'id': str(ix_id)}, depth=0)
                if ix_data and len(ix_data) > 0:
                    ix_name = ix_data[0].get('name', '')

        for netixlan in netixlan_data:
            peer_net_id = netixlan.get('net_id')
            if not peer_net_id or peer_net_id == net_id:
                continue

            # Get peer network info
            peer_net_data = query_peeringdb('net', {'id': str(peer_net_id)}, depth=0)
            if not peer_net_data or len(peer_net_data) == 0:
                continue

            peer_net = peer_net_data[0]
            peer_asn = peer_net.get('asn')
            peer_name = peer_net.get('name', '')

            if not peer_asn:
                continue

            if peer_asn not in peer_networks:
                peer_networks[peer_asn] = {
                    'name': peer_name,
                    'shared_ixs': []
                }

            if ix_name:
                peer_networks[peer_asn]['shared_ixs'].append(ix_name)

    if not peer_networks:
        bot.notice(trigger.nick, f'No peers found for AS{query} at shared IX LANs')
        return

    bot.say(f"Peers for {formatter.bold(net_name)} (AS{query}):")

    # Sort by number of shared IXs (more shared = more likely strong peer)
    sorted_peers = sorted(
        peer_networks.items(),
        key=lambda x: len(x[1]['shared_ixs']),
        reverse=True
    )

    # Show in table
    table_data = []
    for peer_asn, peer_info in sorted_peers[:30]:
        shared_count = len(peer_info['shared_ixs'])
        shared_str = f"{shared_count} IX{'s' if shared_count > 1 else ''}"
        table_data.append([
            f"AS{peer_asn}",
            peer_info['name'][:30],
            shared_str
        ])

    if table_data:
        table_output = formatter.table(
            table_data,
            headers=['ASN', 'Network', 'Shared IXs']
        )
        for line in table_output.split('\n'):
            bot.say(line)

        if len(sorted_peers) > 30:
            bot.say(f"... and {len(sorted_peers) - 30} more peers")


@plugin.command('pdb_peers_detail')
@plugin.example('`pdb_peers_detail AS15169 AS6939')
def pdb_peers_detail(bot, trigger):
    """Show detailed peering information between two ASNs."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_peers_detail <ASN1> <ASN2>')
        bot.notice(trigger.nick, 'Example: `pdb_peers_detail AS15169 AS6939')
        return

    parts = trigger.group(2).strip().split()
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `pdb_peers_detail <ASN1> <ASN2>')
        return

    asn1 = parts[0].upper().replace('AS', '')
    asn2 = parts[1].upper().replace('AS', '')

    if not asn1.isdigit() or not asn2.isdigit():
        bot.notice(trigger.nick, 'Both ASNs must be numbers')
        return

    # Get both networks
    net1_data = query_peeringdb('net', {'asn': asn1}, depth=2)
    net2_data = query_peeringdb('net', {'asn': asn2}, depth=2)

    if not net1_data or len(net1_data) == 0:
        bot.notice(trigger.nick, f'Network AS{asn1} not found')
        return

    if not net2_data or len(net2_data) == 0:
        bot.notice(trigger.nick, f'Network AS{asn2} not found')
        return

    net1 = net1_data[0]
    net2 = net2_data[0]
    net1_name = net1.get('name', 'N/A')
    net2_name = net2.get('name', 'N/A')

    # Get IX LANs for both
    net1_ixlans = {netixlan.get('ixlan_id') for netixlan in net1.get('netixlan_set', [])}
    net2_ixlans = {netixlan.get('ixlan_id') for netixlan in net2.get('netixlan_set', [])}

    # Find shared IX LANs
    shared_ixlans = net1_ixlans & net2_ixlans

    if not shared_ixlans:
        bot.say(f"AS{asn1} ({net1_name}) and AS{asn2} ({net2_name}) do not share any IX LANs")
        return

    bot.say(f"Shared IX LANs between {formatter.bold(net1_name)} (AS{asn1}) and {formatter.bold(net2_name)} (AS{asn2}):")

    table_data = []
    for ixlan_id in list(shared_ixlans)[:20]:
        ixlan_data = query_peeringdb('ixlan', {'id': str(ixlan_id)}, depth=1)
        if not ixlan_data or len(ixlan_data) == 0:
            continue

        ixlan = ixlan_data[0]
        ixlan_name = ixlan.get('name', f'LAN {ixlan_id}')
        ix_id = ixlan.get('ix_id')

        ix_name = ''
        if ix_id:
            ix_data = query_peeringdb('ix', {'id': str(ix_id)}, depth=0)
            if ix_data and len(ix_data) > 0:
                ix_name = ix_data[0].get('name', '')

        # Get IP addresses for both networks on this LAN
        net1_netixlan = query_peeringdb('netixlan', {'net_id': str(net1.get('id')), 'ixlan_id': str(ixlan_id)}, depth=0)
        net2_netixlan = query_peeringdb('netixlan', {'net_id': str(net2.get('id')), 'ixlan_id': str(ixlan_id)}, depth=0)

        net1_ipv4 = ''
        net1_ipv6 = ''
        net2_ipv4 = ''
        net2_ipv6 = ''

        if net1_netixlan and len(net1_netixlan) > 0:
            net1_ipv4 = net1_netixlan[0].get('ipaddr4', '')
            net1_ipv6 = net1_netixlan[0].get('ipaddr6', '')

        if net2_netixlan and len(net2_netixlan) > 0:
            net2_ipv4 = net2_netixlan[0].get('ipaddr4', '')
            net2_ipv6 = net2_netixlan[0].get('ipaddr6', '')

        table_data.append([
            ix_name or ixlan_name,
            net1_ipv4 or '-',
            net2_ipv4 or '-',
            net1_ipv6 or '-',
            net2_ipv6 or '-'
        ])

    if table_data:
        table_output = formatter.table(
            table_data,
            headers=['IX/LAN', f'AS{asn1} IPv4', f'AS{asn2} IPv4', f'AS{asn1} IPv6', f'AS{asn2} IPv6']
        )
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_carrier')
@plugin.example('`pdb_carrier Level3')
def pdb_carrier(bot, trigger):
    """Query PeeringDB for carrier information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_carrier <carrier name or ID>')
        return

    query = trigger.group(2).strip()
    if query.isdigit():
        params = {'id': query}
    else:
        params = {'name__contains': query}

    data = query_peeringdb('carrier', params, depth=1)
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No carrier found for: {query}')
        return

    carrier = data[0]
    name = carrier.get('name', 'N/A')
    website = carrier.get('website', '')

    bot.say(f"{formatter.bold(name)}")
    if website:
        bot.say(f"Website: {website}")


@plugin.command('pdb_carrierfac')
@plugin.example('`pdb_carrierfac 1')
def pdb_carrierfac(bot, trigger):
    """Query PeeringDB for carrier facility connections."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_carrierfac <carrier ID>')
        return

    carrier_id = trigger.group(2).strip()
    params = {'carrier_id': carrier_id}
    data = query_peeringdb('carrierfac', params, depth=2)

    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No facilities found for carrier {carrier_id}')
        return

    bot.say(f"Facilities for carrier {carrier_id}:")
    table_data = []
    for carrierfac in data[:20]:
        fac_id = carrierfac.get('fac_id')
        if fac_id:
            fac_data = query_peeringdb('fac', {'id': str(fac_id)}, depth=0)
            if fac_data and len(fac_data) > 0:
                fac = fac_data[0]
                fac_name = fac.get('name', '')
                fac_city = fac.get('city', '')
                fac_country = fac.get('country', '')
                location = f"{fac_city}, {fac_country}" if fac_city else fac_country
                table_data.append([fac_name, location])

    if table_data:
        table_output = formatter.table(table_data, headers=['Facility', 'Location'])
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_ixfac')
@plugin.example('`pdb_ixfac 1')
def pdb_ixfac(bot, trigger):
    """Query PeeringDB for IX facility connections."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_ixfac <IX ID>')
        return

    ix_id = trigger.group(2).strip()
    params = {'ix_id': ix_id}
    data = query_peeringdb('ixfac', params, depth=2)

    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No facilities found for IX {ix_id}')
        return

    bot.say(f"Facilities for IX {ix_id}:")
    table_data = []
    for ixfac in data[:20]:
        fac_id = ixfac.get('fac_id')
        if fac_id:
            fac_data = query_peeringdb('fac', {'id': str(fac_id)}, depth=0)
            if fac_data and len(fac_data) > 0:
                fac = fac_data[0]
                fac_name = fac.get('name', '')
                fac_city = fac.get('city', '')
                fac_country = fac.get('country', '')
                location = f"{fac_city}, {fac_country}" if fac_city else fac_country
                table_data.append([fac_name, location])

    if table_data:
        table_output = formatter.table(table_data, headers=['Facility', 'Location'])
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_ixpfx')
@plugin.example('`pdb_ixpfx 1')
def pdb_ixpfx(bot, trigger):
    """Query PeeringDB for IX prefix information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_ixpfx <IX LAN ID>')
        return

    ixlan_id = trigger.group(2).strip()
    params = {'ixlan_id': ixlan_id}
    data = query_peeringdb('ixpfx', params, depth=1)

    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No prefixes found for IX LAN {ixlan_id}')
        return

    bot.say(f"Prefixes for IX LAN {ixlan_id}:")
    table_data = []
    for ixpfx in data[:20]:
        protocol = ixpfx.get('protocol', '')
        prefix = ixpfx.get('prefix', '')
        table_data.append([protocol, prefix])

    if table_data:
        table_output = formatter.table(table_data, headers=['Protocol', 'Prefix'])
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_campus')
@plugin.example('`pdb_campus 1')
def pdb_campus(bot, trigger):
    """Query PeeringDB for campus information."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `pdb_campus <campus name or ID>')
        return

    query = trigger.group(2).strip()
    if query.isdigit():
        params = {'id': query}
    else:
        params = {'name__contains': query}

    data = query_peeringdb('campus', params, depth=2)
    if not data or len(data) == 0:
        bot.notice(trigger.nick, f'No campus found for: {query}')
        return

    campus = data[0]
    name = campus.get('name', 'N/A')
    city = campus.get('city', 'N/A')
    country = campus.get('country', 'N/A')

    bot.say(f"{formatter.bold(name)} - {city}, {country}")

    # Show facilities
    fac_set = campus.get('fac_set', [])
    if fac_set:
        bot.say(f"Facilities: {len(fac_set)}")
        table_data = []
        for fac in fac_set[:10]:
            fac_name = fac.get('name', '')
            fac_city = fac.get('city', '')
            fac_country = fac.get('country', '')
            location = f"{fac_city}, {fac_country}" if fac_city else fac_country
            table_data.append([fac_name, location])

        if table_data:
            table_output = formatter.table(table_data, headers=['Facility', 'Location'])
            for line in table_output.split('\n'):
                bot.say(line)


@plugin.command('pdb_asset')
@plugin.example('`pdb_asset')
def pdb_asset(bot, trigger):
    """List PeeringDB assets."""
    data = query_peeringdb('asset', None, depth=0)

    if not data or len(data) == 0:
        bot.notice(trigger.nick, 'No assets found')
        return

    bot.say(f"PeeringDB Assets ({len(data)} total):")
    table_data = []
    for asset in data[:20]:
        asset_id = asset.get('id', '')
        asset_type = asset.get('type', '')
        table_data.append([str(asset_id), asset_type])

    if table_data:
        table_output = formatter.table(table_data, headers=['ID', 'Type'])
        for line in table_output.split('\n'):
            bot.say(line)


@plugin.command('pdb_as_set')
@plugin.example('`pdb_as_set')
@plugin.example('`pdb_as_set AS15169')
def pdb_as_set(bot, trigger):
    """Query PeeringDB for AS-SET information."""
    query = trigger.group(2) if trigger.group(2) else None

    if query:
        # Get AS-SET by ASN
        asn = query.strip().upper().replace('AS', '')
        if not asn.isdigit():
            bot.notice(trigger.nick, 'ASN must be a number')
            return

        # Get network info
        net_data = query_peeringdb('net', {'asn': asn}, depth=0)
        if not net_data or len(net_data) == 0:
            bot.notice(trigger.nick, f'Network AS{asn} not found')
            return

        net = net_data[0]
        irr_as_set = net.get('irr_as_set', '')
        if irr_as_set:
            bot.say(f"AS{asn} ({net.get('name', 'N/A')}): {formatter.bold(irr_as_set)}")
        else:
            bot.say(f"AS{asn} has no AS-SET configured")
    else:
        # List all AS-SETs (this might be large, so limit)
        bot.notice(trigger.nick, 'Usage: `pdb_as_set <ASN> to get AS-SET for a network')


@plugin.command('pdb_user')
@plugin.example('`pdb_user')
@plugin.example('`pdb_user 1')
def pdb_user(bot, trigger):
    """Query PeeringDB for user information."""
    query = trigger.group(2) if trigger.group(2) else None

    if query:
        # Get specific user
        if query.isdigit():
            params = {'id': query}
        else:
            params = {'email__contains': query}
        data = query_peeringdb('user', params, depth=0)
    else:
        # List users (limited)
        data = query_peeringdb('user', None, depth=0)

    if not data or len(data) == 0:
        bot.notice(trigger.nick, 'No users found')
        return

    if query:
        # Show single user details
        user = data[0]
        name = user.get('name', 'N/A')
        email = user.get('email', '')
        bot.say(f"{formatter.bold(name)}")
        if email:
            bot.say(f"Email: {email}")
    else:
        # List users
        bot.say(f"PeeringDB Users ({len(data)} shown, limited):")
        table_data = []
        for user in data[:20]:
            name = user.get('name', 'N/A')
            email = user.get('email', '')
            table_data.append([name, email or '-'])

        if table_data:
            table_output = formatter.table(table_data, headers=['Name', 'Email'])
            for line in table_output.split('\n'):
                bot.say(line)
