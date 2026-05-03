# BuildCore Worklog

## 2025-01-XX — Bug Fixes: Subscription Display, Exception Handlers, View Guards

### Problem 1: Subscription Plans Page Shows No Data (FIXED)

**File:** `backend/app/services/subscription/service.py`

**Root cause:** `_to_response()` called `SubscriptionPlanResponse.model_validate(plan)` first, which tried to validate the ORM `features` column (a `Text` column containing a JSON string like `'["Up to 3 users"]'`) against the schema field `features: list[str]`. Pydantic raised a `ValidationError` because a string is not a `list[str]`. The subsequent `data.features = _parse_features(...)` line never executed. Since `ValidationError` is not a `BuildCoreError`, it was not caught by the route handler, resulting in a 500 Internal Server Error.

**Fix:** Replaced `model_validate(plan)` with manual field-by-field construction of the `SubscriptionPlanResponse`, calling `_parse_features(plan.features)` inline so the JSON string is parsed into `list[str]` before being passed to the Pydantic constructor.

---

### Problem 2: Add Pydantic ValidationError Handlers (FIXED)

**File:** `backend/app/main.py`

**Root cause:** Only `BuildCoreError` had a global exception handler. `RequestValidationError` (from FastAPI request body/query parsing) and `ValidationError` (from Pydantic schema validation) both fell through to the default handler, returning FastAPI's raw 422 HTML/JSON format which was inconsistent with the BuildCore error envelope.

**Fix:** Added two new exception handlers:
- `RequestValidationError` → 422 with `{ success, error: { code, message, details } }`
- `ValidationError` → 422 with the same envelope

Both extract the last element of `err["loc"]` as the field name and `err["msg"]` as the message.

---

### Problem 3: Add Catch-All Exception Handler (FIXED)

**File:** `backend/app/main.py`

**Root cause:** Any unexpected exception (e.g., database connection errors, programming bugs) would return a raw 500 with FastAPI's default body, potentially leaking implementation details.

**Fix:** Added a catch-all `Exception` handler that:
1. Logs the full traceback via `logger.error(..., exc_info=True)`
2. Returns a generic 500 response with `{ success: false, error: { code: "INTERNAL_ERROR", message: "An unexpected error occurred", details: [] } }`

Added `import logging` and `logger = logging.getLogger("buildcore")` at module level.

---

### Problem 4: Employees / Users / Roles Views (NO FIX NEEDED)

**Files:**
- `frontend/src/views/EmployeesView.vue`
- `frontend/src/views/UsersView.vue`
- `frontend/src/views/RolesView.vue`

**Finding:** All three views already properly implement the `isSuperAdminNoOrg` guard:

1. Each defines: `const isSuperAdminNoOrg = computed(() => authStore.isSuperAdmin && !authStore.hasOrganization);`
2. Each shows an informational notice when the guard is true (amber banner with Building2/Shield icon, linking to Organizations page)
3. Each skips `onMounted` data fetching when the guard is true
4. Each hides action buttons (Add Employee / Invite User / Create Role) when the guard is true
5. The auth store (`frontend/src/features/auth/store.ts`) already exports `isSuperAdmin` and `hasOrganization` computed properties

No changes were needed for these views.

---

### Problem 5: OrganizationsView Subscription Plan Dropdown (NO FIX NEEDED)

**File:** `frontend/src/views/OrganizationsView.vue`

**Finding:** The organization create/edit form already includes a subscription plan dropdown:

1. `fetchSubscriptionPlans()` fetches active plans from `GET /subscriptions` on mount
2. The form has `subscription_plan_id` field (in `defaultForm` and `form` reactive)
3. The modal form includes a `<select>` with `CreditCard` icon, showing plan name, monthly price, user limit, and project limit
4. The `saveOrganization()` payload includes `subscription_plan_id`
5. The `openEditModal()` function pre-populates `subscription_plan_id` from the org data

No changes were needed for this view.
