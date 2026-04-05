# -*- coding: utf-8 -*-
"""
SendGrid Inbound Parse Webhook Controller

Receives POSTs from SendGrid Inbound Parse and routes them through
Odoo's mail gateway (message_process) for proper alias routing,
partner matching, and thread handling.

SendGrid setup:
1. Configure Inbound Parse at https://app.sendgrid.com/settings/parse
2. Set URL to: https://yourdomain.com/mail/sendgrid/inbound?token=YOUR_SECRET
3. Check "POST the raw, full MIME message"
4. Optionally check spam filter

Environment variable:
- SENDGRID_INBOUND_SECRET: Token for webhook authentication
"""
import base64
import email
import logging
import os

from odoo import http, _, SUPERUSER_ID
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

# Load secret from environment - MUST be set in production
SECRET = os.environ.get('SENDGRID_INBOUND_SECRET', 'changeme')

if SECRET == 'changeme':
    _logger.warning(
        'sendgrid_inbound: SENDGRID_INBOUND_SECRET is not set. '
        'The webhook endpoint is using the default insecure token. '
        'Set SENDGRID_INBOUND_SECRET in your environment before going to production.'
    )


class SendgridInbound(http.Controller):

    @http.route('/mail/sendgrid/inbound', type='http', auth='none',
                methods=['POST'], csrf=False, save_session=False)
    def handle_inbound_email(self, **kw):
        """
        Handle inbound email from SendGrid Inbound Parse.

        SendGrid sends multipart/form-data with:
        - 'email': raw MIME message (if "POST raw" is enabled)
        - Other fields: from, to, subject, text, html, attachments, etc.

        We prefer the raw MIME and pass it to Odoo's mail gateway
        for proper routing (aliases, threading, partner matching).
        """
        # Validate token via query param or header
        token = request.params.get('token') or \
                request.httprequest.headers.get('X-Webhook-Token')

        if not token or token != SECRET:
            _logger.warning('SendGrid webhook: unauthorized attempt from %s',
                          request.httprequest.remote_addr)
            return Response('unauthorized', status=401)

        # Get the raw MIME message from 'email' file field
        f = request.httprequest.files.get('email')
        if not f:
            # Fallback: try to get from form field (non-raw mode)
            raw_text = request.params.get('email')
            if raw_text:
                raw = raw_text.encode('utf-8') if isinstance(raw_text, str) else raw_text
            else:
                _logger.error('SendGrid webhook: no email content received')
                return Response('missing email file', status=400)
        else:
            # Read raw bytes of the uploaded MIME message
            try:
                raw = f.stream.read()
            except Exception:
                raw = f.read()

        if not raw:
            _logger.error('SendGrid webhook: empty email content')
            return Response('empty email', status=400)

        # Parse the MIME message for logging and content extraction
        try:
            msg = email.message_from_bytes(raw)
            subject = msg.get('Subject', '(no subject)')
            from_addr = msg.get('From', 'unknown')
            to_addr = msg.get('To', 'unknown')
            message_id = msg.get('Message-ID', '')

            # Extract text and HTML parts
            body_text, body_html = self._extract_email_body(msg)

            _logger.info('SendGrid inbound: from=%s to=%s subject=%s msgid=%s',
                        from_addr, to_addr, subject, message_id)
        except Exception as e:
            _logger.warning('SendGrid webhook: failed to parse MIME headers: %s', e)
            subject = '(parse error)'
            from_addr = 'unknown'
            to_addr = 'unknown'
            body_text = None
            body_html = None

        # Route through Odoo's mail gateway for proper handling
        # This handles: alias routing, partner matching, thread creation
        try:
            with request.env.cr.savepoint():
                MailThread = request.env['mail.thread'].with_user(SUPERUSER_ID)

                # message_process routes based on To: address and aliases
                # If no alias matches, it creates a standalone mail.message
                result = MailThread.message_process(
                    model=False,  # Let Odoo determine from alias
                    message=raw,
                    # We keep our own copy of the EML on the log record, not on the message
                    save_original=False,
                    strip_attachments=False,
                )
                mail_message = self._find_message_by_msgid(message_id)
                log = self._create_log(subject, from_addr, to_addr, message_id,
                                       state='processed', mail_message_id=(mail_message.id if mail_message else False),
                                       raw=raw, body_text=body_text, body_html=body_html)
                _logger.info('SendGrid inbound: processed successfully, result=%s, log=%s', result, log.id)

        except Exception as e:
            _logger.exception('SendGrid webhook: message_process failed: %s', e)
            # Fallback: store raw message even if routing fails
            try:
                mail_message = self._store_raw_message(raw, subject, from_addr)
                self._create_log(subject, from_addr, to_addr, message_id,
                                 state='fallback', error_text=str(e),
                                 mail_message_id=mail_message.id, raw=raw,
                                 body_text=body_text, body_html=body_html)
                _logger.info('SendGrid inbound: stored raw message as fallback')
            except Exception as e2:
                self._create_log(subject, from_addr, to_addr, message_id,
                                 state='error', error_text=str(e2))
                _logger.exception('SendGrid webhook: fallback storage failed: %s', e2)
                return Response('processing error', status=500)

        return Response('ok', status=200)

    def _store_raw_message(self, raw, subject, from_addr):
        """
        Fallback: create a mail.message without attaching the raw EML.
        The raw is stored on the log record instead, to avoid bloating replies.
        """
        MailMessage = request.env['mail.message'].with_user(SUPERUSER_ID).sudo()

        message_vals = {
            'subject': subject or 'Inbound email (unrouted)',
            'body': _('<p>Inbound email received from <b>%s</b></p>'
                     '<p><i>This message could not be automatically routed.</i></p>') % (from_addr or 'unknown'),
            'message_type': 'email',
            'subtype_id': request.env.ref('mail.mt_note').id,
        }
        return MailMessage.create(message_vals)

    def _create_log(self, subject, from_addr, to_addr, message_id, state,
                    error_text=None, mail_message_id=None, raw=None,
                    body_text=None, body_html=None):
        """Persist a lightweight log and keep EML attached only to the log."""
        Log = request.env['sendgrid.inbound.log'].with_user(SUPERUSER_ID).sudo()
        log = Log.create({
            'subject': subject,
            'from_addr': from_addr,
            'to_addr': to_addr,
            'message_id': message_id,
            'state': state,
            'error_text': error_text,
            'body_text': body_text,
            'body_html': body_html,
            'mail_message_id': mail_message_id or False,
        })

        if raw:
            request.env['ir.attachment'].with_user(SUPERUSER_ID).sudo().create({
                'name': f'{subject or "inbound"}.eml',
                'datas': base64.b64encode(raw).decode('ascii'),
                'res_model': 'sendgrid.inbound.log',
                'res_id': log.id,
                'mimetype': 'message/rfc822',
            })

        return log

    def _find_message_by_msgid(self, message_id):
        """Find the mail.message by Message-ID header, if present."""
        if not message_id:
            return None
        return request.env['mail.message'].with_user(SUPERUSER_ID).sudo().search([
            ('message_id', '=', message_id)
        ], limit=1, order='id desc')

    def _extract_email_body(self, msg):
        """Extract plain text and HTML parts from email message."""
        body_text = None
        body_html = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' and not body_text:
                    try:
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception:
                        pass
                elif content_type == 'text/html' and not body_html:
                    try:
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception:
                        pass
        else:
            content_type = msg.get_content_type()
            try:
                payload = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                if content_type == 'text/plain':
                    body_text = payload
                elif content_type == 'text/html':
                    body_html = payload
            except Exception:
                pass

        return body_text, body_html
