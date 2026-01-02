"""
Sopel module for managing group-based permissions.
Allows admins to create groups, assign commands, and add users.
"""
from permissions import Permissions
from common import IRCFormatter, get_module_logger
import os
import sys
from typing import List, Optional

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = get_module_logger(__name__)
formatter = IRCFormatter()


def _get_user_account(bot, nick: str) -> Optional[str]:
    """Get the account name for a user (if registered with services)."""
    try:
        user = bot.users.get(nick)
        if user and user.account:
            return user.account.lower()
    except Exception:
        pass
    return None


def _is_registered(bot, nick: str) -> bool:
    """Check if user is registered with services."""
    account = _get_user_account(bot, nick)
    return account is not None


@plugin.command('perm_groups')
@plugin.example('`perm_groups')
def perm_groups(bot, trigger):
    """List all permission groups."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    groups = Permissions.get_all_groups(bot)

    if not groups:
        bot.say('No groups defined.')
        return

    bot.say(f"{formatter.bold('Permission Groups')} ({len(groups)} total):")

    for group_name, group_data in sorted(groups.items()):
        commands = group_data.get('commands', [])
        users = group_data.get('users', [])
        commands_str = ', '.join(commands[:5])
        if len(commands) > 5:
            commands_str += f' ... ({len(commands)} total)'
        bot.say(
            f"{formatter.bold(group_name)}: "
            f"{len(users)} user(s), "
            f"commands: {commands_str}"
        )


@plugin.command('perm_group')
@plugin.example('`perm_group MODERATOR')
def perm_group(bot, trigger):
    """Show details of a specific group."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_group <group_name>')
        return

    group_name = trigger.group(2).strip().upper()
    groups = Permissions.get_all_groups(bot)

    if group_name not in groups:
        bot.notice(trigger.nick, f'Group {group_name} not found.')
        return

    group_data = groups[group_name]
    commands = group_data.get('commands', [])
    users = group_data.get('users', [])

    bot.say(f"{formatter.bold('Group')}: {group_name}")
    if group_name == 'DEFAULT':
        bot.say(
            f"{formatter.bold('Note')}: "
            "DEFAULT group applies to all users not in any other group"
        )
    bot.say(f"{formatter.bold('Commands')} ({len(commands)}): {', '.join(commands) if commands else 'None'}")
    if group_name == 'DEFAULT':
        bot.say(f"{formatter.bold('Users')}: Applies to all non-grouped users")
    else:
        bot.say(f"{formatter.bold('Users')} ({len(users)}): {', '.join(users) if users else 'None'}")


@plugin.command('perm_create')
@plugin.example('`perm_create MODERATOR kick ban')
def perm_create(bot, trigger):
    """Create a new permission group with commands."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_create <group_name> <command1> [command2] ...')
        bot.notice(trigger.nick, 'Example: `perm_create MODERATOR kick ban')
        return

    parts = trigger.group(2).strip().split()
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `perm_create <group_name> <command1> [command2] ...')
        return

    group_name = parts[0].upper()
    commands = [c.lower() for c in parts[1:]]

    if group_name == 'ADMIN':
        bot.notice(trigger.nick, 'Cannot create ADMIN group (already exists).')
        return

    if Permissions.create_group(bot, group_name, commands):
        bot.say(
            f"Created group {formatter.bold(group_name)} "
            f"with commands: {', '.join(commands)}"
        )
    else:
        bot.notice(trigger.nick, f'Group {group_name} already exists.')


@plugin.command('perm_adduser')
@plugin.example('`perm_adduser username MODERATOR')
def perm_adduser(bot, trigger):
    """Add a registered user to a group."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_adduser <account> <group_name>')
        bot.notice(trigger.nick, 'Example: `perm_adduser username MODERATOR')
        return

    parts = trigger.group(2).strip().split()
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `perm_adduser <account> <group_name>')
        return

    account = parts[0].lower()
    group_name = parts[1].upper()

    # Verify group exists
    groups = Permissions.get_all_groups(bot)
    if group_name not in groups:
        bot.notice(trigger.nick, f'Group {group_name} not found.')
        return

    if Permissions.add_user_to_group(bot, account, group_name):
        bot.say(f"Added {formatter.monospace(account)} to group {formatter.bold(group_name)}")
    else:
        bot.notice(trigger.nick, f'Failed to add user to group {group_name}.')


@plugin.command('perm_removeuser')
@plugin.example('`perm_removeuser username MODERATOR')
def perm_removeuser(bot, trigger):
    """Remove a user from a group."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_removeuser <account> <group_name>')
        return

    parts = trigger.group(2).strip().split()
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `perm_removeuser <account> <group_name>')
        return

    account = parts[0].lower()
    group_name = parts[1].upper()

    if group_name == 'ADMIN' or group_name == 'DEFAULT':
        bot.notice(
            trigger.nick,
            'Cannot remove users from ADMIN or DEFAULT groups via command.'
        )
        return

    if Permissions.remove_user_from_group(bot, account, group_name):
        bot.say(
            f"Removed {formatter.monospace(account)} "
            f"from group {formatter.bold(group_name)}"
        )
    else:
        bot.notice(trigger.nick, f'User not in group {group_name}.')


@plugin.command('perm_addcmd')
@plugin.example('`perm_addcmd MODERATOR kick')
def perm_addcmd(bot, trigger):
    """Add a command to a group."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_addcmd <group_name> <command>')
        return

    parts = trigger.group(2).strip().split()
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `perm_addcmd <group_name> <command>')
        return

    group_name = parts[0].upper()
    command = parts[1].lower()

    if Permissions.add_command_to_group(bot, group_name, command):
        bot.say(
            f"Added command {formatter.monospace(command)} "
            f"to group {formatter.bold(group_name)}"
        )
    else:
        bot.notice(trigger.nick, f'Group {group_name} not found.')


@plugin.command('perm_removecmd')
@plugin.example('`perm_removecmd MODERATOR kick')
def perm_removecmd(bot, trigger):
    """Remove a command from a group."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_removecmd <group_name> <command>')
        return

    parts = trigger.group(2).strip().split()
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `perm_removecmd <group_name> <command>')
        return

    group_name = parts[0].upper()
    command = parts[1].lower()

    if group_name == 'ADMIN' and command == '*':
        bot.notice(trigger.nick, 'Cannot remove * from ADMIN group.')
        return

    if Permissions.remove_command_from_group(bot, group_name, command):
        bot.say(
            f"Removed command {formatter.monospace(command)} "
            f"from group {formatter.bold(group_name)}"
        )
    else:
        bot.notice(trigger.nick, f'Group {group_name} not found or command not in group.')


@plugin.command('perm_delete')
@plugin.example('`perm_delete MODERATOR')
def perm_delete(bot, trigger):
    """Delete a permission group (cannot delete ADMIN)."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_delete <group_name>')
        return

    group_name = trigger.group(2).strip().upper()

    if group_name == 'ADMIN' or group_name == 'DEFAULT':
        bot.notice(trigger.nick, 'Cannot delete ADMIN or DEFAULT groups.')
        return

    if Permissions.delete_group(bot, group_name):
        bot.say(f"Deleted group {formatter.bold(group_name)}")
    else:
        bot.notice(trigger.nick, f'Group {group_name} not found.')


@plugin.command('perm_user')
@plugin.example('`perm_user username')
def perm_user(bot, trigger):
    """Show groups a user belongs to."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_user <account>')
        return

    account = trigger.group(2).strip().lower()
    groups = Permissions.get_user_groups(bot, account)

    if not groups:
        bot.say(f"User {formatter.monospace(account)} is not in any groups.")
    else:
        bot.say(
            f"User {formatter.monospace(account)} is in groups: "
            f"{', '.join(sorted(groups))}"
        )


@plugin.command('perm_check')
@plugin.example('`perm_check username kick')
def perm_check(bot, trigger):
    """Check if a user has permission for a command."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `perm_check <account> <command>')
        return

    parts = trigger.group(2).strip().split()
    if len(parts) < 2:
        bot.notice(trigger.nick, 'Usage: `perm_check <account> <command>')
        return

    account = parts[0].lower()
    command = parts[1].lower()

    # Create a mock trigger for permission check
    class MockTrigger:
        def __init__(self, account_name):
            self.nick = account_name
            self.sender = trigger.sender

    mock_trigger = MockTrigger(account)

    # Temporarily set the account in bot.users
    # This is a workaround since we're checking by account
    has_perm = False
    user_groups = Permissions.get_user_groups(bot, account)

    for group_name in user_groups:
        commands = Permissions.get_group_commands(bot, group_name)
        if '*' in commands or command in [c.lower() for c in commands]:
            has_perm = True
            break

    if has_perm:
        bot.say(
            f"User {formatter.monospace(account)} "
            f"{formatter.bold('has')} permission for command "
            f"{formatter.monospace(command)}"
        )
    else:
        bot.say(
            f"User {formatter.monospace(account)} "
            f"{formatter.bold('does not have')} permission for command "
            f"{formatter.monospace(command)}"
        )


def _init_ignored_users(bot):
    """Initialize ignored users storage."""
    if 'ignored_users' not in bot.memory:
        bot.memory['ignored_users'] = set()


def _is_ignored(bot, nick: str, account: Optional[str] = None) -> bool:
    """Check if a user is ignored."""
    _init_ignored_users(bot)
    ignored = bot.memory['ignored_users']
    nick_lower = nick.lower()
    if account:
        account_lower = account.lower()
        return nick_lower in ignored or account_lower in ignored
    return nick_lower in ignored


@plugin.command('ignore')
@plugin.example('`ignore username')
@plugin.example('`ignore *!*@*.spam.com')
@plugin.example('`ignore spammer!*@*')
def ignore_user(bot, trigger):
    """Ignore a user completely (supports masks like *!*@host)."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `ignore <nick|account|mask>')
        bot.notice(trigger.nick, 'Examples: .ignore username')
        bot.notice(trigger.nick, '          .ignore *!*@*.spam.com')
        bot.notice(trigger.nick, '          .ignore spammer!*@*')
        return

    target = trigger.group(2).strip()
    _init_ignored_users(bot)

    # Store as-is (case-insensitive matching happens in is_user_ignored)
    if target.lower() in [p.lower() for p in bot.memory['ignored_users']]:
        bot.notice(trigger.nick, f'{target} is already ignored.')
        return

    bot.memory['ignored_users'].add(target)
    bot.say(f"Ignoring {formatter.monospace(target)}")


@plugin.command('unignore')
@plugin.example('`unignore username')
@plugin.example('`unignore *!*@*.spam.com')
def unignore_user(bot, trigger):
    """Stop ignoring a user or mask."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `unignore <nick|account|mask>')
        return

    target = trigger.group(2).strip()
    _init_ignored_users(bot)

    # Find exact match (case-insensitive)
    ignored_list = list(bot.memory['ignored_users'])
    target_lower = target.lower()
    found = None
    for pattern in ignored_list:
        if pattern.lower() == target_lower:
            found = pattern
            break

    if not found:
        bot.notice(trigger.nick, f'{target} is not ignored.')
        return

    bot.memory['ignored_users'].discard(found)
    bot.say(f"Stopped ignoring {formatter.monospace(found)}")


@plugin.command('ignored')
@plugin.example('`ignored')
def list_ignored(bot, trigger):
    """List all ignored users."""
    if not Permissions.is_admin(bot, trigger):
        bot.notice(trigger.nick, 'Permission denied. Admin access required.')
        return

    _init_ignored_users(bot)
    ignored = bot.memory['ignored_users']

    if not ignored:
        bot.say('No users are currently ignored.')
        return

    ignored_list = sorted(ignored)
    bot.say(f"{formatter.bold('Ignored Users')} ({len(ignored_list)}):")
    bot.say(', '.join(ignored_list))
