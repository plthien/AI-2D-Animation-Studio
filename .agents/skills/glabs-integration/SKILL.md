---
name: glabs-integration
description: Port and adapt G-Labs webhook client while keeping explicit paid-task fencing, asset versioning and media QC for P3.
---

# Skill — glabs-integration

## References

`MASTER_SPEC.md` §7, §3.4, Appendix A P3; source `app/modules/media/glabs_webhook_client.py` and permitted shared durable media components.

## Procedure

1. Keep provider base endpoint, request status/result parsing from pinned YTB; extend image purposes to character master, parts atlas, background and props using own `generation_request.v1`.
2. Every paid task requires explicit user confirmation and persisted owner/task identity. Submit once; do not auto-repeat ambiguous POST, even on timeout or process restart.
3. Poll/recover durable state with fencing; all external network and download I/O outside SQLite write transactions. Server-only secrets and strict loopback CORS.
4. Validate real bytes/MIME/decoded image pixels, dimensions, alpha and hash; store approved immutable variants; never substitute a generated image for an unapproved asset.
5. Test mock successes/restarts/errors, malicious MIME/path/URL, repeated confirmation, race between poll and cancel, provider results without matching ownership.

## Acceptance

A live G-Labs authenticated Windows request is a separate **required later acceptance**; mocked CI is insufficient proof of provider readiness.


## Mandatory animation-first v1.2 amendment

For character_parts_atlas/expression_sheet generation, enforce an existing source reference artifact ID and same character lineage. Reference and parts atlas must be independently reviewed; paid G-Labs submission still requires explicit approval.
