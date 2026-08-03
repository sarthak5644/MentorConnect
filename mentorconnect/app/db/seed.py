"""
app/db/seed.py
-----------------
Idempotent seed script: ensures the three RBAC roles exist and that a
Super Admin account is bootstrapped on first run (from SUPERADMIN_* env vars).
Safe to run multiple times - it only creates what's missing.

Run manually with:  python -m app.db.seed
Also invoked automatically on application startup (see main.py lifespan).
"""

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import hash_password
from app.core.logger import logger
from app.core.config import settings
from app.models.user import Role, User
from app.models.category import Category, Field
from app.models.enums import RoleName, UserStatus

# A small starter taxonomy so the platform isn't empty on first run.
# Admins can add more categories/fields later via the /categories endpoints.
_DEFAULT_TAXONOMY: dict[str, list[str]] = {
    "Technology": ["Software Engineering", "Data Science", "Machine Learning", "Cybersecurity", "Cloud Computing"],
    "Business": ["Entrepreneurship", "Marketing", "Finance", "Product Management", "Sales"],
    "Design": ["UI/UX Design", "Graphic Design", "Product Design"],
    "Career": ["Resume Building", "Interview Preparation", "Career Switching"],
    "Academics": ["Higher Studies Guidance", "Research Mentorship", "Test Preparation"],
}


def seed_roles(db: Session) -> None:
    for role_name in RoleName:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if existing is None:
            db.add(Role(name=role_name, description=f"{role_name.value.replace('_', ' ').title()} role"))
            logger.info(f"Seeded role: {role_name.value}")
    db.commit()


def seed_super_admin(db: Session) -> None:
    existing = db.query(User).filter(User.email == settings.SUPERADMIN_EMAIL).first()
    if existing is not None:
        return

    super_admin_role = db.query(Role).filter(Role.name == RoleName.SUPER_ADMIN).first()
    if super_admin_role is None:
        logger.error("Cannot seed Super Admin: SUPER_ADMIN role not found. Run seed_roles first.")
        return

    admin_user = User(
        full_name=settings.SUPERADMIN_FULL_NAME,
        email=settings.SUPERADMIN_EMAIL,
        mobile_number=None,
        hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
        role_id=super_admin_role.id,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
        is_mobile_verified=True,
    )
    db.add(admin_user)
    db.commit()
    logger.info(f"Seeded Super Admin account: {settings.SUPERADMIN_EMAIL}")
    logger.warning(
        "IMPORTANT: Change the default Super Admin password immediately after first login!"
    )


def seed_taxonomy(db: Session) -> None:
    """Seeds a small default set of categories/fields if none exist yet."""
    existing_count = db.query(Category).count()
    if existing_count > 0:
        return

    for category_name, field_names in _DEFAULT_TAXONOMY.items():
        category = Category(name=category_name, description=f"{category_name}-related mentorship", is_active=True)
        db.add(category)
        db.flush()  # get category.id without a full commit
        for field_name in field_names:
            db.add(Field(category_id=category.id, name=field_name, is_active=True))
    db.commit()
    logger.info("Seeded default category/field taxonomy.")


def run_seed() -> None:
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_super_admin(db)
        seed_taxonomy(db)
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
