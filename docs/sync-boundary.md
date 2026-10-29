# Toolkit and User Environment Sync

Distribution delivers a package. Configuration enables it and chooses local settings. Synchronization reconciles desired state across machines. These are separate responsibilities.

| AI Development Toolkit | Separate User Environment Sync |
| --- | --- |
| Engineering content, skills, workflow references | Dotfiles, shell, Git and editor settings |
| Release versions and native package metadata | Machine paths, bootstrap, OS differences |
| Installation/removal documentation and compatibility evidence | AI global settings and MCP configuration |
| Safe examples of explicit configuration | Secrets retrieval policy and workstation reconciliation |

Marketplace installation does not synchronize credentials, history, caches, OS settings, or local modifications. It does not make incompatible client extensions portable. Neither project should commit secrets.

Toolkit works independently in a temporary clone, CI, devcontainer, or cloud workspace. Consumers need only a reviewed release and client installation. The future environment project consumes client + toolkit version/source + chosen components and configures local imports; toolkit never depends on it.

Do not start a second repository until machine reconciliation is needed. Then evaluate chezmoi, yadm, GNU Stow, and Ansible against actual OS and secrets constraints. These are candidates, not a selected dependency. Move machine examples/configuration there while retaining package content and install documentation here. Do not build a universal sync engine.
