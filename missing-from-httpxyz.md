# Commits in httpxyz / httpcorexyz missing from httpx2

Survey of substantive, portable commits in the published forks at
`/home/michiel/py/httpxyz` and `/home/michiel/py/httpcorexyz` (released
on Codeberg and PyPI) that are **not** yet in `pydantic/httpx2` and
**not** covered by an open PR there.

Context: httpxyz was started to break the upstream `httpx` impasse —
merging pending PRs, improving perf, splitting httpcore. Pydantic
subsequently announced httpx2, and the httpxyz maintainers are not
competing — the goal here is to feed the useful work forward into
httpx2 rather than maintain a parallel fork. See
<https://tildeweb.nl/~michiel/httpx2.html>.

Open PRs already covering ports were checked via `gh pr list --repo
pydantic/httpx2 --state open` on 2026-06-02, and re-checked on
2026-07-14 — several items have since merged, one PR closed unmerged
(superseded by an upstream fix), and a couple of remaining gaps have
since grown their own open PRs.

Fork-only plumbing (image branding, `sys.modules` aliasing, Forgejo CI,
release bumps, docs about the fork itself, codespell typo CI, the
`httpx-alias` plugin etc.) is intentionally **excluded** — that work is
not relevant to httpx2.

## httpxyz → httpx2

### Features worth considering

| Fork commit | Title | Notes |
|---|---|---|
| `6866277` | Add `keep_method_for_redirects` option to Client / AsyncClient | Verified still missing — no reference anywhere in `src/httpx2`. Opt-in to preserve method on 301/302 (303 unaffected). Port of encode/httpx#3783 (Takashi Kajinami). |
| `34e7bbe` | Support pickling `HTTPStatusError` | Verified still missing — `_exceptions.py`'s `HTTPStatusError` has no `__reduce__`. Camillo Lugaresi's patch adds roundtrip-through-pickle support. |

### Docs worth pulling in

| Fork commit | Title | Notes |
|---|---|---|
| `f672124` | Document that `AsyncClient()` blocks the event loop during SSL init | Verified still missing. Adds a docstring note + workaround (`asyncio.to_thread`). Related to encode/httpx#3707 discussion. |

### Skipped — already in httpx2 / already in an open PR / fork-only

- `3573282` (ensure mounted transports are closed even if main transport raises) → opened as **PR #1070** ("Ensure mounted transports are closed even if main transport raises", 2026-07-15). Wraps `close()`/`__exit__`/`aclose()`/`__aexit__` cleanup in try/finally so mounted proxy transports are still closed if the main transport raises. Port of encode/httpx#3769; commit authored as Kadir Can Ozden, the original fix's author.
- `bd45506` (fix `unquote` index error on empty string) → **already in httpx2**, and had been for a while: merged 2026-06-04 as **PR #1023** ("Parse empty Digest auth realm without crashing"), authored by the repo owner with Jeroen van Zundert as co-author. `_auth.py:228` already uses `value.strip('"')` and the `unquote()` helper is gone from `_utils.py`. This survey's earlier claim that it was "still missing" was stale.
- `70d302c` (add RFC 9110 status code texts) → opened as **PR #1069** ("Add RFC 9110 status code constants", 2026-07-15). Renames `REQUEST_ENTITY_TOO_LARGE`→`CONTENT_TOO_LARGE` (413), `REQUEST_URI_TOO_LONG`→`URI_TOO_LONG` (414), `REQUESTED_RANGE_NOT_SATISFIABLE`→`RANGE_NOT_SATISFIABLE` (416), `UNPROCESSABLE_ENTITY`→`UNPROCESSABLE_CONTENT` (422); old names kept as aliases.
- `36420a4` (fix `InvalidURL` raised on malformed Location header when `follow_redirects=False`) → now has **open PR #1064** ("Preserve the response when a redirect has an invalid Location and redirects are not followed", opened 2026-07-14). Confirmed still missing in `_client.py` (`_build_redirect_request` at line 951 is still called unconditionally before the `follow_redirects` check at line 954) and the PR's description matches the fork fix exactly.
- `e0030ea` (add real async iterator for ByteStreams) → now has **open PR #1036** ("Add real async iterator for ByteStreams", akx, opened 2026-06-16). `_content.py:38` still uses an `async def __aiter__` generator, so the fix is still needed; the PR is a verbatim port of encode/httpx#3777 (Aarni Koskela), matching the fork commit.
- `091af7358` (httpx2) covers the same SSL-cert-with-verify-str case as `094bf04` in httpxyz.
- `599523b` + `0598ab0` (Sander's per-label IDNA decode) → **not** via PR #979 (that PR was closed *unmerged* on 2026-06-04 — the maintainer deferred to the fix landing in the `idna` package itself: kjd/idna@1a5bf80). It shipped instead via **PR #1018** ("Decode IDNA labels in non-leading host positions"), merged 2026-06-04. Already in httpx2.
- `a9e7541` (no_proxy IPv6 CIDR + IPNetPattern) → split across two PRs: **#967** ("Allow IPv6 CIDR notation in `no_proxy`") merged 2026-06-12; **#969** ("Add IPNetPattern for accurate CIDR proxy/mount matching") still open.
- `417d6c6` (params don't overwrite baseurl) → still open as **PR #966**.
- `1756dbb` (elapsed time on stream wrapper) → already merged as `de30f399` in httpx2.
- `04d7191` (tests on random port) → already merged as `999da321` (#994).
- `52fb1ab` (zstd decompressobj reuse) → already merged as `ae5995f7` in httpx2.
- `9bab7e8` (Python 3.14 support) → already in via `0ba70abc` and friends.
- `f4a1f64` (lazy `_main` import) → already in httpx2 (see `__init__.py:93` `__getattr__`).
- `97bc190` (codespell typos) → broadly covered by httpx2's `60c8262b`.
- `990205d` (`| None` on `auth` annotation) → trivial, unlikely to be missing; not verified line-by-line.
- `261beea` (CLI default scheme https) — fork-only convenience, but could be argued for httpx2 too; flagging as borderline.
- `f60e98d`, `3d23ea7`, `8b3a686`, `b8ae1b9`, `86b8484`, `87499f0`, `b6df770`, `2ee49f5`, `8bc5289`, `1f631d3`, `1a6e416`, `e9ba4af`, `7e0de8a` etc. — fork-only (sys.modules aliasing, docs about the fork, CI, branding, releases). Not portable.

## httpcorexyz → httpx2 (`src/httpcore2`)

### Bug fixes worth porting

| Fork commit | Title | Notes |
|---|---|---|
| `9d86b44` | Reduce lock contention in `PoolByteStream.close()` | Verified still missing — `connection_pool.py:402` still does `self._pool._requests.remove(self._pool_request)` inside `self._pool._optional_thread_lock`, and `Origin` in `_models.py` still has no `__hash__`. Port of encode/httpcore#1038. |

### Refactor worth considering

| Fork commit | Title | Notes |
|---|---|---|
| — | — | (see Skipped below — the one refactor item tracked here now has an open PR) |

### Skipped — already in httpx2 / open PR / fork-only

- `c4e9340` (explicitly close async generators to prevent Trio warnings) → **already in httpx2**. `safe_async_iterate()` / `safe_iterate()` are present in `_utils.py` and used across `connection_pool.py`, `http2.py`, `_models.py`. `git log -S` shows this landed all the way back at the `httpcore` → `httpcore2` rename (`ce6ebe2b`, #138) — i.e. httpx2 already had equivalent handling before this survey started, not a port of the fork commit specifically.
- `91ad8ea` (retire `map_exceptions` in favour of plain try/except, #1044) → now has **open PR #1038** ("Speed up exception handling", akx, opened 2026-06-16). `map_exceptions` is still live in `httpcore2/_exceptions.py`, `_synchronization.py`, `_backends/{anyio,sync,trio}.py`, `_async(/_sync)/http11.py`, confirming the gap; PR #1038 reports a ~9% microbenchmark win from the same change.
- `e88f30b` (h2 semaphore release on `NoAvailableStreamIDError`) → **merged** as PR #1012 (port of encode/httpcore#1061).
- `e88f30b` (h2 stream-events race in `_response_closed`) → **merged** as PR #1013 (port of encode/httpcore#1062). Note: fork bundled both #1061 and #1062 in this one commit; split into two httpx2 PRs to match the upstream split.
- `b192486` (close proxy connection when tunnel TLS handshake fails) → still open as **PR #1010**.
- `0387930` (propagate timeout through SOCKS5 handshake) → **merged** as PR #1009.
- `3058e2d` (RLock instead of Lock to prevent thread deadlock) → **merged** as PR #1008.
- `d3db03d` + `237ac4d` (FQDN trailing-dot SNI fix + `Origin.normalized_host`) → still open as **PR #1007**.
- `a7500e4` (pool poisoning on cancellation, `is_connected()`) → **merged** as PR #983 (2026-07-14).
- `199129e` (memoryview write) → already merged as `79f788b7` (#954) in httpx2.
- `079768d` (connection_pool O(N²) + bugs) → already merged as `8027999f` (#974) in httpx2 — though confirm both bug fixes from the fork's commit are included, not just the perf rewrite.
- `4a4eb1e` (anyio fast_acquire) → already merged as `b4c59404` (#970) in httpx2.
- `bdaf7f8`, `32e5f5b`, `1ec6c7a`, `f364bfe`, `1d67bd6` and the housekeeping `fix: install httpcore in test env` series — fork-only (typing back-port for old Python, the fork itself, sys.modules aliasing, CI plumbing). Not portable.

## Suggested next steps

Genuinely unaddressed, with no open PR as of 2026-07-14:

1. `9d86b44` (lock contention in `PoolByteStream.close()` + `Origin.__hash__`) — perf-shaped, requires care.
2. `6866277` (`keep_method_for_redirects`) is a public-API addition — worth opening as a discussion before a PR.
3. `34e7bbe` (pickling `HTTPStatusError`) — small, additive.
4. `f672124` (docs: `AsyncClient()` blocks the event loop during SSL init) — docs-only.

Already in progress (open PRs, not yet merged): `b192486` → PR #1010 (CONNECT tunnel TLS close), `d3db03d`+`237ac4d` → PR #1007 (FQDN trailing-dot SNI), `36420a4` → PR #1064 (redirect response preserved on invalid Location), `e0030ea` → PR #1036 (real async iterator for ByteStreams), `91ad8ea` → PR #1038 (retire `map_exceptions`), `a9e7541`(part) → PR #969 (IPNetPattern), `417d6c6` → PR #966 (params vs baseurl), `70d302c` → PR #1069 (RFC 9110 status code constants), `3573282` → PR #1070 (mounted transports closed on raise).

Landed since the last survey (2026-06-02 → 2026-07-14): `3058e2d` → PR #1008 (RLock), `0387930` → PR #1009 (SOCKS5 timeout), `e88f30b` → PR #1012 + PR #1013 (h2 fixes), `a7500e4` → PR #983 (pool poisoning on cancellation), `a9e7541`(part) → PR #967 (IPv6 CIDR in `no_proxy`), `599523b`+`0598ab0` → PR #1018 (IDNA decode, via upstream `idna` fix rather than PR #979 which closed unmerged).
