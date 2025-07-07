# Agency Configuration (`agencii_config.json`)

## Top-level fields

### `name` (string)
Display name for the agency.
Default: agency folder name.

### `logo_url` (string)
Optional URL to display a logo in dashboards.

### `description` (string)
Short summary for humans.

### `version` (string)
Version of this configuration (`semver` recommended).
Default: `"1.0.0"`.

### `auto_deploy` (boolean)
If `true`, the agent will deploy automatically on repo push.
Default: `true`.

### `first_run` (boolean)
Used internally to detect first launch. Can be omitted by users.
Default: `true`.
---

## `github_integration` (object)

### `enabled` (boolean)
Whether to sync this repo with a GitHub App.
Default: `true`.

### `main_branch` (string)
Which branch triggers deploys. Usually `"main"` or `"master"`.
Default: `"main"`.

---

## `deployment_settings` (object)

### `lifecycle_timeout` (int)
Total seconds an agent is allowed to stay alive. Use 0 for no timeout.
Default: `300`.

### `memory_limit` (string)
Maximum memory usage (e.g. `MiB`: `"1024"`, `"512"`). Use valid memory values: any even value between 128 MiB and 8192 MiB.
Default: `"512"`.

### `cpu_limit` (string)
CPU allocation (`"1"` = 1 core, `"0.5"` = half core, available cores are from 0.5 to 8).
Default: `"1"`.