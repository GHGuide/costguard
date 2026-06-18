# UiPath product feedback (AgentHack Best Product Feedback)

Concrete, reproducible feedback gathered while building CostGuard (a coded agent + Orchestrator + Test Cloud + Action Center, driven end-to-end by Claude Code via the `uip` CLI on staging.uipath.com). Ordered by impact. Each item: what happened → impact → suggested fix.

### 1. `TM.Default` is not a valid Test Manager scope, and the failure mode is a silent 401
- **What:** Requesting a client-credentials token with `scope=TM.Default` succeeds (token issued), but every Test Manager API call then returns **401 Unauthorized** with an empty body. The working scopes are the granular ones (`TM.Projects`, `TM.TestCases`, `TM.TestSets`, …). `TM.Default` issues a token that authorizes nothing.
- **Impact:** Hours lost. The token is valid, the call 401s, and nothing indicates the scope is the problem. By contrast `OR.Default` *is* a valid umbrella.
- **Fix:** Either make `TM.Default` a real umbrella scope (parity with `OR.Default`), or reject it at token issuance with `invalid_scope`, or have the 401 response say "token is missing TM.* scopes." Document the granular TM scope list next to the OR list.

### 2. `uip codedagent publish` fails with opaque 500s while `uip or packages upload` works
- **What:** `uip codedagent publish --tenant` and `--folder` both fail — `--folder` 500s at "Fetching available package feeds," `--tenant` 500s at "Publishing package" — each returning only `{"statusCode":500,"activityId":...}`. The identical operation via `uip or packages upload <nupkg>` + `uip or processes create` succeeded immediately.
- **Impact:** The headline "deploy your coded agent" path was unusable; only deep CLI knowledge of `uip or` unblocked it.
- **Fix:** Have `codedagent publish` fall back to / share the `or packages upload` path; surface the real server error instead of a 500+activityId; and for external apps, detect that `--my-workspace` is invalid (no personal workspace) earlier with a clear message rather than a scope error.

### 3. External-app authorization errors don't point to the fix
- **What:** A confidential External App with all the right scopes still gets **403** in Orchestrator ("a folder is required" / "not authorized") and **401** in Test Manager until you (a) assign it a **tenant role**, (b) assign it to a **folder** with a role, and (c) for process creation, give it **Folder Administrator** (Automation User is insufficient). None of the errors say this; we needed `uip docsai` to discover it.
- **Impact:** Several round-trips of trial-and-error across Manage Access + Folders.
- **Fix:** When an authenticated app lacks a role, return an actionable error ("app X has no role on folder Y; assign one in Manage Access → External apps"). A one-click "grant this app the roles its scopes imply" would be ideal.

### 4. Action Center task creation returns a bare 404 on a tenant where it isn't provisioned
- **What:** `sdk.tasks.create_quickform(...)` (and `create(...)`) POST to `…/orchestrator_/tasks/GenericTasks/CreateTask` and get **404 "Service: orchestrator not found"** on this tenant — both locally and inside a deployed cloud job. `create(...)` also requires `appName`/`appKey` with no inline hint.
- **Impact:** Human-in-the-loop via Action Center couldn't be completed; the 404 gives no signal that the service/endpoint is unavailable vs the request being malformed.
- **Fix:** Return a clear "Action Center / Tasks service not enabled for this tenant" error; document that `create` needs an Action app and `create_quickform` needs a form schema; provide a minimal end-to-end QuickForm example in the SDK docs.

### 5. Staging blocks non-browser clients (Cloudflare error 1010) until a browser User-Agent is set
- **What:** A plain stdlib HTTPS call to the identity token endpoint returns **403 Cloudflare error 1010** ("banned based on browser signature"). Adding a browser `User-Agent` header fixes it.
- **Impact:** Confusing for anyone scripting against the API directly; looks like an auth failure.
- **Fix:** Don't gate the API/identity endpoints on browser-signature WAF rules, or document the requirement; the official SDK/CLI should always send a proper UA.

### 6. `uip tasks` can't create tasks; `jobs start` needs the release-key GUID
- **What:** (a) `uip tasks` only manages existing tasks (assign/complete/list) — no `create`; task creation is SDK-only. (b) `uip or jobs start <process>` returns **400 "Undefined process"** for the process name *and* the ProcessKey; only the release **Key GUID** works.
- **Impact:** Minor but each cost a debugging cycle.
- **Fix:** Add `uip tasks create`; let `jobs start` accept process name/ProcessKey (resolve to the latest release) and say which forms are accepted on error.

### 7. `uip codedagent setup` install guidance vs Homebrew/PEP-668 + Python 3.14
- **What:** Setup needs the `uipath` SDK on PATH and suggests `python3.13 -m pip install uipath`, which fails on Homebrew Python (PEP-668 externally-managed) and isn't available for Python 3.14. `uv tool install uipath` worked.
- **Impact:** A new builder on a stock Mac hits a wall at step one.
- **Fix:** Lead the setup hint with `uv tool install uipath` / `pipx`; state the supported Python range explicitly (3.14 was too new).

### What worked well (credit where due)
- `uip or` (packages/processes/jobs/folders/feeds) is excellent and unblocked everything.
- `uip docsai ask` gave accurate, actionable answers and repeatedly got us unstuck.
- Non-interactive client-credentials `uip login` and `uip codedagent run`/`init` (call-graph tracing) are genuinely great DX.
- Coded agents running as serverless Orchestrator jobs "just worked" once deployed (~11s cold run, clean output arguments).

*Environment: staging.uipath.com, org hackathon26_717, `uip` CLI 1.195.0, uipath SDK 2.11.4, macOS, Claude Code.*
