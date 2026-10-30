---
name: kaboost-release-review
description: Review a release candidate end to end before tagging.
---
# Release review

Check, and report evidence for each point:

- The version is consistent everywhere (run the project's version check when it has one) and the changelog covers the user-observable changes since the last release.
- The diff since the last tag contains nothing unrelated to the release.
- CI is green on the release commit, and the distribution builds and installs.
- Migration, compatibility, and rollback notes exist for anything users must act on.
- The tag will be made on the merge commit on the main branch.

End with ready or not ready and the blocking items.
