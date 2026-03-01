import pytest
from src.infrastructure.database import DatabaseManager

def test_debug():
    manager = DatabaseManager("sqlite:///:memory:")
    print("Databases:", manager.databases)
    print("Current DB:", manager.get_current_db_name())
    print("Engines keys:", list(manager._engines.keys()))
    try:
        engine = manager.get_engine()
        print("Engine:", engine)
        print("Engine has dialect:", hasattr(engine, 'dialect'))
    except Exception as e:
        print("Error getting engine:", e)
        print("Exception type:", type(e))

if __name__ == "__main__":
    test_debug()