# Agency Configuration (`agencii_config.json`)

## Top-level fields

### `name` (string)
Display name for the agency.
Default: agency folder name.

### `description` (string)
Short summary for humans.

### `version` (string)
Version of this configuration (`semver` recommended).
Default: `"1.0.0"`.

### `auto_deploy` (boolean)
If `true`, the agent will deploy automatically on repo push.
Default: `true`.

### `deployment_settings` (object)

### `lifecycle_timeout` (int)
Total seconds an agent is allowed to stay alive. Use 0 for no timeout.
Default: `300`.

### `memory_limit` (string)
Maximum memory usage (e.g. `MiB`: `"1024"`, `"512"`). Use valid memory values: any even value between 128 MiB and 8192 MiB.
Default: `"512"`.

### `cpu_limit` (string)
CPU allocation (`"1"` = 1 core, `"0.5"` = half core, available cores are from 0.5 to 8).
Default: `"1"`.

### `app_token_env` (string)
Environment variable name for the app token used for agency fastapi.
Default: `""`.