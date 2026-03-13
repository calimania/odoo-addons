import json
import os
import time

from odoo import fields, http
from odoo.http import Response, request


class CalimaPublicApi(http.Controller):
    """Public JSON endpoints for integrations and website clients."""

    @staticmethod
    def _json_response(payload, status=200, cache_seconds=120):
        body = json.dumps(payload, ensure_ascii=True)
        headers = [
            ('Content-Type', 'application/json; charset=utf-8'),
            ('Cache-Control', f'public, max-age={cache_seconds}'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, X-Calima-Debug-Token'),
        ]
        return Response(body, status=status, headers=headers)

    @http.route('/api/public/events', type='http', auth='public', methods=['OPTIONS'], csrf=False, save_session=False)
    def events_options(self, **_kw):
        return self._json_response({'ok': True}, cache_seconds=300)

    @http.route('/api/public/events', type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def events(self, **kw):
        started = time.time()

        limit = min(max(int(kw.get('limit', 20)), 1), 100)
        page = max(int(kw.get('page', 1)), 1)
        offset = (page - 1) * limit

        Event = request.env['event.event'].sudo()
        domain = [
            ('website_published', '=', True),
            ('date_end', '>=', fields.Datetime.now()),
        ]

        website = getattr(request, 'website', None)
        if website and 'website_id' in Event._fields:
            domain += ['|', ('website_id', '=', False), ('website_id', '=', website.id)]

        total = Event.search_count(domain)
        events = Event.search(domain, order='date_begin asc, id asc', limit=limit, offset=offset)

        data = []
        for event in events:
            address = event.address_id
            data.append({
                'id': event.id,
                'name': event.name,
                'summary': event.subtitle or '',
                'start_at': str(event.date_begin or ''),
                'end_at': str(event.date_end or ''),
                'event_url': event.website_url or '',
                'image_url': f'/web/image/event.event/{event.id}/image_1920',
                'city': address.city if address else '',
                'country': address.country_id.name if address and address.country_id else '',
            })

        website_name = website.name if website else ''
        company_name = website.company_id.name if website and website.company_id else ''

        payload = {
            'api_version': 1,
            'generated_at': fields.Datetime.now().isoformat(),
            'website_name': website_name,
            'company_name': company_name,
            'page': page,
            'page_size': limit,
            'total': total,
            'has_more': offset + len(data) < total,
            'events': data,
            'query_ms': int((time.time() - started) * 1000),
        }
        return self._json_response(payload, cache_seconds=120)

    @http.route('/api/public/events/debug', type='http', auth='public', methods=['OPTIONS'], csrf=False, save_session=False)
    def events_debug_options(self, **_kw):
        return self._json_response({'ok': True}, cache_seconds=30)

    @http.route('/api/public/events/debug', type='http', auth='public', methods=['GET'], csrf=False, save_session=False)
    def events_debug(self, **kw):
        debug_enabled = os.environ.get('CALIMA_DEBUG_API', 'true').lower() in {'1', 'true', 'yes', 'on'}
        if not debug_enabled:
            return self._json_response({'error': 'not_found'}, status=404, cache_seconds=0)

        required_token = os.environ.get('CALIMA_DEBUG_TOKEN', '').strip()
        provided_token = request.httprequest.headers.get('X-Calima-Debug-Token') or kw.get('token', '')
        if required_token and provided_token != required_token:
            return self._json_response({'error': 'unauthorized'}, status=401, cache_seconds=0)

        Event = request.env['event.event'].sudo()
        website = getattr(request, 'website', None)

        domain = [
            ('website_published', '=', True),
            ('date_end', '>=', fields.Datetime.now()),
        ]
        if website and 'website_id' in Event._fields:
            domain += ['|', ('website_id', '=', False), ('website_id', '=', website.id)]

        payload = {
            'debug': True,
            'host': request.httprequest.host,
            'website': {
                'id': website.id if website else False,
                'name': website.name if website else '',
                'company_id': website.company_id.id if website and website.company_id else False,
                'company_name': website.company_id.name if website and website.company_id else '',
            },
            'event_model_available': bool(Event),
            'effective_domain': domain,
            'matching_count': Event.search_count(domain),
            'limit_default': 20,
            'notes': 'Set CALIMA_DEBUG_TOKEN to require X-Calima-Debug-Token header.',
        }
        return self._json_response(payload, cache_seconds=15)
