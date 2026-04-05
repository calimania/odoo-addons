{
    'name': 'Markket',
    'version': '19.0.1.3.37',
    'summary': 'Markkkët integration',
    'description': """
Markkët
=======

Initial placeholder module for the Markket ecommerce marketplace solution

This first edition includes:
- A basic data model for marketplace listings
- A minimal controller endpoint for store sync
- Starter menu, list, and form views

Future releases can extend this with synchronization to operational Odoo flows.
    """,
    'author': 'Calimania',
    'website': 'https://github.com/calimania/odoo-addons',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/markket_store_views.xml',
        'views/markket_store_url_views.xml',
        'views/markket_api_key_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
