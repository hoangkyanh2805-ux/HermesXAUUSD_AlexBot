# Progress Sync — Output Template

Copy this structure into the agent response after updating `docs/progress-report.md`.

---

## 1. Progress summary

One short paragraph: overall state, biggest gap, whether Supabase/Metabase labels are accurate.

---

## 2. Verified completed items

Bullet list. Each item must include evidence:

- **Item** — `path/to/file.py::function` or test name

---

## 3. Partially completed items

Bullet list with explicit gap:

- **Item** — what exists / what is missing

---

## 4. Missing items

Bullet list prioritized (P0/P1 if helpful).

---

## 5. Claimed but unverified items

Table or bullets mapping chat/bot claims → why not verified.

---

## 6. Risk warnings

- Scope creep risks
- Security (secrets in chat, .env)
- False "production-ready" labels
- G10 / overtrading
- IPv6 / pooler / operator-only steps

---

## 7. Next coding tasks

Numbered, minimal scope. Format:

```text
F1. [Title] — files: a.py, b.py — done when: <check>
```

Do not include CRM, broker, funnel, or client password work.

---

## 8. Test plan

| Step | Command / action | Needs secrets? | Expected result |
|------|------------------|----------------|-----------------|
| Unit tests | `python tests/run_tests.py` | No | N passed |
| Sync dry-run | `python scripts/sync_to_supabase.py --dry-run` | No | ok: true |
| sig-test-001 E2E | … | Maybe | rows in signals |

---

## 9. Acceptance criteria

Checkbox table against project brief (14 items or current tracker in progress-report §7).

Mark only items with verified evidence as done.

---

## Footer

Link to updated doc:

`docs/progress-report.md` (updated YYYY-MM-DD)
