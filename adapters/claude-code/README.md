# Claude Code adapter

`plugin.json` is the maintained metadata template. `scripts/build.py` copies canonical content to the committed package. Skills contain no runtime scripts; the one bundled script is the init engine (`init/kaboost_init.py`, standard library only), which runs only when you invoke `/kaboost:init`. Core rules and the adaptive workflow are shipped as readable references; installing them does not make them always active.

Review/import the core explicitly as described in the root README. Native skill names are namespaced by plugin. Automatic selection is model-dependent; explicit invocation remains available.

Local lifecycle check: `python3 scripts/smoke_claude.py`. It sets CLAUDE_CONFIG_DIR to a temporary profile, seeds a settings sentinel, registers a private fixture marketplace, installs twice, updates a fixture version, uninstalls, rolls back, and removes the catalog. It does not change your real Claude settings or call a model. It tests local paths; it does not prove Git transport, offline behavior, authentication, global rule loading, or model effectiveness.

For a release change, uninstall the plugin and remove the old catalog before registering the new pinned tag. This avoids ambiguous duplicate marketplace identities. Removing the marketplace may remove its sourced plugins. Keep local overrides outside the cache and restart after updates. Installation and core-import checkout must be versioned together by the operator.

See the [migration and conflict procedure](../../docs/migration.md) before changing versions or local overrides.
