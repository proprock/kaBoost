## Code discovery

Use semantic code-graph tools first (symbol search, call tracing, code snippets), then symbol-aware editing tools where available, then text search (`rg`) for string literals, configuration, and documentation. Do not read whole files once the relevant symbol is known. Check that a graph index exists and is fresh before indexing; if indexing fails once, fall back to text search rather than retrying unchanged.
