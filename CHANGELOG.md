# Changelog

## Unreleased

- Correct the README's pre-publication status notes: this repository and its v0.1.0 release were published on 2026-10-25, and the cross-linked repositories are published with green CI.
- Add a subprocess CLI regression test for a negative stale threshold (`--days -1` exits 2 with a clean error and no traceback).

## v0.1.0 - prepared on 2026-10-24

- Add frozen-brief, source-review, and on-disk acceptance protocols and four templates.
- Build numbered decision packages and stale-goal reports from a flat Markdown folder.
- Include three synthetic goals, boundary cases, and generated labeled reports.
- Preserve nested evidence headings after a reproduced decision-loss regression.
- Keep tracked text at LF so regenerated samples stay clean with Windows Git defaults.
- Verify 53 pytest cases locally and configure one Ubuntu / Python 3.11 CI job.

The GitHub release is planned for 2026-10-27 and has not yet been published.
The parser implements a small documented format; it is not a general Markdown
or YAML engine. Reports collect requests and dates; they do not grant acceptance
or establish operational effectiveness. Hosted CI results remain pending.
