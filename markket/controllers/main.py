from odoo import http
from odoo.http import Response


class MarkketController(http.Controller):

    @http.route('/markket/health', type='http', auth='public', methods=['GET'], csrf=False)
    def markket_health(self, **kwargs):
        return Response('markket:ok', status=200, content_type='text/plain; charset=utf-8')
