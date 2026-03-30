{
    'name': 'SendGrid Inbound Webhook',
    'version': '1.0.0',
    'summary': 'Receive SendGrid Inbound Parse and create mail messages',
    'description': 'Webhook receiver for SendGrid Inbound Parse. Routes incoming emails through Odoo\'s mail gateway for proper alias routing, partner matching, and thread handling.',
    'author': 'Calimania',
    'website': 'https://github.com/calimania/odoo-addons',
    'license': 'LGPL-3',
    'depends': ['mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/inbound_log_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
}
