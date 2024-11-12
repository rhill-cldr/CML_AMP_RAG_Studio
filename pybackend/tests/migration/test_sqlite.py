import sqlite3

import pytest
from src.migration.datastore import SQLiteDatastore
from src.migration.migrator import Migrator


@pytest.fixture
def sqlite_connection():
    """Create a SQLite in-memory database connection for testing."""
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def sqlite_datastore(sqlite_connection: sqlite3.Connection):
    """Create a SQLDatastore instance with an in-memory SQLite database."""
    datastore = SQLiteDatastore(sqlite_connection)
    return datastore


@pytest.fixture
def migrator(sqlite_datastore: SQLiteDatastore):
    return Migrator(sqlite_datastore)


def test_sqlite_migration_content(sqlite_datastore: SQLiteDatastore):
    sqlite_datastore.ensure_migration_state_table_exists()
    sqlite_datastore.ensure_migration_content_table_exists()

    migrations_from_db = sqlite_datastore.get_migrations_from_db()
    migrations_from_disk = sqlite_datastore.get_migrations_from_disk()
    assert len(migrations_from_db) == 0

    migrator = Migrator(sqlite_datastore)
    migrator.perform_migration()

    migrations_from_db = sqlite_datastore.get_migrations_from_db()
    assert migrations_from_db == migrations_from_disk


def test_sqlite_migration_up_down(
    sqlite_datastore: SQLiteDatastore,
    migrator: Migrator,
):
    migrator.perform_migration()

    state = sqlite_datastore.get_migration_state()
    migrations_in_disk = sqlite_datastore.get_migrations_from_disk()

    assert not state.dirty
    assert state.version == len(migrations_in_disk) // 2

    migrator.perform_migration(desired_version=0)

    state = sqlite_datastore.get_migration_state()
    assert state.version == 0
    assert not state.dirty
