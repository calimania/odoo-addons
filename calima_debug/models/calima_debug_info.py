import platform
import sys

import odoo.release as release
from odoo import api, fields, models


def _censor(value, visible=3):
    """Return *value* with all but the first *visible* characters replaced by asterisks."""
    if not value:
        return '***'
    shown = value[:visible]
    hidden = len(value) - visible
    return shown + ('*' * max(hidden, 3))


class CalimaDebugInfo(models.TransientModel):
    """Read-only system information dashboard for self-hosting administrators.

    Opens as a wizard so the data is always freshly computed; nothing is
    persisted in the database.
    """

    _name = 'calima.debug.info'
    _description = 'Calima Debug – System Info'

    # --- Odoo ----------------------------------------------------------------

    odoo_version = fields.Char(string='Odoo Version', readonly=True)
    odoo_version_info = fields.Char(string='Version Detail', readonly=True)
    server_mode = fields.Char(string='Server Mode', readonly=True)

    # --- Python / OS ---------------------------------------------------------

    python_version = fields.Char(string='Python Version', readonly=True)
    os_info = fields.Char(string='Operating System', readonly=True)

    # --- Database ------------------------------------------------------------

    database_name = fields.Char(string='Database Name (censored)', readonly=True)

    # --- Web / Network -------------------------------------------------------

    base_url = fields.Char(string='Base URL', readonly=True)
    server_timezone = fields.Char(string='Server Timezone', readonly=True)

    # --- Modules -------------------------------------------------------------

    installed_modules_count = fields.Integer(string='Installed Modules', readonly=True)

    # --- Paths ---------------------------------------------------------------

    addons_paths = fields.Text(string='Addon Paths', readonly=True)

    # -------------------------------------------------------------------------

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        # Odoo version
        res['odoo_version'] = release.version
        res['odoo_version_info'] = str(release.version_info)

        # Server mode
        try:
            from odoo.tools import config
            res['server_mode'] = 'debug' if config.get('dev_mode') else 'production'
        except Exception:
            res['server_mode'] = 'unknown'

        # Python / OS
        res['python_version'] = sys.version.split('\n')[0].strip()
        res['os_info'] = f'{platform.system()} {platform.release()} ({platform.machine()})'

        # Database name — censor all but first 3 chars
        db = self.env.cr.dbname or ''
        res['database_name'] = _censor(db)

        # Base URL
        icp = self.env['ir.config_parameter'].sudo()
        res['base_url'] = icp.get_param('web.base.url', 'Not configured')

        # Server timezone
        res['server_timezone'] = icp.get_param('web.server.timezone', 'UTC (default)')

        # Installed modules
        res['installed_modules_count'] = self.env['ir.module.module'].sudo().search_count(
            [('state', '=', 'installed')]
        )

        # Addon paths
        try:
            from odoo.tools import config as odoo_config
            raw = odoo_config.get('addons_path', '')
            paths = [p.strip() for p in raw.split(',') if p.strip()]
            res['addons_paths'] = '\n'.join(paths) if paths else 'Not available'
        except Exception:
            res['addons_paths'] = 'Not available'

        return res
