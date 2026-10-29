# Codex delivery research

Reviewed 2026-10-29. These are documentation and local CLI observations, not
evidence that this toolkit has been installed or behaves correctly in Codex.

| Surface | Documented delivery or activation | Limits for this project |
| --- | --- | --- |
| Codex CLI | Local skills are discovered from repo `.agents/skills` and user `~/.agents/skills`; `/skills` or `$` can explicitly select skills. Plugins and marketplace sources are also supported. | The installed Linux CLI is `0.165.0`; its `plugin add` and `plugin marketplace add` help describe local and Git sources and `--ref`. No toolkit adapter or lifecycle has been tested. |
| Codex IDE extension | OpenAI documents `/skills` or `$` for explicit skill invocation, and local or cloud work from the editor. | Do not assume local marketplace management or plugin behavior is identical across VS Code, Xcode, and JetBrains integrations without testing each surface. |
| Codex in ChatGPT desktop | OpenAI documents repo and personal local marketplaces, a plugin directory UI, and per-project enablement in trusted projects. | A local desktop marketplace is not proof that this toolkit is installed or active in the user's desktop client. |
| Remote distribution | OpenAI documents Git marketplace sources for the CLI, including a ref and optional sparse paths; the public plugin directory is shared across supported ChatGPT and Codex surfaces. | A source/ref option is not a verified install, immutable tag, or guarantee that every IDE and desktop surface supports identical remote workflows. No release is published by this project yet. |

Local Codex skills are progressively disclosed: metadata supports selection and
the full instructions are read when the skill is selected. Multiple skills with
the same name can both appear; a future adapter must test duplicate loading and
user/project instruction precedence. Core rules are not automatically active
merely because skills are available. This research does not select a packaging
mechanism for the adapter or claim any runtime support.

Sources: [OpenAI skill discovery and invocation](https://learn.chatgpt.com/docs/build-skills),
[plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins),
[IDE surfaces](https://learn.chatgpt.com/docs/ide), and
[CLI overview](https://learn.chatgpt.com/docs/cli). Local evidence: `codex
--version`, `codex plugin --help`, `codex plugin add --help`, and `codex plugin
marketplace add --help`, run without installing or modifying a plugin.
