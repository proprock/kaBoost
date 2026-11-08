## Rust tooling

- Use the toolchain the project selects (`rust-toolchain.toml`, `rust-version`); do not install or switch toolchains or cargo tools globally without agreement.
- Check in this order: `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo test --workspace`. Add `--locked` when `Cargo.lock` is committed, and commit it for binaries.
- Wrap `unsafe` in safe interfaces and give each `unsafe` block a `// SAFETY:` comment that states the invariant.
- Do not `unwrap` or `expect` on external input or fallible system calls in production code; return errors with context.
