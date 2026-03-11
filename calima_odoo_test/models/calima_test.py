from odoo import fields, models


class CalimaTest(models.Model):
    """Minimal test model used to verify that addon loading works correctly."""

    _name = 'calima.test'
    _description = 'Calima Test'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
