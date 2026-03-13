{
    'name': 'Calima Debug',
    'version': '19.0.1.0.0',
    'summary': 'System information dashboard and installation validator for self-hosting administrators.',
    'description': """
Calima Debug
============

A lightweight diagnostic addon for Calimania's odoo-addons repository.

**System Information Dashboard**

Opens a read-only dashboard (Calima Debug → System Info) showing:

* Odoo version
* Python version
* Database name (censored)
* Configured base URL
* Server timezone
* Number of installed modules
* Addon paths loaded by the server

**Installation Validator**

A simple writable model (Calima Debug → Test Records) lets you
create and delete records to confirm the ORM and database write layer work.

If this module installs successfully and the System Info screen loads,
your Odoo environment is correctly configured to run custom addons.
    """,
    'author': 'Calimania',
    'website': 'https://github.com/calimania/odoo-addons',
    'category': 'Technical',
    'license': 'LGPL-3',
    'depends': ['base', 'website', 'website_event'],
    'data': [
        'security/ir.model.access.csv',
        'views/calima_debug_info_views.xml',
        'views/calima_debug_json_views.xml',
        'views/calima_test_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
