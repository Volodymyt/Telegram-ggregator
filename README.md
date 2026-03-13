# Telegram-ggregator

Telegram-ggregator is a Python service repository in its initial setup stage.

Project knowledge, planning documents, and role definitions live under [docs/README.md](docs/README.md).

## Codex Role Wrapper

Use `bin/codex-role` to launch Codex with a repository role from `docs/roles`.

```bash
bin/codex-role tech-lead
bin/codex-role engineer fix parser bug
bin/codex-role product-owner refine backlog -- --model gpt-5.4
```

The wrapper always runs Codex with the repository root as `-C` and injects an initial prompt that points Codex to the selected role document.

Role-specific aliases are also available as thin wrappers around `bin/codex-role`.

```bash
bin/codex-tech-lead "plan refactor"
bin/codex-engineer fix parser bug -- --model gpt-5.4
bin/codex-product-owner refine backlog
```

For team-wide convenience, add the repository `bin/` directory to `PATH` in your shell setup.

```bash
export PATH="/path/to/Telegram-ggregator/bin:$PATH"
```
