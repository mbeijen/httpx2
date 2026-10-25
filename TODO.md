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

Checked against `pydantic/httpx2` on 2026-06-02, 2026-07-14 and
2026-10-25 (`upstream/main` at `2fc91585`, plus `gh pr list --state
open`). Source paths below are relative to `upstream/main`, which now
nests packages as `src/httpx2/httpx2/` and `src/httpcore2/httpcore2/`.

Fork-only plumbing (image branding, `sys.modules` aliasing, Forgejo CI,
release bumps, docs about the fork itself, codespell typo CI, the
`httpx-alias` plugin etc.) is intentionally **excluded** — that work is
not relevant to httpx2.

## Status at a glance (2026-10-25)

Not started, no PR anywhere:

1. `f672124` — docs: `AsyncClient()` blocks the event loop during SSL init. Still true, mechanism changed.
2. `6866277` — `keep_method_for_redirects`. Public API; discuss first.
3. `9d86b44` — lock contention in `PoolByteStream.close()`. Wait for #1169.

My open PRs that need attention:

- **#1010** (CONNECT tunnel TLS close) — **duplicated** by #1226 (itzzdev09, 2026-09-22, fixes issue #1175). Pick one; comment on both.
- **#1070** (mounted transports closed on raise) — **overlaps** Kludex's #1270 (`AsyncExitStack` in `AsyncClient`, 2026-10-18), which also keeps closing others when one raises, but async-only. Coordinate: rebase #1070 to sync-only on top of #1270, or close.
- **#1007** (trailing-dot SNI) — still open since 2026-06-01. Nearby work has moved: #1223 landed (TLS hostname override in proxy tunnels) and #1225 is open (match SNI overrides when reusing pooled connections). Rebase and check for conflicts.
- **#1172** (forward `uds` / `local_address` / `retries` to proxied connections) — not a fork port; open since 2026-08-29, no review yet.

Others' open PRs covering fork commits: #1064 (`36420a4`), #1036 (`e0030ea`), #1038 (`91ad8ea`), #1211 (`34e7bbe`), #966 + duplicate #1174 (`417d6c6`).

## httpxyz → httpx2

### Features worth considering

| Fork commit | Title | Notes |
|---|---|---|
| `6866277` | Add `keep_method_for_redirects` option to Client / AsyncClient | Verified still missing 2026-10-25 — no reference anywhere in `src/httpx2`, no issue or PR. Opt-in to preserve method on 301/302 (303 unaffected). Port of encode/httpx#3783 (Takashi Kajinami). |

### Docs worth pulling in

| Fork commit | Title | Notes |
|---|---|---|
| `f672124` | Document that `AsyncClient()` blocks the event loop during SSL init | Verified still missing. Still true, but for a different reason than in the fork: httpx2 switched from certifi to `truststore` (#1002), and since #1253 (2026-10-19) the default Linux context calls `load_verify_locations()` on the system CA bundle at construction (`httpcore2/_ssl.py`). macOS/Windows use `truststore.SSLContext` and are cheaper. The docstring note + `asyncio.to_thread` workaround needs rewording to match. Related to encode/httpx#3707. |

### Skipped — already in httpx2 / already in an open PR / fork-only

- `08cbebd` (SSL context dropped for HTTPS proxy from URL string) → **won't port.** Tried as **PR #1299** (2026-10-25), closed by me the same day. Giving an HTTPS proxy the transport's `verify=` context couples two separate trust domains: `verify=False` for an origin would silently disable verification of the proxy's certificate (security downgrade), and `verify=ctx` holding only a private CA would break a proxy with a publicly signed certificate. Current httpx2 behaviour (proxy uses the default context unless `Proxy(..., ssl_context=...)` is passed) is the safer one. The fork commit and encode/httpx#3506 only cover a URL string passed straight to the transport anyway; `Client` and env proxies were never affected by them. Possible follow-up: a docs-only PR for `docs/advanced/proxies.md` saying `verify=` applies to the origin only and showing `Proxy("https://…", ssl_context=ctx)` for a proxy behind a private CA (that's what httpxyz issue #6 needed). Note httpxyz itself still ships the coupled behaviour for `HTTPTransport(proxy="https://…", verify=…)`.
- `3573282` (ensure mounted transports are closed even if main transport raises) → open as **PR #1070** (mine, 2026-07-15). Port of encode/httpx#3769; commit authored as Kadir Can Ozden. Now overlaps **PR #1270** (Kludex, 2026-10-18), which unwinds `AsyncClient` transports with an `AsyncExitStack` so one raising no longer skips the others — async only; the sync `Client` is not touched by #1270.
- `36420a4` (fix `InvalidURL` raised on malformed Location header when `follow_redirects=False`) → still open as **PR #1064** (devl00p). Still needed: `_client.py:1051` / `:1890` still call `_build_redirect_request` before the `follow_redirects` check.
- `e0030ea` (add real async iterator for ByteStreams) → still open as **PR #1036** (akx). Still needed: `_content.py:34` is still an `async def __aiter__` generator. Related work landed (#1204, "Avoid nested async generator finalization errors") and is open (#1212, #1281, Kludex) but none of it touches `AsyncByteStream`/`_content.py`.
- `34e7bbe` (support pickling `HTTPStatusError`) → now covered by **PR #1211** (drusc0, 2026-09-15, "don't leak request/response payload when pickling HTTPError"). Different approach from the fork: it makes all `HTTPError`s picklable *and* redacts the request/response payload, fixing the keyword-only `__init__` crash as a side effect. Review that rather than port the fork patch.
- `417d6c6` (params don't overwrite baseurl) → still open as **PR #966** (KeeganOP), and now duplicated by **PR #1174** (ferstar, 2026-08-29, closes issue #1173).
- `70d302c` (add RFC 9110 status code texts) → **merged** as PR #1069 (2026-08-02). Marcelo followed up with #1135 ("Restore deprecated status code aliases", 2026-08-13).
- `a9e7541` (no_proxy IPv6 CIDR + IPNetPattern) → **done**. #967 merged 2026-06-12; #969 (IPNetPattern) closed unmerged 2026-10-18 in favour of **#1165** (turettn, "Support IP CIDR ranges in NO_PROXY", merged 2026-10-18), plus Marcelo's #1267 (bracketed IPv6 / skip unparseable `NO_PROXY` entries).
- `bd45506` (fix `unquote` index error on empty string) → already in httpx2 via **PR #1023** (merged 2026-06-04).
- `599523b` + `0598ab0` (Sander's per-label IDNA decode) → shipped via **PR #1018** (merged 2026-06-04); PR #979 closed unmerged in favour of the upstream `idna` fix (kjd/idna@1a5bf80).
- `091af7358` (httpx2) covers the same SSL-cert-with-verify-str case as `094bf04` in httpxyz.
- `1756dbb` (elapsed time on stream wrapper) → already merged as `de30f399` in httpx2.
- `04d7191` (tests on random port) → already merged as `999da321` (#994).
- `52fb1ab` (zstd decompressobj reuse) → already merged as `ae5995f7` in httpx2.
- `9bab7e8` (Python 3.14 support) → already in via `0ba70abc` and friends.
- `f4a1f64` (lazy `_main` import) → already in httpx2 (`__init__.py` `__getattr__`).
- `97bc190` (codespell typos) → broadly covered by httpx2's `60c8262b`.
- `990205d` (`| None` on `auth` annotation) → trivial, unlikely to be missing; not verified line-by-line.
- `261beea` (CLI default scheme https) — fork-only convenience, but could be argued for httpx2 too; flagging as borderline.
- `f60e98d`, `3d23ea7`, `8b3a686`, `b8ae1b9`, `86b8484`, `87499f0`, `b6df770`, `2ee49f5`, `8bc5289`, `1f631d3`, `1a6e416`, `e9ba4af`, `7e0de8a` etc. — fork-only (sys.modules aliasing, docs about the fork, CI, branding, releases). Not portable.

## httpcorexyz → httpx2 (`src/httpcore2`)

### Bug fixes worth porting

| Fork commit | Title | Notes |
|---|---|---|
| `9d86b44` | Reduce lock contention in `PoolByteStream.close()` | Verified still missing 2026-10-25 — `_async/connection_pool.py:436-437` still does `self._pool._requests.remove(self._pool_request)` inside `self._pool._optional_thread_lock`, and `Origin` in `_models.py` still has no `__hash__`. Port of encode/httpcore#1038. **Hold off:** Marcelo's open **#1169** ("Track connection pool state incrementally", 2026-08-27) rewrites this whole area (dict/deque state, origin-indexed idle connections); his earlier attempt #1076 landed and was reverted (#1197). Re-evaluate once #1169 settles. |

### Skipped — already in httpx2 / open PR / fork-only

- `b192486` (close proxy connection when tunnel TLS handshake fails) → still open as **PR #1010** (mine, 2026-06-02). **Duplicated** by **PR #1226** (itzzdev09, 2026-09-22, "Close the tunnel connection when TLS setup fails after CONNECT", fixes issue #1175) — same files, same fix. Comment on both and let the maintainer pick.
- `d3db03d` + `237ac4d` (FQDN trailing-dot SNI fix + `Origin.normalized_host`) → still open as **PR #1007** (mine). Since then #1223 landed (honor TLS hostname override in proxy tunnels, touches `http_proxy.py` SNI) and #1225 is open (match SNI overrides when reusing pooled connections) — rebase and check for conflicts.
- `91ad8ea` (retire `map_exceptions` in favour of plain try/except) → still open as **PR #1038** (akx). `map_exceptions` still live in `_exceptions.py`, `_synchronization.py`, `_backends/{anyio,sync,trio}.py`, `_async/_sync http11.py`.
- `c4e9340` (explicitly close async generators to prevent Trio warnings) → already in httpx2 since the `httpcore` → `httpcore2` rename (`ce6ebe2b`, #138). `safe_async_iterate()` was later reworked in #1204.
- `e88f30b` (h2 semaphore release on `NoAvailableStreamIDError`) → **merged** as PR #1012.
- `e88f30b` (h2 stream-events race in `_response_closed`) → **merged** as PR #1013. Fork bundled encode/httpcore#1061 and #1062 in one commit; split into two httpx2 PRs.
- `0387930` (propagate timeout through SOCKS5 handshake) → **merged** as PR #1009.
- `3058e2d` (RLock instead of Lock to prevent thread deadlock) → **merged** as PR #1008.
- `a7500e4` (pool poisoning on cancellation, `is_connected()`) → **merged** as PR #983 (2026-07-14).
- `199129e` (memoryview write) → already merged as `79f788b7` (#954) in httpx2.
- `079768d` (connection_pool O(N²) + bugs) → already merged as `8027999f` (#974) in httpx2 — though confirm both bug fixes from the fork's commit are included, not just the perf rewrite.
- `4a4eb1e` (anyio fast_acquire) → already merged as `b4c59404` (#970) in httpx2.
- `bdaf7f8`, `32e5f5b`, `1ec6c7a`, `f364bfe`, `1d67bd6` and the housekeeping `fix: install httpcore in test env` series — fork-only (typing back-port for old Python, the fork itself, sys.modules aliasing, CI plumbing). Not portable.

## Suggested next steps

1. Triage my stale PRs: comment on **#1010** vs #1226 (duplicate), coordinate **#1070** with Kludex's #1270, rebase **#1007** against #1223/#1225.
2. `f672124` docs note — rewrite for the truststore / #1253 world before opening.
3. `6866277` (`keep_method_for_redirects`) — open a discussion before a PR.
4. `9d86b44` — park until #1169 is merged or closed.

Landed since the 2026-07-14 survey: `70d302c` → PR #1069 (RFC 9110 status codes), `a9e7541` → #1165 + #1267 (CIDR / IPv6 in `NO_PROXY`; my #969 closed in favour of #1165).
