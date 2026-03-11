{
    'name': 'Calima Odoo Test',
    'version': '17.0.1.0.0',
    'summary': 'Minimal placeholder addon to verify Odoo installation and addon loading.',
    'description': """
Calima Odoo Test
================

A lightweight placeholder addon for Calimania's odoo-addons repository.

Use this module to:

* Confirm that Odoo can discover and install addons from this repository.
* Verify that your Odoo.sh or on-premise environment loads custom modules correctly
  before deploying more complex addons.
* Debug installation issues in isolation — if this module installs successfully,
  your addon path and Python environment are correctly configured.

After installation a **Calima Test** menu entry will appear in the Apps menu.
You can create simple test records to confirm the database layer is working.
    """,
    'author': 'Calimania',
    'website': 'https://github.com/calimania/odoo-addons',
    'category': 'Technical',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/calima_test_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
