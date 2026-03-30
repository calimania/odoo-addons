# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SendgridInboundLog(models.Model):
    """Stores inbound webhook processing attempts for visibility."""

    _name = 'sendgrid.inbound.log'
    _description = 'SendGrid Inbound Log'
    _order = 'create_date desc'

    subject = fields.Char(string='Subject')
    from_addr = fields.Char(string='From')
    to_addr = fields.Char(string='To')
    message_id = fields.Char(string='Message-ID')
    state = fields.Selection([
        ('processed', 'Processed'),
        ('fallback', 'Stored Fallback'),
        ('error', 'Error'),
    ], string='State', default='processed')
    error_text = fields.Text(string='Error')
    body_text = fields.Text(string='Body (Text)', help='Plain text content of the email')
    body_html = fields.Html(string='Body (HTML)', help='HTML content of the email')
    mail_message_id = fields.Many2one(
        'mail.message',
        string='Mail Message',
        help='Resulting mail.message (routed or fallback)'
    )

    # Routing context — computed from the linked mail.message
    routed_model = fields.Char(
        string='Routed To (Model)',
        compute='_compute_routing',
        store=True,
        help='The Odoo model the email was routed to (e.g. crm.lead, helpdesk.ticket)',
    )
    routed_res_id = fields.Integer(
        string='Routed Record ID',
        compute='_compute_routing',
        store=True,
    )
    routed_record_name = fields.Char(
        string='Routed Record',
        compute='_compute_routing',
        store=True,
        help='Name of the record the email was routed to',
    )

    @api.depends('mail_message_id', 'mail_message_id.model', 'mail_message_id.res_id')
    def _compute_routing(self):
        for log in self:
            msg = log.mail_message_id
            if msg and msg.model and msg.res_id:
                log.routed_model = msg.model
                log.routed_res_id = msg.res_id
                try:
                    record = self.env[msg.model].sudo().browse(msg.res_id)
                    log.routed_record_name = record.display_name if record.exists() else False
                except Exception:
                    log.routed_record_name = False
            else:
                log.routed_model = False
                log.routed_res_id = 0
                log.routed_record_name = False

    def action_open_routed_record(self):
        """Open the record this email was routed to."""
        self.ensure_one()
        if not self.routed_model or not self.routed_res_id:
            return False
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.routed_model,
            'res_id': self.routed_res_id,
            'view_mode': 'form',
            'target': 'current',
        }
