from odoo import fields, models


class MarkketStoreUrl(models.Model):
    _name = 'markket.store.url'
    _description = 'Markket Store URL'
    _order = 'sequence, id'

    store_id = fields.Many2one('markket.store', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(default=10)

    markket_url_id = fields.Integer(index=True)
    label = fields.Char(required=True)
    url = fields.Char(required=True)

    active = fields.Boolean(default=True)
