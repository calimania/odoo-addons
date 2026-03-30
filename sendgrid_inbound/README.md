# SendGrid Inbound Webhook

Odoo addon that receives inbound emails from SendGrid Inbound Parse and routes them through Odoo's mail gateway for proper alias routing, partner matching, and thread handling.

## How it Works

1. SendGrid receives email at your MX domain (e.g., `example.com`).
2. SendGrid POSTs the raw MIME message to the webhook endpoint.
3. The addon validates the secret token.
4. The webhook passes the raw message to Odoo's `message_process()` which:
   - Matches the To: address against mail aliases.
   - Creates records on the target model (helpdesk ticket, lead, etc.).
   - Or stores as unrouted `mail.message` if no alias matches.
5. The endpoint returns HTTP 200 on success.

## Setup

### 1. Environment Variable

Set `SENDGRID_INBOUND_SECRET` in your `.env` or `docker-compose.yml`:

```bash
SENDGRID_INBOUND_SECRET=your-long-random-secret-here
```

### 2. SendGrid Inbound Parse Configuration

1. Go to https://app.sendgrid.com/settings/parse
2. Add a new Inbound Parse setting:
   - **Receiving Domain**: Your MX subdomain (e.g., `parse.yourdomain.com`)
   - **Destination URL**: `https://yourdomain.com/mail/sendgrid/inbound?token=YOUR_SECRET`
   - **Enable**: "POST the raw, full MIME message"
   - **Optional**: Check "Check incoming emails for spam"

### 3. DNS Setup

Add an MX record for your parse subdomain pointing to SendGrid:

```
parse.yourdomain.com  MX  10  mx.sendgrid.net
```

### 4. Install the Module

```bash
docker compose exec odoo odoo -d odoo -i sendgrid_inbound --stop-after-init --db_host=db
```

### 5. Configure Odoo Aliases (Optional but Recommended)

To route emails to specific models, create mail aliases:

1. Go to Settings → Technical → Email → Aliases
2. Create aliases like:
   - `support@yourdomain.com` → Helpdesk Ticket
   - `sales@yourdomain.com` → CRM Lead
   - `info@yourdomain.com` → Mail Channel

## Testing

```bash
# Test with sample EML file
curl -v -F "email=@erp-addons/sendgrid_inbound/sample.eml;type=message/rfc822" \
  -F "token=changeme" \
  http://localhost:8069/mail/sendgrid/inbound
```

## Logs

### UI
- Go to **SendGrid Inbound** → **Inbound Emails**
- View all received emails with status (processed/fallback/error)
- Open a record to see full details and attached raw message

### Server Logs

```bash
docker compose logs --no-color -f odoo | grep -i sendgrid
```

## Troubleshooting

- **404 on webhook**: Ensure URL is `/mail/sendgrid/inbound` (not `/sendgrid/inbound`)
- **Token mismatch (401)**: Verify `SENDGRID_INBOUND_SECRET` matches the token parameter
- **No route found**: Create a mail.alias for the destination email address
- **Fallback messages**: Stored when no matching alias exists; add alias to auto-route
- `SendGrid inbound: processed successfully` - Routed via mail gateway
- `SendGrid inbound: stored raw message as fallback` - No alias matched

## Security Notes

- **Token in URL**: SendGrid logs URLs, so consider this when choosing your secret
- **Alternative**: Use `X-Webhook-Token` header if your reverse proxy can inject it
- **Rate limiting**: Consider adding nginx `limit_req` for this endpoint
- **IP allowlist**: SendGrid IPs can be allowlisted (see SendGrid docs)

## Troubleshooting


 401 Unauthorized | Token mismatch - verify `SENDGRID_INBOUND_SECRET` in container |
 400 Missing email | SendGrid not sending raw MIME - check "POST raw" setting |
 Emails not routing | Create mail aliases in Odoo for your addresses |
 No records created | Check Odoo logs for `message_process` errors |

## Files

- `controllers.py` - Webhook endpoint and mail routing logic
- `__manifest__.py` - Module metadata
- `sample.eml` - Test email file for curl testing

