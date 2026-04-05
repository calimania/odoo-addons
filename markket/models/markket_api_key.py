from odoo import fields, models


class MarkketApiKey(models.Model):
    _name = 'markket.api.key'
    _description = 'Markket API Key'
    _order = 'id desc'

    name = fields.Char(required=True)
    owner_user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user, index=True)
    active = fields.Boolean(default=True)
    api_key = fields.Char(required=True)
    notes = fields.Text()
    masked_key = fields.Char(compute='_compute_masked_key', store=False)

    def _compute_masked_key(self):
        for record in self:
            if not record.api_key:
                record.masked_key = False
                continue
            size = len(record.api_key)
            if size <= 8:
                record.masked_key = '*' * size
            else:
                record.masked_key = f"{record.api_key[:4]}...{record.api_key[-4:]}"
