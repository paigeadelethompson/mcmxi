"""
Sopel permission checking utilities.
"""
from sopel import plugin


# Permissions utility
class Permissions:
    """Helper for Sopel permission checks."""

    @staticmethod
    def require_privilege(bot, trigger, level: int):
        """
        Require a privilege level.
        Levels: 0=anyone, 1=voiced, 2=halfop, 3=op, 4=admin, 5=owner
        """
        if not trigger.sender:
            return False

        if level == 0:
            return True

        channel = trigger.sender
        nick = trigger.nick

        if level >= 5:  # Owner
            if bot.config.core.owner and nick.lower() == bot.config.core.owner.lower():
                return True

        if level >= 4:  # Admin
            if bot.config.core.admins and nick.lower() in [a.lower() for a in bot.config.core.admins]:
                return True

        if level >= 3:  # Op
            if bot.channels[channel].privileges[nick] >= plugin.OP:
                return True

        if level >= 2:  # Halfop
            if bot.channels[channel].privileges[nick] >= plugin.HALFOP:
                return True

        if level >= 1:  # Voiced
            if bot.channels[channel].privileges[nick] >= plugin.VOICE:
                return True

        return False

    @staticmethod
    def has_privilege(bot, trigger, level: int) -> bool:
        """Check if user has privilege level."""
        return Permissions.require_privilege(bot, trigger, level)

