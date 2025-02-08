from fastapi import Depends

from storage.storage import Storage, db_state_default, db_state
from manager.global_manager import GlobalManager

def get_database():
    storage = Storage(GlobalManager.global_config.database_url, GlobalManager.global_config.database_pragmas)
    storage.database._state._state.set(db_state_default.copy())
    storage.database._state.reset()
    try:
        storage.connect()
        yield
    finally:
        if not storage.is_closed():
            storage.close()


