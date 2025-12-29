"""
Sopel module for Email APIs.
Supports 8 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HTTPClient, IRCFormatter, get_module_logger, register_apis

logger = get_module_logger(__name__)
http = HTTPClient(max_size=5 * 1024 * 1024)
formatter = IRCFormatter()


# API definitions
APIS = [
    {
        'name': 'Disify',
        'description': 'Validate and detect disposable and temporary email addresses',
        'link': 'https://www.disify.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'DropMail',
        'description': 'GraphQL API for creating and managing ephemeral e-mail inboxes',
        'link': 'https://dropmail.me/api/#live-demo',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Guerrilla Mail',
        'description': 'Disposable temporary Email addresses',
        'link': 'https://www.guerrillamail.com/GuerrillaMailAPI.html',
        'https': True,
        'cors': 'unknown',
    },
    {
        'name': 'Heybounce',
        'description': 'Email Verification API',
        'link': 'https://www.heybounce.io/#email-verification-api',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'Kickbox',
        'description': 'Email verification API',
        'link': 'https://open.kickbox.com/',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'mail.gw',
        'description': '10 Minute Mail',
        'link': 'https://docs.mail.gw',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'mail.tm',
        'description': 'Temporary Email Service',
        'link': 'https://docs.mail.tm',
        'https': True,
        'cors': 'yes',
    },
    {
        'name': 'MailCheck.ai',
        'description': 'Prevent users to sign up with temporary email addresses',
        'link': 'https://www.mailcheck.ai/#documentation',
        'https': True,
        'cors': 'unknown',
    },
]


@plugin.command('email_disify')
@plugin.example('.email_disify test@example.com')
def email_disify(bot, trigger):
    """Validate email address using Disify API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: .email_disify <email_address>')
        return

    email = trigger.group(2).strip()
    logger.info(f'Email validation: {email}')

    encoded_email = http.quote(email)
    url = f'https://www.disify.com/api/email/{encoded_email}'

    logger.debug(f'Validating email: {url}')
    data = http.get(url)

    if not data:
        bot.notice(trigger.nick, 'Failed to validate email. Please try again.')
        return

    is_valid = data.get('valid', False)
    is_disposable = data.get('disposable', False)
    is_dns_valid = data.get('dns', {}).get('valid', False)
    domain = data.get('domain', 'Unknown')

    response = f"Email {formatter.monospace(email)}:"
    if is_valid:
        response += f" {formatter.bold('Valid')}"
    else:
        response += f" {formatter.bold('Invalid')}"

    if is_disposable:
        response += f" | {formatter.bold('Disposable')}"
    if domain != 'Unknown':
        response += f" | Domain: {formatter.italic(domain)}"
    if is_dns_valid:
        response += f" | DNS: {formatter.bold('Valid')}"

    bot.say(formatter.truncate(response, max_len=400))


def setup(bot):
    """Module setup - Email APIs loaded."""
    register_apis('email', APIS)
    bot.memory['email_loaded'] = True
    bot.memory['email_count'] = 8
    logger.info('Email module loaded')


def shutdown(bot):
    """Module shutdown."""
    bot.memory['email_loaded'] = False
    logger.info('Email module unloaded')
