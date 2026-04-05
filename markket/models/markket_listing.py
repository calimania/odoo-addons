from odoo import fields, models


class MarkketListing(models.Model):
    _name = 'markket.listing'
    _description = 'Markket Listing'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    description = fields.Text()
    external_ref = fields.Char(help='Placeholder external marketplace identifier.')
