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
pydantic/httpx2 --state open` on 2026-06-01.

Fork-only plumbing (image branding, `sys.modules` aliasing, Forgejo CI,
release bumps, docs about the fork itself, codespell typo CI, the
`httpx-alias` plugin etc.) is intentionally **excluded** — that work is
not relevant to httpx2.

## httpxyz → httpx2

### Behavioural fixes worth porting

| Fork commit | Title | Notes |
|---|---|---|
| `36420a4` | Fix `InvalidURL` raised on malformed Location header when `follow_redirects=False` | Verified missing — `_client.py:951` still calls `_build_redirect_request` unconditionally before checking `follow_redirects`. Closes httpxyz #37; same shape as upstream encode/httpx issue. |
| `bd45506` | Fix `unquote` index error on empty string | Verified missing — `_utils.py:89` still has the old `unquote()`. Original upstream proposal: encode/httpx#3771, with akx's improved version. |
| `3573282` | Ensure mounted transports are closed even if main transport raises | `try/finally` around main-transport close so proxy mounts don't leak. Port of encode/httpx#3769 (Kadir Can Ozden). |
| `e0030ea` | Add real async iterator for ByteStreams | Verified missing — `_content.py:38` still uses an `async def __aiter__` generator. Triggers ResourceWarning under trio ≥0.31. Port of encode/httpx#3777 (Aarni Koskela). |

### Features worth considering

| Fork commit | Title | Notes |
|---|---|---|
| `6866277` | Add `keep_method_for_redirects` option to Client / AsyncClient | Verified missing — opt-in to preserve method on 301/302 (303 unaffected). Port of encode/httpx#3783 (Takashi Kajinami). |
| `70d302c` | Add RFC 9110 status code texts | Updated wording for status constants, old names kept as backwards-compat aliases. No equivalent in httpx2's `_status_codes.py`. |
| `34e7bbe` | Support pickling `HTTPStatusError` | Camillo Lugaresi's patch — adds `__reduce__`-style support so the exception roundtrips through pickle. Verified missing in `_exceptions.py`. |

### Docs worth pulling in

| Fork commit | Title | Notes |
|---|---|---|
| `f672124` | Document that `AsyncClient()` blocks the event loop during SSL init | Adds a docstring note + workaround (`asyncio.to_thread`). Related to encode/httpx#3707 discussion. |

### Skipped — already in httpx2 / already in an open PR / fork-only

- `091af7358` (httpx2) covers the same SSL-cert-with-verify-str case as `094bf04` in httpxyz.
- `599523b` + `0598ab0` (Sander's per-label IDNA decode) → covered by open PR #979.
- `a9e7541` (no_proxy IPv6 CIDR + IPNetPattern) → covered by open PRs #967 and #969.
- `417d6c6` (params don't overwrite baseurl) → covered by open PR #966.
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
| `3058e2d` | Use `RLock` instead of `Lock` to prevent thread deadlock | Verified missing — `_synchronization.py` still uses plain Lock. Port of encode/httpcore#1003 (Zenulous). Re-entrant acquire from the same thread currently deadlocks. |
| `0387930` | Propagate timeout through SOCKS5 handshake | Verified missing — `_init_socks5_connection()` in `httpcore2/_async/socks_proxy.py:42` takes no `timeout` arg. A non-responsive SOCKS5 proxy hangs forever regardless of the request timeout. Port of encode/httpcore#1055. |
| `b192486` | Close proxy connection when tunnel TLS handshake fails | CONNECT-tunnel TLS failure currently leaves the TCP connection ACTIVE in the pool until `max_connections` is exhausted. Port of encode/httpcore#1049 (baizhu). |
| `e88f30b` | Release h2 semaphore/streams on error + fix stream-events race | Two related deadlock/race fixes: release the max-streams semaphore on `NoAvailableStreamIDError`, and move `del self._events[stream_id]` inside `_state_lock`. Ports encode/httpcore#1061 and #1062. |
| `c4e9340` | Explicitly close async generators to prevent Trio warnings | Adds `safe_async_iterate()` / `safe_iterate()` context managers and applies them across `connection_pool.py`, `http11.py`, `http2.py`, `_models.py`. Port of encode/httpcore#1019 (Alex Grönholm). |
| `9d86b44` | Reduce lock contention in `PoolByteStream.close()` | Marks pool requests closed outside the lock, cleans up inside `_assign_requests_to_connections()`. Also adds `Origin.__hash__`. Port of encode/httpcore#1038. |

### Refactor worth considering

| Fork commit | Title | Notes |
|---|---|---|
| `91ad8ea` | Retire `map_exceptions` in favour of plain try/except (#1044) | Verified `map_exceptions` is still live in `httpcore2/_exceptions.py`, `_synchronization.py`, `_backends/{anyio,sync,trio}.py`. Justification: `@contextmanager` overhead on hot read/write paths. Larger diff (~120 lines net) — judgement call whether httpx2 wants it. |

### Skipped — already in httpx2 / open PR / fork-only

- `d3db03d` + `237ac4d` (FQDN trailing-dot SNI fix + `Origin.normalized_host`) → covered by open PR #1007.
- `a7500e4` (pool poisoning on cancellation, `is_connected()`) → covered by open PR #983.
- `199129e` (memoryview write) → already merged as `79f788b7` (#954) in httpx2.
- `079768d` (connection_pool O(N²) + bugs) → already merged as `8027999f` (#974) in httpx2 — though confirm both bug fixes from the fork's commit are included, not just the perf rewrite.
- `4a4eb1e` (anyio fast_acquire) → already merged as `b4c59404` (#970) in httpx2.
- `bdaf7f8`, `32e5f5b`, `1ec6c7a`, `f364bfe`, `1d67bd6` and the housekeeping `fix: install httpcore in test env` series — fork-only (typing back-port for old Python, the fork itself, sys.modules aliasing, CI plumbing). Not portable.

## Suggested next steps

1. The **httpcorexyz bug-fix block** (`3058e2d`, `0387930`, `b192486`, `e88f30b`, `c4e9340`) is the most valuable — each is an upstream-reviewed httpcore fix that httpx2 currently lacks, and each ports cleanly with `unasync.py` already in place.
2. The httpxyz **redirect/transport/stream fixes** (`36420a4`, `3573282`, `e0030ea`) are small, isolated, and have upstream PRs to cite.
3. `6866277` (`keep_method_for_redirects`) is a public-API addition — worth opening as a discussion before a PR if you're unsure whether the httpx2 maintainers want it.
4. `91ad8ea` (`map_exceptions` retirement) is bigger and more opinionated — open an issue/discussion first.
