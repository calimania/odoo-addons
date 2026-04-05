from odoo import http
from odoo.http import request, Response


class MarkketController(http.Controller):

    @http.route('/markket/health', type='http', auth='public', methods=['GET'], csrf=False)
    def markket_health(self, **kwargs):
        return Response('markket:ok', status=200, content_type='text/plain; charset=utf-8')

    @http.route('/markket/stores/sync', type='json', auth='user', methods=['POST'], csrf=False)
    def sync_store_from_slug(self, slug=None, owner_user_id=None, **kwargs):
        if not slug:
            return {'ok': False, 'error': 'slug is required'}

        store = request.env['markket.store'].sync_store_from_public_api(
            slug=slug,
            owner_user_id=owner_user_id,
        )
        return {
            'ok': True,
            'store_id': store.id,
            'store_slug': store.store_slug,
            'name': store.name,
        }

    @http.route('/markket/webhook/incoming', type='http', auth='none', methods=['POST'], csrf=False)
    def receive_store_push(self, store_slug=None, content_type=None, signature=None, timestamp=None, **kwargs):
        return Response(
            'not implemented: incoming push receiver',
            status=501,
            content_type='text/plain; charset=utf-8',
        )

    @http.route('/markket/push/outgoing', type='json', auth='user', methods=['POST'], csrf=False)
    def push_to_markket(self, store_slug=None, payload=None, content_type='application/json', **kwargs):
        return {
            'ok': False,
            'error': 'not_implemented',
            'store_slug': store_slug,
            'content_type': content_type,
        }

    @http.route('/markket/api-keys/save', type='json', auth='user', methods=['POST'], csrf=False)
    def save_api_key(self, name=None, api_key=None, owner_user_id=None, **kwargs):
        return {
            'ok': False,
            'error': 'not_implemented',
            'name': name,
            'owner_user_id': owner_user_id,
            'api_key_supplied': bool(api_key),
        }

    def is_valid_webhook(self, payload=None, signature=None, timestamp=None, secret=None):
        raise NotImplementedError('Webhook signature validation is not implemented yet.')
