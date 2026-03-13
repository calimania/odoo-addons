import json
import platform
import sys
from datetime import datetime, timezone

import odoo.release as release
from odoo import api, fields, models
from odoo.http import request

from .calima_debug_info import _censor


class CalimaDebugJson(models.TransientModel):
    """Pretty JSON snapshot for quick diagnostics in the Odoo UI."""

    _name = 'calima.debug.json'
    _description = 'Calima Debug - JSON Snapshot'

    generated_at = fields.Datetime(string='Generated At (UTC)', readonly=True)
    request_host = fields.Char(string='Request Host', readonly=True)
    payload_json = fields.Text(string='Payload (JSON)', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        icp = self.env['ir.config_parameter'].sudo()
        addons_paths = []
        try:
            from odoo.tools import config as odoo_config
            raw = odoo_config.get('addons_path', '')
            addons_paths = [p.strip() for p in raw.split(',') if p.strip()]
        except Exception:
            addons_paths = []

        payload = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'odoo': {
                'version': release.version,
                'version_info': str(release.version_info),
                'base_url': icp.get_param('web.base.url', 'Not configured'),
            },
            'runtime': {
                'python': sys.version.split('\n')[0].strip(),
                'os': f'{platform.system()} {platform.release()} ({platform.machine()})',
                'timezone': icp.get_param('web.server.timezone', 'UTC (default)'),
            },
            'database': {
                'name_censored': _censor(self.env.cr.dbname or ''),
            },
            'modules': {
                'installed_count': self.env['ir.module.module'].sudo().search_count(
                    [('state', '=', 'installed')]
                ),
            },
            'addons_paths': addons_paths,
            'api_routes': [
                '/api/public/events',
                '/api/public/events/debug',
            ],
        }

        host = 'n/a'
        if request and request.httprequest:
            host = request.httprequest.host or 'n/a'

        res['generated_at'] = fields.Datetime.now()
        res['request_host'] = host
        res['payload_json'] = json.dumps(payload, indent=2, ensure_ascii=True)
        return res
