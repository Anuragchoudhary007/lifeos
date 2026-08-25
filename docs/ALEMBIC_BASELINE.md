# Alembic baseline procedure

LifeOS has an existing SQLite database that predates Alembic. Do not run
`alembic upgrade head` or generate a migration against it until a reviewed
baseline revision has been created.

When schema evolution is approved:

1. Back up `storage/database/lifeos.db`.
2. Inspect the live schema and compare it with the SQLAlchemy models.
3. Create a reviewed baseline revision that represents the existing schema.
4. Stamp the existing database with that revision using `alembic stamp <revision>`.
5. Create subsequent migrations from the stamped baseline and review generated
   SQLite operations before applying them.

No Alembic revision was generated or applied in Phase 4.
