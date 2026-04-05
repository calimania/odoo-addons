SendGrid Inbound Webhook
========================

Webhook receiver for SendGrid Inbound Parse. Routes incoming emails through Odoo's mail gateway for proper alias routing, partner matching, and thread handling.

Installation
------------

::

    docker compose exec odoo odoo -d odoo -i sendgrid_inbound --stop-after-init --db_host=db

Configuration
-------------

Set environment variable::

    SENDGRID_INBOUND_SECRET=your-secret-here

Then configure SendGrid Inbound Parse to POST to::

    https://yourdomain.com/mail/sendgrid/inbound?token=YOUR_SECRET

Usage
-----

- View logs: Menu → SendGrid Inbound → Inbound Emails
- Create mail aliases to auto-route emails to models
- Fallback messages stored when no alias matches

For detailed instructions, see README.md
