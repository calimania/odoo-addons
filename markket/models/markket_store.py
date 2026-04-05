import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from odoo import api, fields, models
from odoo.exceptions import UserError


class MarkketStore(models.Model):
    _name = 'markket.store'
    _description = 'Markket Store'
    _order = 'id desc'

    name = fields.Char(required=True)
    store_slug = fields.Char(required=True, index=True)
    owner_user_id = fields.Many2one('res.users', required=True, default=lambda self: self.env.user, index=True)
    active = fields.Boolean(default=True)
    description = fields.Text()

    markket_id = fields.Integer(index=True)
    markket_document_id = fields.Char(index=True)
    locale = fields.Char()
    stripe_customer_id = fields.Char()
    uuid = fields.Char()
    markket_created_at = fields.Datetime()
    markket_updated_at = fields.Datetime()
    published_at = fields.Datetime()

    last_sync_at = fields.Datetime(readonly=True)
    last_sync_status = fields.Selection(
        [('never', 'Never'), ('success', 'Success'), ('error', 'Error')],
        default='never',
        readonly=True,
    )
    last_sync_message = fields.Text(readonly=True)
    raw_payload = fields.Text(readonly=True)
    url_ids = fields.One2many('markket.store.url', 'store_id', string='Store URLs')

    _sql_constraints = [
        (
            'markket_store_slug_owner_uniq',
            'unique(store_slug, owner_user_id)',
            'Each user can only have one store record per slug.',
        )
    ]

    @api.model
    def _parse_iso_datetime(self, value):
        if not value:
            return False
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        except ValueError:
            return False

    @api.model
    def _fetch_store_payload(self, slug):
        query = urlencode({'filters[slug]': slug, 'populate[]': 'URLS'})
        url = f'https://api.markket.place/api/stores?{query}'
        request = Request(url, headers={'Accept': 'application/json'})

        with urlopen(request, timeout=15) as response:
            body = response.read().decode('utf-8')

        payload = json.loads(body or '{}')
        data = payload.get('data') or []
        if not data:
            raise UserError(f'No Markket store found for slug: {slug}')
        return data[0]

    @api.model
    def sync_store_from_public_api(self, slug, owner_user_id=False):
        if not slug:
            raise UserError('Store slug is required.')

        payload = self._fetch_store_payload(slug)
        attrs = payload if isinstance(payload, dict) else {}
        urls = attrs.get('URLS') or []

        owner_id = owner_user_id or self.env.user.id
        now = fields.Datetime.now()

        values = {
            'name': attrs.get('title') or slug,
            'store_slug': attrs.get('slug') or slug,
            'owner_user_id': owner_id,
            'active': bool(attrs.get('active', True)),
            'description': attrs.get('Description') or attrs.get('description') or False,
            'markket_id': attrs.get('id') or 0,
            'markket_document_id': attrs.get('documentId') or False,
            'locale': attrs.get('locale') or False,
            'stripe_customer_id': attrs.get('STRIPE_CUSTOMER_ID') or False,
            'uuid': attrs.get('uuid') or False,
            'markket_created_at': self._parse_iso_datetime(attrs.get('createdAt')),
            'markket_updated_at': self._parse_iso_datetime(attrs.get('updatedAt')),
            'published_at': self._parse_iso_datetime(attrs.get('publishedAt')),
            'last_sync_at': now,
            'last_sync_status': 'success',
            'last_sync_message': 'Synchronized from Markket public API.',
            'raw_payload': json.dumps(attrs, ensure_ascii=True, indent=2),
        }

        record = self.search(
            [('store_slug', '=', values['store_slug']), ('owner_user_id', '=', owner_id)],
            limit=1,
        )
        if record:
            record.write(values)
        else:
            record = self.create(values)

        url_commands = [(5, 0, 0)]
        for item in urls:
            item_data = item if isinstance(item, dict) else {}
            url_commands.append((0, 0, {
                'markket_url_id': item_data.get('id') or 0,
                'label': item_data.get('Label') or item_data.get('label') or 'Link',
                'url': item_data.get('URL') or item_data.get('url') or '',
                'active': True,
            }))

        record.write({'url_ids': url_commands})

        return record

    def action_sync_from_public_api(self):
        for record in self:
            record.sync_store_from_public_api(record.store_slug, owner_user_id=record.owner_user_id.id)
        return True
