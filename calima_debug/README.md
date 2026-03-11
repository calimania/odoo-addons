# calima_debug

A diagnostic Odoo addon for the [calimania/odoo-addons](https://github.com/calimania/odoo-addons) repository.

Install this module to instantly confirm your Odoo environment is healthy and
to get a quick overview of your server configuration — without deploying any
of the more complex Calimania modules.

---

## Features

### System Info dashboard

**Calima Debug → System Info** opens a read-only popup with:

| Field | What it tells you |
|---|---|
| Odoo Version | Exact release running |
| Python Version | Interpreter version |
| OS Info | Operating system & architecture |
| Database Name | Censored (first 3 chars + `***`) |
| Base URL | Configured `web.base.url` parameter |
| Server Timezone | `web.server.timezone` parameter |
| Installed Modules | Count of all installed addons |
| Addon Paths | Every directory Odoo scans for addons |

All fields are read-only — no data is stored in the database.

### Test Records

**Calima Debug → Test Records** lets you create and delete simple records to
confirm the ORM and database write layer work end-to-end.

---

## Installation

### Odoo.sh

1. Add this repository as a *linked repository* in your Odoo.sh project.
2. Enable **Developer Mode** (Settings → Activate Developer Mode).
3. Go to **Apps**, click **Update Apps List**.
4. Search for `Calima Debug` and click **Install**.

### On-premise / Docker

1. Mount / copy this repository so that the `calima_debug` folder is on
   your `addons_path`.
2. Restart Odoo and update the apps list as above.

---

## Post-install validation checklist

| Step | What it confirms |
|---|---|
| Module installs without error | Addon path, Python imports, DB migrations |
| "Calima Debug" menu appears | Views and menus load correctly |
| System Info screen opens | Wizard model and computed fields work |
| Test record can be created | ORM and DB write layer work |

---

## Compatibility

| Odoo version | Status |
|---|---|
| 17.0 | ✅ Supported |
| 16.0 | Should work (update `version` prefix in `__manifest__.py` to `16.0`) |

## License

LGPL-3 — see the root [LICENSE](../LICENSE) file.
