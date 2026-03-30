{
    'name': 'SendGrid Inbound Webhook',
    # // 19.0.A.B.C ( 19 Odoo ) ( 0 means no breaking changes ) ( feature, bugfix, minor)
    'version': '19.0.1.1.1',
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
        'version': '19.0.1.0.0',
}
