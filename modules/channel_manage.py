"""
Sopel module for channel management commands.
Supports ChanServ (Anope/Atheme) for registered channels.
"""
from common import IRCFormatter, get_module_logger, Permissions
import os
import sys
import time
from datetime import datetime

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = get_module_logger(__name__)
formatter = IRCFormatter()

# Cache for channel registration status
_channel_registered_cache = {}
_cache_timeout = 300  # 5 minutes


def _is_channel_registered(bot, channel: str) -> bool:
    """Check if channel is registered with services (cached)."""
    channel_lower = channel.lower()

    # Check cache
    if channel_lower in _channel_registered_cache:
        cached_time, is_registered = _channel_registered_cache[channel_lower]
        if time.time() - cached_time < _cache_timeout:
            return is_registered

    # Try to determine if channel is registered
    # We'll assume it's registered if we can't determine otherwise
    # (services will handle the command appropriately)
    is_registered = True  # Default assumption

    # Cache the result
    _channel_registered_cache[channel_lower] = (time.time(), is_registered)
    return is_registered


def _get_chanserv_name(bot) -> str:
    """Get ChanServ name (defaults to ChanServ)."""
    # Could check bot.config for services name
    return 'ChanServ'


def _send_chanserv_command(bot, command: str):
    """Send a command to ChanServ via PRIVMSG."""
    chanserv = _get_chanserv_name(bot)
    # Send PRIVMSG to ChanServ with the command
    # Format: PRIVMSG ChanServ :COMMAND args
    bot.write(['PRIVMSG', chanserv], command)


def _has_command_permission(bot, trigger, command: str) -> bool:
    """Check if user has permission to use a command via group system."""
    return Permissions.has_command_permission(bot, trigger, command)


@plugin.command('kick')
@plugin.example('`kick #channel username')
@plugin.example('`kick username reason')
def channel_kick(bot, trigger):
    """Kick a user from channel (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `kick <#channel> <nick> [reason]')
        bot.notice(
            trigger.nick,
            '       `kick <nick> [reason] (current channel)'
        )
        return

    parts = trigger.group(2).strip().split(None, 1)
    channel = None
    target = None
    reason = ''

    # Parse arguments
    if len(parts) >= 1:
        if parts[0].startswith('#'):
            # Channel specified
            channel = parts[0]
            if len(parts) >= 2:
                reason_parts = parts[1].split(None, 1)
                target = reason_parts[0]
                if len(reason_parts) > 1:
                    reason = reason_parts[1]
        else:
            # No channel, use current
            channel = trigger.sender
            target = parts[0]
            if len(parts) > 1:
                reason = parts[1]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `kick <#channel> <nick> [reason]')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'kick'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered, otherwise use IRC command
    if _is_channel_registered(bot, channel):
        if reason:
            cmd = f"KICK {channel} {target} :{reason}"
        else:
            cmd = f"KICK {channel} {target}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Kicked {formatter.monospace(target)} from {channel}")
    else:
        # Direct IRC kick
        if reason:
            bot.write(['KICK', channel, target], reason)
        else:
            bot.write(['KICK', channel, target])
        bot.say(f"Kicked {formatter.monospace(target)} from {channel}")


@plugin.command('ban')
@plugin.example('`ban #channel username')
@plugin.example('`ban username')
def channel_ban(bot, trigger):
    """Ban a user from channel (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `ban <#channel> <nick_or_mask>')
        bot.notice(
            trigger.nick,
            '       `ban <nick_or_mask> (current channel)'
        )
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `ban <#channel> <nick_or_mask>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'kick'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Build ban mask if needed
    ban_mask = target
    if '!' not in target and '@' not in target:
        # Try to get user's hostmask
        try:
            user = bot.users.get(target)
            if user:
                user_user = getattr(user, 'user', '*')
                user_host = getattr(user, 'host', '*')
                ban_mask = f"{target}!{user_user}@{user_host}"
        except Exception:
            ban_mask = f"{target}!*@*"

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"BAN {channel} {ban_mask}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Banned {formatter.monospace(ban_mask)} from {channel}")
    else:
        # Direct IRC ban
        bot.write(['MODE', channel, '+b', ban_mask])
        bot.say(f"Banned {formatter.monospace(ban_mask)} from {channel}")


@plugin.command('unban')
@plugin.example('`unban #channel username')
@plugin.example('`unban username')
def channel_unban(bot, trigger):
    """Unban a user from channel (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `unban <#channel> <nick_or_mask>')
        bot.notice(
            trigger.nick,
            '       `unban <nick_or_mask> (current channel)'
        )
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `unban <#channel> <nick_or_mask>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'unban'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"UNBAN {channel} {target}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Unbanned {formatter.monospace(target)} from {channel}")
    else:
        # Direct IRC unban (need to get ban mask from channel)
        # For simplicity, try the target as-is
        bot.write(['MODE', channel, '-b', target])
        bot.say(f"Unbanned {formatter.monospace(target)} from {channel}")


@plugin.command('op')
@plugin.example('`op #channel username')
@plugin.example('`op username')
def channel_op(bot, trigger):
    """Give op to a user (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `op <#channel> <nick>')
        bot.notice(trigger.nick, '       `op <nick> (current channel)')
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `op <#channel> <nick>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'op'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"OP {channel} {target}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Opped {formatter.monospace(target)} in {channel}")
    else:
        # Direct IRC op
        bot.write(['MODE', channel, '+o', target])
        bot.say(f"Opped {formatter.monospace(target)} in {channel}")


@plugin.command('deop')
@plugin.example('`deop #channel username')
@plugin.example('`deop username')
def channel_deop(bot, trigger):
    """Remove op from a user (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `deop <#channel> <nick>')
        bot.notice(trigger.nick, '       `deop <nick> (current channel)')
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `deop <#channel> <nick>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'deop'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"DEOP {channel} {target}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Deopped {formatter.monospace(target)} in {channel}")
    else:
        # Direct IRC deop
        bot.write(['MODE', channel, '-o', target])
        bot.say(f"Deopped {formatter.monospace(target)} in {channel}")


@plugin.command('voice')
@plugin.example('`voice #channel username')
@plugin.example('`voice username')
def channel_voice(bot, trigger):
    """Give voice to a user (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `voice <#channel> <nick>')
        bot.notice(trigger.nick, '       `voice <nick> (current channel)')
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `voice <#channel> <nick>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'voice'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"VOICE {channel} {target}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Voiced {formatter.monospace(target)} in {channel}")
    else:
        # Direct IRC voice
        bot.write(['MODE', channel, '+v', target])
        bot.say(f"Voiced {formatter.monospace(target)} in {channel}")


@plugin.command('devoice')
@plugin.example('`devoice #channel username')
@plugin.example('`devoice username')
def channel_devoice(bot, trigger):
    """Remove voice from a user (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `devoice <#channel> <nick>')
        bot.notice(trigger.nick, '       `devoice <nick> (current channel)')
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `devoice <#channel> <nick>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'devoice'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"DEVOICE {channel} {target}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Devoiced {formatter.monospace(target)} in {channel}")
    else:
        # Direct IRC devoice
        bot.write(['MODE', channel, '-v', target])
        bot.say(f"Devoiced {formatter.monospace(target)} in {channel}")


@plugin.command('topic')
@plugin.example('`topic #channel New topic here')
@plugin.example('`topic New topic here')
def channel_topic(bot, trigger):
    """Set channel topic (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `topic <#channel> <topic>')
        bot.notice(trigger.nick, '       `topic <topic> (current channel)')
        return

    text = trigger.group(2).strip()
    channel = None
    topic = ''

    # Parse channel and topic
    if text.startswith('#'):
        parts = text.split(None, 1)
        channel = parts[0]
        if len(parts) > 1:
            topic = parts[1]
    else:
        channel = trigger.sender
        topic = text

    if not channel or not topic:
        bot.notice(trigger.nick, 'Usage: `topic <#channel> <topic>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'topic'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"TOPIC {channel} :{topic}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Set topic for {channel}")
    else:
        # Direct IRC topic
        bot.write(['TOPIC', channel], topic)
        bot.say(f"Set topic for {channel}")


@plugin.command('invite')
@plugin.example('`invite #channel username')
@plugin.example('`invite username')
def channel_invite(bot, trigger):
    """Invite a user to channel (uses ChanServ if available)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `invite <#channel> <nick>')
        bot.notice(trigger.nick, '       `invite <nick> (current channel)')
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `invite <#channel> <nick>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Check permissions via group system
    if not _has_command_permission(bot, trigger, 'invite'):
        bot.notice(trigger.nick, 'Permission denied.')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"INVITE {channel} {target}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Invited {formatter.monospace(target)} to {channel}")
    else:
        # Direct IRC invite
        bot.write(['INVITE', target, channel])
        bot.say(f"Invited {formatter.monospace(target)} to {channel}")


@plugin.command('banlist')
@plugin.example('`banlist #channel')
@plugin.example('`banlist')
def channel_banlist(bot, trigger):
    """List channel bans (uses ChanServ if available)."""
    channel = trigger.group(2) if trigger.group(2) else trigger.sender
    channel = channel.strip()

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Usage: `banlist [#channel]')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"BANLIST {channel}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Requested banlist for {channel} from ChanServ")
    else:
        # Request banlist via MODE
        bot.write(['MODE', channel, '+b'])
        bot.say(f"Requested banlist for {channel}")


@plugin.command('accesslist')
@plugin.example('`accesslist #channel')
@plugin.example('`accesslist')
def channel_accesslist(bot, trigger):
    """List channel access list (ChanServ only)."""
    channel = trigger.group(2) if trigger.group(2) else trigger.sender
    channel = channel.strip()

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Usage: `accesslist [#channel]')
        return

    # Only works with ChanServ
    if _is_channel_registered(bot, channel):
        cmd = f"ACCESS {channel} LIST"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Requested access list for {channel} from ChanServ")
    else:
        bot.notice(trigger.nick, f'{channel} is not registered.')


@plugin.command('chinfo')
@plugin.example('`chinfo #channel')
@plugin.example('`chinfo')
def channel_info(bot, trigger):
    """Get channel information (uses ChanServ if available)."""
    channel = trigger.group(2) if trigger.group(2) else trigger.sender
    channel = channel.strip()

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Usage: `chinfo [#channel]')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"INFO {channel}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Requested channel info for {channel} from ChanServ")
    else:
        # Show basic info from bot's perspective
        try:
            if channel in bot.channels:
                ch = bot.channels[channel]
                topic = getattr(ch, 'topic', 'No topic set')
                user_count = len(ch.users)
                modes = getattr(ch, 'modes', set())
                modes_str = ''.join(sorted(modes)) if modes else 'none'

                bot.say(f"{formatter.bold('Channel')}: {channel}")
                bot.say(f"Users: {user_count}, Modes: {modes_str}")
                if topic:
                    bot.say(f"Topic: {topic[:200]}")
            else:
                bot.notice(trigger.nick, f'Not in channel {channel}.')
        except Exception as e:
            logger.error(f'Error getting channel info: {e}')
            bot.notice(trigger.nick, 'Failed to get channel information.')


@plugin.command('chmodes')
@plugin.example('`chmodes #channel')
@plugin.example('`chmodes')
def channel_modes(bot, trigger):
    """Get channel modes (uses ChanServ if available)."""
    channel = trigger.group(2) if trigger.group(2) else trigger.sender
    channel = channel.strip()

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Usage: `chmodes [#channel]')
        return

    # Use ChanServ if channel is registered
    if _is_channel_registered(bot, channel):
        cmd = f"MODE {channel}"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Requested channel modes for {channel} from ChanServ")
    else:
        # Request modes via MODE
        bot.write(['MODE', channel])
        bot.say(f"Requested channel modes for {channel}")


@plugin.command('chtopic')
@plugin.example('`chtopic #channel')
@plugin.example('`chtopic')
def channel_topic_view(bot, trigger):
    """View channel topic."""
    channel = trigger.group(2) if trigger.group(2) else trigger.sender
    channel = channel.strip()

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Usage: `chtopic [#channel]')
        return

    try:
        if channel in bot.channels:
            ch = bot.channels[channel]
            topic = getattr(ch, 'topic', 'No topic set')
            topic_author = getattr(ch, 'topic_author', '')
            topic_time = getattr(ch, 'topic_time', 0)

            bot.say(f"{formatter.bold('Topic')} for {channel}: {topic}")
            if topic_author and topic_time:
                try:
                    topic_date = datetime.fromtimestamp(topic_time)
                    date_str = topic_date.strftime('%Y-%m-%d %H:%M:%S')
                    bot.say(f"Set by {topic_author} on {date_str}")
                except Exception:
                    pass
        else:
            bot.notice(trigger.nick, f'Not in channel {channel}.')
    except Exception as e:
        logger.error(f'Error getting topic: {e}')
        bot.notice(trigger.nick, 'Failed to get channel topic.')


@plugin.command('chusers')
@plugin.example('`chusers #channel')
@plugin.example('`chusers')
def channel_users(bot, trigger):
    """List channel users with their modes."""
    channel = trigger.group(2) if trigger.group(2) else trigger.sender
    channel = channel.strip()

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Usage: `chusers [#channel]')
        return

    try:
        if channel not in bot.channels:
            bot.notice(trigger.nick, f'Not in channel {channel}.')
            return

        ch = bot.channels[channel]
        users = ch.users

        # Count users by privilege
        ops = []
        halfops = []
        voiced = []
        normal = []

        for nick, priv in users.items():
            if priv >= plugin.OP:
                ops.append(nick)
            elif priv >= plugin.HALFOP:
                halfops.append(nick)
            elif priv >= plugin.VOICE:
                voiced.append(nick)
            else:
                normal.append(nick)

        total = len(users)
        bot.say(
            f"{formatter.bold('Channel Users')} for {channel}: {total} total"
        )

        if ops:
            ops_list = ', '.join(sorted(ops)[:20])
            bot.say(f"Ops ({len(ops)}): {ops_list}")
            if len(ops) > 20:
                bot.say(f"... and {len(ops) - 20} more ops")
        if halfops:
            halfops_list = ', '.join(sorted(halfops)[:20])
            bot.say(f"Halfops ({len(halfops)}): {halfops_list}")
            if len(halfops) > 20:
                bot.say(f"... and {len(halfops) - 20} more halfops")
        if voiced:
            voiced_list = ', '.join(sorted(voiced)[:20])
            bot.say(f"Voiced ({len(voiced)}): {voiced_list}")
            if len(voiced) > 20:
                bot.say(f"... and {len(voiced) - 20} more voiced")
        if normal:
            normal_count = len(normal)
            if normal_count <= 10:
                normal_list = ', '.join(sorted(normal))
                bot.say(f"Normal ({normal_count}): {normal_list}")
            else:
                normal_list = ', '.join(sorted(normal)[:10])
                bot.say(
                    f"Normal ({normal_count}): {normal_list} "
                    f"... and {normal_count - 10} more"
                )

    except Exception as e:
        logger.error(f'Error getting channel users: {e}')
        bot.notice(trigger.nick, 'Failed to get channel users.')


@plugin.command('chflags')
@plugin.example('`chflags #channel username')
@plugin.example('`chflags username')
def channel_flags(bot, trigger):
    """View user's flags/permissions in channel (ChanServ only)."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `chflags [#channel] <nick>')
        return

    parts = trigger.group(2).strip().split()
    channel = None
    target = None

    if len(parts) >= 1:
        if parts[0].startswith('#'):
            channel = parts[0]
            if len(parts) >= 2:
                target = parts[1]
        else:
            channel = trigger.sender
            target = parts[0]

    if not channel or not target:
        bot.notice(trigger.nick, 'Usage: `chflags [#channel] <nick>')
        return

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Invalid channel name.')
        return

    # Only works with ChanServ
    if _is_channel_registered(bot, channel):
        cmd = f"FLAGS {channel} {target}"
        _send_chanserv_command(bot, cmd)
        target_fmt = formatter.monospace(target)
        bot.say(f"Requested flags for {target_fmt} in {channel} from ChanServ")
    else:
        bot.notice(trigger.nick, f'{channel} is not registered.')


@plugin.command('chsettings')
@plugin.example('`chsettings #channel')
@plugin.example('`chsettings')
def channel_settings(bot, trigger):
    """View channel settings (ChanServ only)."""
    channel = trigger.group(2) if trigger.group(2) else trigger.sender
    channel = channel.strip()

    if not channel.startswith('#'):
        bot.notice(trigger.nick, 'Usage: `chsettings [#channel]')
        return

    # Only works with ChanServ
    if _is_channel_registered(bot, channel):
        cmd = f"SET {channel} LIST"
        _send_chanserv_command(bot, cmd)
        bot.say(f"Requested channel settings for {channel} from ChanServ")
    else:
        bot.notice(trigger.nick, f'{channel} is not registered.')
