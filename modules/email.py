"""
Sopel module for Email APIs.
Supports 8 public APIs with no authentication required.
"""

import os
import sys

from sopel import plugin

# Ensure we can import common
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import GraphQLClient, HTTPClient, IRCFormatter, get_module_logger, register_apis

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
@plugin.example('`email_disify test@example.com')
def email_disify(bot, trigger):
    """Validate email address using Disify API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `email_disify <email_address>')
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


@plugin.command('email_kickbox')
@plugin.example('`email_kickbox test@example.com')
def email_kickbox(bot, trigger):
    """Verify email address using Kickbox API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `email_kickbox <email_address>')
        return

    email = trigger.group(2).strip()
    logger.info(f'Kickbox email verification: {email}')

    encoded_email = http.quote(email)
    url = f'https://open.kickbox.com/v1/verify?email={encoded_email}&apikey=free'

    logger.debug(f'Verifying email: {url}')
    data = http.get(url, timeout=10)

    if not data:
        bot.notice(trigger.nick, 'Failed to verify email. Please try again.')
        return

    result = data.get('result', 'unknown')
    reason = data.get('reason', '')
    role = data.get('role', False)
    disposable = data.get('disposable', False)
    accept_all = data.get('accept_all', False)
    did_you_mean = data.get('did_you_mean', '')

    response = f"Email {formatter.monospace(email)}: {formatter.bold(result.upper())}"
    
    if reason:
        response += f" | {reason}"
    if role:
        response += f" | {formatter.italic('Role-based')}"
    if disposable:
        response += f" | {formatter.bold('Disposable')}"
    if accept_all:
        response += f" | {formatter.italic('Accepts all')}"
    if did_you_mean:
        response += f" | Did you mean: {formatter.monospace(did_you_mean)}"

    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('email_mailcheck')
@plugin.example('`email_mailcheck test@example.com')
def email_mailcheck(bot, trigger):
    """Check if email is temporary/disposable using MailCheck.ai API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `email_mailcheck <email_address>')
        return

    email = trigger.group(2).strip()
    logger.info(f'MailCheck.ai validation: {email}')

    encoded_email = http.quote(email)
    url = f'https://api.mailcheck.ai/v1/email/{encoded_email}'

    logger.debug(f'Checking email: {url}')
    data = http.get(url, timeout=10)

    if not data:
        bot.notice(trigger.nick, 'Failed to check email. Please try again.')
        return

    is_disposable = data.get('disposable', False)
    is_valid = data.get('valid', True)
    domain = data.get('domain', '')
    reason = data.get('reason', '')

    response = f"Email {formatter.monospace(email)}:"
    if is_valid:
        response += f" {formatter.bold('Valid')}"
    else:
        response += f" {formatter.bold('Invalid')}"
    
    if is_disposable:
        response += f" | {formatter.bold('Disposable/Temporary')}"
    else:
        response += f" | {formatter.bold('Not disposable')}"
    
    if domain:
        response += f" | Domain: {formatter.italic(domain)}"
    if reason:
        response += f" | {reason}"

    bot.say(formatter.truncate(response, max_len=400))


@plugin.command('email_guerrilla')
@plugin.example('`email_guerrilla get_email_address')
def email_guerrilla(bot, trigger):
    """Get a disposable email address from Guerrilla Mail."""
    action = trigger.group(2).strip().lower() if trigger.group(2) else 'get_email_address'
    
    if action == 'get_email_address':
        # Get a new email address
        url = 'https://www.guerrillamail.com/ajax.php?f=get_email_address&ip=127.0.0.1&agent=Mozilla_foo_bar'
        logger.info('Getting Guerrilla Mail address')
        
        data = http.get(url, timeout=10)
        
        if not data:
            bot.notice(trigger.nick, 'Failed to get email address.')
            return
        
        email = data.get('email_addr', '')
        email_token = data.get('email_timestamp', '')
        
        if email:
            bot.say(f"Guerrilla Mail address: {formatter.bold(email)}")
            if email_token:
                bot.notice(trigger.nick, f"Token: {formatter.monospace(email_token)}")
        else:
            bot.notice(trigger.nick, 'Failed to get email address.')
    else:
        bot.notice(trigger.nick, 'Usage: `email_guerrilla get_email_address')


@plugin.command('email_dropmail')
@plugin.example('`email_dropmail create')
@plugin.example('`email_dropmail inbox <session_id>')
def email_dropmail(bot, trigger):
    """Create or manage ephemeral email inboxes using DropMail GraphQL API."""
    if not trigger.group(2):
        bot.notice(trigger.nick, 'Usage: `email_dropmail create')
        bot.notice(trigger.nick, '       `email_dropmail inbox <session_id>')
        return

    args = trigger.group(2).strip().split(None, 1)
    action = args[0].lower()

    # DropMail uses a token in the URL (8+ chars, can be any string for now)
    import uuid
    auth_token = uuid.uuid4().hex[:8]
    gql_client = GraphQLClient(
        f'https://dropmail.me/api/graphql/{auth_token}'
    )

    if action == 'create':
        # Create a new inbox
        query = """
        mutation {
            introduceSession {
                id
                addresses {
                    address
                }
            }
        }
        """

        logger.info('Creating DropMail inbox')
        result = gql_client.execute(query)

        if not result or 'introduceSession' not in result:
            bot.notice(trigger.nick, 'Failed to create DropMail inbox.')
            return

        session = result['introduceSession']
        session_id = session.get('id', '')
        addresses = session.get('addresses', [])

        if addresses:
            address = addresses[0].get('address', '')
            bot.say(f"DropMail inbox created: {formatter.bold(address)}")
            bot.notice(trigger.nick, f"Session ID: {formatter.monospace(session_id)}")
        else:
            bot.notice(trigger.nick, 'Failed to create inbox.')

    elif action == 'inbox' and len(args) > 1:
        # Get messages for an inbox
        session_id = args[1].strip()

        query = """
        query ($id: ID!) {
            session(id: $id) {
                mails {
                    rawSize
                    fromAddr
                    toAddr
                    downloadUrl
                    text
                    headerSubject
                }
            }
        }
        """

        logger.info(f'Getting DropMail messages for session: {session_id}')
        result = gql_client.execute(query, {'id': session_id})

        if not result or 'session' not in result:
            bot.notice(trigger.nick, 'Failed to get inbox messages.')
            return

        session = result['session']
        mails = session.get('mails', [])

        if not mails:
            bot.notice(trigger.nick, 'No messages in inbox.')
            return

        bot.say(
            f"{formatter.bold('DropMail Messages')} "
            f"({formatter.underline(str(len(mails)))} total):"
        )

        for i, mail in enumerate(mails[:5], 1):
            subject = mail.get('headerSubject', 'No Subject')
            from_addr = mail.get('fromAddr', 'Unknown')

            response_parts = [
                f"{i}. {formatter.bold(subject)}",
                f"From: {formatter.italic(from_addr)}"
            ]

            bot.say(' | '.join(response_parts))

        if len(mails) > 5:
            bot.say(f"... and {len(mails) - 5} more messages")

    else:
        bot.notice(trigger.nick, 'Usage: `email_dropmail create')
        bot.notice(trigger.nick, '       `email_dropmail inbox <session_id>')


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
