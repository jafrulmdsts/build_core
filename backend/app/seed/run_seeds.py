"""
Master seed runner.

Runs all seed functions in the correct order and creates
the default Super Admin user from settings.

Usage:
    uv run -m app.seed.run_seeds
"""

import asyncio
import hashlib
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select

from app.config import get_settings
from app.database import async_session_maker
from app.core.security import get_password_hash
from app.models.user import User
from app.seed.seed_roles import seed_roles
from app.seed.seed_sdui_menus import seed_sdui_menus
from app.seed.seed_subscription_plans import seed_subscription_plans

settings = get_settings()


async def seed_superadmin(db) -> None:
    """Create the default Super Admin user if not already present."""
    stmt = select(User).where(User.email == settings.SUPER_ADMIN_EMAIL)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        print(f"  [SKIP] Super Admin already exists: {settings.SUPER_ADMIN_EMAIL}")
        return

    superadmin = User(
        email=settings.SUPER_ADMIN_EMAIL,
        password_hash=get_password_hash(settings.SUPER_ADMIN_PASSWORD),
        first_name="Super",
        last_name="Admin",
        is_super_admin=True,
        is_active=True,
        role_id="00000000-0000-4000-a000-000000000001",  # Super Admin role UUID
    )
    db.add(superadmin)
    await db.flush()
    print(f"  [OK] Super Admin created: {settings.SUPER_ADMIN_EMAIL}")


async def run_all_seeds() -> None:
    """Run every seed in dependency order inside a single transaction."""
    async with async_session_maker() as db:
        try:
            print("\n[SEED] Starting database seeding...\n")

            print("[1/4] Seeding roles...")
            await seed_roles(db)
            print("      Done.")

            print("[2/4] Seeding subscription plans...")
            await seed_subscription_plans(db)
            print("      Done.")

            print("[3/4] Seeding SDUI menus...")
            await seed_sdui_menus(db)
            print("      Done.")

            print("[4/4] Seeding Super Admin user...")
            await seed_superadmin(db)

            await db.commit()
            print("\n[SEED] All seeds completed successfully!\n")

        except Exception as e:
            await db.rollback()
            print(f"\n[SEED] ERROR - Seeding failed: {e}\n")
            raise


if __name__ == "__main__":
    asyncio.run(run_all_seeds())
