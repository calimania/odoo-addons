from odoo import fields, models


class CalimaTest(models.Model):
    """Minimal test model used to verify that the ORM and DB write layer work."""

    _name = 'calima.test'
    _description = 'Calima Debug – Test Record'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
