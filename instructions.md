# BuildCore — Coding Guidelines

## Strict Rules

### 1. File Size Limit
- Maximum **500 lines** per file. Split into smaller modules if needed.

### 2. No Foreign Keys
- **No `ForeignKey()` or `relationship()`** in SQLAlchemy models.
- All relations are soft — use `String(36)` columns to store referenced IDs.
- Validation of referenced records happens at the **service layer**.

### 3. No Database ENUMs
- **No `ENUM` types** in PostgreSQL or SQLAlchemy.
- All status/type fields are `String(50)` or similar.
- Validation uses Python `enum.Enum` classes in **Pydantic schemas**.

### 4. Soft Delete
- All business tables have a `deleted_at` column (nullable DateTime).
- "Delete" operations set `deleted_at = now()`, never hard delete.
- Queries always filter: `WHERE deleted_at IS NULL`.

### 5. Fail-Fast Validation
- Stop on the **first error** encountered.
- Raise `BuildCoreError` subclass immediately.
- Return **422** (ValidationError) or **400** for invalid input.
- No partial updates — if one field fails, the whole request fails.

### 6. Naming Conventions
- **Database columns**: `snake_case` (e.g., `created_at`, `organization_id`)
- **API request/response fields**: `camelCase` (e.g., `createdAt`, `organizationId`)
- Auto-conversion layer between DB and API (Pydantic `alias` or service layer)

### 7. No Mock Data
- All API endpoints return real data from the database.
- Seed data is for initial setup only (system roles, SDUI menus, subscription plans).

### 8. File Naming
- **No UUID in file names.** Use registration number or logical ID.
- Example: `EMP-001_contract.pdf` instead of `a1b2c3d4-contract.pdf`.

### 9. Feature-Driven Structure
- Code organized by **feature** (auth, organization, user, project, etc.).
- Each feature has: `service.py`, `crud.py`, `schemas.py` (if needed).
- Shared utilities go in `core/`, never in feature folders.

### 10. Multi-Tenant
- Every business table includes `organization_id`.
- Tenant ID extracted from JWT via middleware (`contextvars`).
- Service layer filters queries by `organization_id`.

## Storage
- File storage is driven by `.env` (`STORAGE_NAME`).
- Supported: MinIO (default), S3, Local filesystem.
- Switch by changing `.env` only — no code changes.

## API Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "meta": { "page": 1, "per_page": 20, "total": 100, "total_pages": 5 }
}
```

## Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [{ "field": "email", "message": "This field is required" }]
  }
}
```

## Authentication
- JWT access token: **30 minutes** expiry
- JWT refresh token: **7 days** expiry
- Registration: **Super Admin invite-based** only (invite link with token)
- Password hashing: **Argon2id**

## Audit Trail
- Only `audit_logs` table is partitioned (year-wise by `created_at`).
- Track: who, what, when, where (IP), old/new values.

---

## Development Environment — SSH & Git Push

### SSH Key Info (DO NOT LOSE)
This environment has **no native `ssh` binary**. Git push uses a Python `paramiko` wrapper.

- **Private Key**: `/home/z/.ssh/id_rsa_buildcore`
- **SSH Wrapper Script**: `/home/z/.ssh/ssh_wrapper.py`
- **Key Type**: RSA (4096-bit)
- **Comment**: `buildcore@dev.bot`

### Public Key (already added to GitHub):
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCXs8tuXJBjr968sRCnvWDqWYiibszaIGeTz2n/0dk3bdJBHkYUH1gPCvYol0tBGbh3X8VHnnRQukIt4iu7DR+qpmyXJIF4jy1097NYbREtnRuRsqqVaTIPYGgGfuKjwqc2437EbdjqcxXe8fIRTGKo/EN3KMaIsL+jBvxSnSmUmGYA5J3xZJXh+82fv1p0lGulHHv0gkk3/Bneqyi2x5z4P+JoC9jsu/SoOz2qDkbe1b8CDeMzJWAdC8jkjbL2ILAGDJY+DwudtfRryHe94u75LoqFIVvBPRJo7u8HiAxKSuvPjhRbKVZcEVG94dLt8ChJmveSI3H8Pq6MGJEVxIcyq3+D7VFXwD3DTZNIvhaTWnYWZfwLa9X72IC9Ptkwim4O78IWmAYzwJET5e/lK6EwvcHeEYVkbbPR2Xf/HhBIlT+FApPuIyFOIh2xbNo/4CP4hBrDShfD4K0GuBNkfcHVU9rn84iY4GO+QIx6KhWM2J0IzTZGkTmUWbOmQHwTY79silBgNi+ZhtaPPS08+XA1UwTB6X540ORwt7zJO8ohhSwFfPj490SgmZR+EhkoFuBTlqBibcubWCYutrT6aa+5Lp/tObpaGXcUgbKy3eBEnF57MMNMde5udSVyOxALQdwlYGqvcQksk2IAVYnUgfitXCEghCRYjRBElmc33jmO2w==
```

### How to Push:
```bash
GIT_SSH_COMMAND="python3 /home/z/.ssh/ssh_wrapper.py" git -C /home/z/build_core push origin main
```

### How to Pull:
```bash
GIT_SSH_COMMAND="python3 /home/z/.ssh/ssh_wrapper.py" git -C /home/z/build_core pull origin main
```

### Wrapper Dependencies:
- `paramiko` — required for SSH connections
- Install: `python3 -m pip install paramiko`

### If Key Stops Working:
1. Generate new RSA key:
   ```bash
   python3 -c "import paramiko; k=paramiko.RSAKey.generate(4096); k.write_private_key_file('/home/z/.ssh/id_rsa_buildcore'); print(k.get_name()+' '+k.get_base64())"
   ```
2. Add new public key to GitHub → Settings → Deploy Keys → Allow write access
3. Update instructions.md with new public key
4. **NEVER use HTTPS push** — no credential helper available in this environment

### Git Remote:
```
origin  git@github.com:jafrulmdsts/build_core.git
```
