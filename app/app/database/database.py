import databases
import sqlalchemy

# DEV database currently set up.
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/dev"
database = databases.Database(DATABASE_URL)

async def startup():
    # Start database on app startup.
    try:
        await database.connect()
        print("INFO:     Successfully connected to database.")
    except ConnectionRefusedError:
        print("ERROR:    Could not connect to database.")
        raise 

async def shutdown():
    # Stop database on shutdown.
    print("INFO:     Disconnecting from database.")
    await database.disconnect()

def provide_connection() -> databases.Database:
        return database