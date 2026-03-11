# calima_odoo_test

A minimal placeholder Odoo addon for the [calimania/odoo-addons](https://github.com/calimania/odoo-addons) repository.

## Purpose

Use this module to verify that your Odoo environment can discover and install
custom addons from this repository **before** deploying more complex modules.

If this module installs successfully:

- Odoo can find the repository addon path ✅
- Python can import the addon package ✅
- Database migrations run without errors ✅
- Views and menus load correctly ✅

## What it does

Registers a single model (`calima.test`) with three fields (`name`, `description`, `active`)
and exposes a **Calima Test** top-level menu where you can create test records.

## Installation

### Odoo.sh

1. Add this repository as a *linked repository* in your Odoo.sh project.
2. Go to **Settings → Technical → Activate Developer Mode**.
3. Go to **Apps**, click **Update Apps List**.
4. Search for `Calima Odoo Test` and click **Install**.

### On-premise / Docker

1. Mount / copy this repository so that the `calima_odoo_test` folder is on
   your `addons_path`.
2. Restart Odoo and update the apps list as described above.

## Compatibility

| Odoo version | Status |
|---|---|
| 17.0 | ✅ Supported |
| 16.0 | Should work (change `version` prefix in `__manifest__.py` to `16.0`) |

## License

LGPL-3 — see the root [LICENSE](../LICENSE) file.
