## Release

- Change the version, the changelog entry and the release notes in the milestone pull request, not afterwards.
- Run `python scripts/kaboost_check_version.py` before tagging; it fails when `pyproject.toml` and the newest `CHANGELOG.md` heading disagree.
- Tag the merge commit on the main branch after the pull request is merged, and tag nothing else.
