"""
Sopel group-based permission checking utilities.
"""
import fnmatch
import threading
from typing import Dict, List, Optional, Set


def _build_user_mask(bot, nick: str) -> Optional[str]:
    """Build a user mask in format nick!user@host."""
    try:
        user = bot.users.get(nick)
        if not user:
            return None

        user_nick = nick
        user_user = getattr(user, 'user', '*')
        user_host = getattr(user, 'host', '*')

        # If we don't have user or host, return None
        if user_user == '*' and user_host == '*':
            return None

        return f"{user_nick}!{user_user}@{user_host}".lower()
    except Exception:
        return None


def is_user_ignored(bot, trigger) -> bool:
    """Check if a user is ignored by the bot (supports masks)."""
    if 'ignored_users' not in bot.memory:
        return False

    ignored = bot.memory['ignored_users']
    nick_lower = trigger.nick.lower()

    # Build user mask if available
    user_mask = _build_user_mask(bot, trigger.nick)

    # Check each ignored pattern
    for pattern in ignored:
        pattern_lower = pattern.lower()

        # Exact match for nick
        if pattern_lower == nick_lower:
            return True

        # Check by account if available
        try:
            user = bot.users.get(trigger.nick)
            if user and user.account:
                account_lower = user.account.lower()
                if pattern_lower == account_lower:
                    return True
        except Exception:
            pass

        # Check mask pattern (nick!user@host format)
        if '!' in pattern or '@' in pattern:
            if user_mask:
                # Use fnmatch for wildcard matching
                if fnmatch.fnmatch(user_mask, pattern_lower):
                    return True
                # Also check if pattern matches just the host
                if '@' in pattern_lower:
                    host_part = pattern_lower.split('@', 1)[1]
                    if user_mask and '@' in user_mask:
                        user_host = user_mask.split('@', 1)[1]
                        if fnmatch.fnmatch(user_host, host_part):
                            return True

    return False


class Permissions:
    """Group-based permission system for Sopel."""

    # In-memory storage for groups and permissions
    # Format: {
    #   'groups': {
    #     'ADMIN': {'commands': ['*'], 'users': ['admin1', 'admin2']},
    #     'MODERATOR': {'commands': ['kick', 'ban'], 'users': ['mod1']}
    #   }
    # }
    _storage: Dict = {}
    _lock = threading.Lock()

    @staticmethod
    def _init_storage(bot):
        """Initialize storage in bot.memory if not exists."""
        if 'permissions' not in bot.memory:
            with Permissions._lock:
                bot.memory['permissions'] = {
                    'groups': {},
                    'user_groups': {}  # Map account -> set of groups
                }
        Permissions._storage = bot.memory['permissions']

    @staticmethod
    def _init_admin_group(bot):
        """Initialize ADMIN group with config admins."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            groups = Permissions._storage['groups']

            # Create ADMIN group if it doesn't exist
            if 'ADMIN' not in groups:
                groups['ADMIN'] = {
                    'commands': ['*'],  # * means all commands
                    'users': []
                }

            # Create DEFAULT group if it doesn't exist
            # This group applies to users not in any other group
            # Allow all commands by default
            if 'DEFAULT' not in groups:
                groups['DEFAULT'] = {
                    'commands': ['*'],  # Allow all commands by default
                    'users': []  # This group doesn't have explicit users
                }

            # Add config admins to ADMIN group
            if hasattr(bot.config.core, 'admins') and bot.config.core.admins:
                admin_list = bot.config.core.admins
                if isinstance(admin_list, str):
                    admin_list = [admin_list]

                for admin in admin_list:
                    admin_lower = admin.lower()
                    if admin_lower not in groups['ADMIN']['users']:
                        groups['ADMIN']['users'].append(admin_lower)

                # Update user_groups mapping
                user_groups = Permissions._storage['user_groups']
                for admin in admin_list:
                    admin_lower = admin.lower()
                    if admin_lower not in user_groups:
                        user_groups[admin_lower] = set()
                    user_groups[admin_lower].add('ADMIN')

    @staticmethod
    def _get_user_account(bot, nick: str) -> Optional[str]:
        """Get the account name for a user (if registered with services)."""
        try:
            user = bot.users.get(nick)
            if user and user.account:
                return user.account.lower()
        except Exception:
            pass
        return None

    @staticmethod
    def _is_registered(bot, nick: str) -> bool:
        """Check if user is registered with services."""
        account = Permissions._get_user_account(bot, nick)
        return account is not None

    @staticmethod
    def has_command_permission(
        bot, trigger, command: str
    ) -> bool:
        """
        Check if user has permission to use a command.
        Returns True if:
        - User is in ADMIN group (has * permission)
        - User is in a group that has this command
        - Command is public (no permission check needed)
        """
        if not trigger.sender:
            return False

        # Check if user is ignored
        if is_user_ignored(bot, trigger):
            return False

        Permissions._init_storage(bot)
        Permissions._init_admin_group(bot)

        nick = trigger.nick.lower()
        account = Permissions._get_user_account(bot, trigger.nick)

        # Allow everyone - don't require account registration
        # If not registered, still allow (permissive mode)
        if not account:
            return True

        with Permissions._lock:
            user_groups = Permissions._storage['user_groups']
            groups = Permissions._storage['groups']

            # Get all groups this user belongs to
            user_group_set = user_groups.get(account, set())

            # Also check by nick (for backwards compatibility)
            if nick in user_groups:
                user_group_set.update(user_groups[nick])

            # If user is not in any group, check DEFAULT group
            if not user_group_set:
                user_group_set = {'DEFAULT'}

            # Check each group
            for group_name in user_group_set:
                if group_name not in groups:
                    continue

                group = groups[group_name]
                commands = group.get('commands', [])

                # Check if group has * (all commands) or specific command
                cmd_lower = command.lower()
                cmd_list = [c.lower() for c in commands]
                if '*' in commands or cmd_lower in cmd_list:
                    return True

        return False

    @staticmethod
    def is_admin(bot, trigger) -> bool:
        """Check if user is an admin (in ADMIN group)."""
        return Permissions.has_command_permission(bot, trigger, '*')

    @staticmethod
    def get_user_groups(bot, account: str) -> Set[str]:
        """Get all groups a user belongs to."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            user_groups = Permissions._storage['user_groups']
            return user_groups.get(account.lower(), set()).copy()

    @staticmethod
    def get_group_commands(bot, group_name: str) -> List[str]:
        """Get all commands for a group."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            groups = Permissions._storage['groups']
            if group_name.upper() in groups:
                return groups[group_name.upper()].get('commands', []).copy()
        return []

    @staticmethod
    def get_all_groups(bot) -> Dict[str, Dict]:
        """Get all groups."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            return Permissions._storage['groups'].copy()

    @staticmethod
    def create_group(bot, group_name: str, commands: List[str]) -> bool:
        """Create a new group with specified commands."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            groups = Permissions._storage['groups']
            group_name_upper = group_name.upper()

            if group_name_upper in groups:
                return False  # Group already exists

            groups[group_name_upper] = {
                'commands': [c.lower() for c in commands],
                'users': []
            }
            return True

    @staticmethod
    def add_user_to_group(bot, account: str, group_name: str) -> bool:
        """Add a user to a group."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            groups = Permissions._storage['groups']
            user_groups = Permissions._storage['user_groups']
            group_name_upper = group_name.upper()

            if group_name_upper not in groups:
                return False  # Group doesn't exist

            account_lower = account.lower()

            # Add to group's user list
            if account_lower not in groups[group_name_upper]['users']:
                groups[group_name_upper]['users'].append(account_lower)

            # Add to user_groups mapping
            if account_lower not in user_groups:
                user_groups[account_lower] = set()
            user_groups[account_lower].add(group_name_upper)

            return True

    @staticmethod
    def remove_user_from_group(bot, account: str, group_name: str) -> bool:
        """Remove a user from a group."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            groups = Permissions._storage['groups']
            user_groups = Permissions._storage['user_groups']
            group_name_upper = group_name.upper()

            if group_name_upper not in groups:
                return False

            account_lower = account.lower()

            # Remove from group's user list
            if account_lower in groups[group_name_upper]['users']:
                groups[group_name_upper]['users'].remove(account_lower)

            # Remove from user_groups mapping
            if account_lower in user_groups:
                user_groups[account_lower].discard(group_name_upper)
                if not user_groups[account_lower]:
                    del user_groups[account_lower]

            return True

    @staticmethod
    def add_command_to_group(bot, group_name: str, command: str) -> bool:
        """Add a command to a group."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            groups = Permissions._storage['groups']
            group_name_upper = group_name.upper()

            if group_name_upper not in groups:
                return False

            command_lower = command.lower()
            if command_lower not in groups[group_name_upper]['commands']:
                groups[group_name_upper]['commands'].append(command_lower)

            return True

    @staticmethod
    def remove_command_from_group(bot, group_name: str, command: str) -> bool:
        """Remove a command from a group."""
        Permissions._init_storage(bot)

        with Permissions._lock:
            groups = Permissions._storage['groups']
            group_name_upper = group_name.upper()

            if group_name_upper not in groups:
                return False

            command_lower = command.lower()
            if command_lower in groups[group_name_upper]['commands']:
                groups[group_name_upper]['commands'].remove(command_lower)

            return True

    @staticmethod
    def delete_group(bot, group_name: str) -> bool:
        """Delete a group (cannot delete ADMIN or DEFAULT groups)."""
        Permissions._init_storage(bot)

        group_name_upper = group_name.upper()
        if group_name_upper == 'ADMIN' or group_name_upper == 'DEFAULT':
            return False  # Cannot delete ADMIN or DEFAULT groups

        with Permissions._lock:
            groups = Permissions._storage['groups']
            user_groups = Permissions._storage['user_groups']
            group_name_upper = group_name.upper()

            if group_name_upper not in groups:
                return False

            # Remove all users from this group
            users_in_group = groups[group_name_upper]['users'].copy()
            for user in users_in_group:
                if user in user_groups:
                    user_groups[user].discard(group_name_upper)
                    if not user_groups[user]:
                        del user_groups[user]

            # Delete the group
            del groups[group_name_upper]
            return True
