import databases
import sqlalchemy

# DEV database currently set up.
DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5432/dev"
database = databases.Database(DATABASE_URL)

# metadata = sqlalchemy.MetaData()

# users = sqlalchemy.Table(
#     "users",
#     metadata,
#     sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
#     sqlalchemy.Column("username", sqlalchemy.String),
#     sqlalchemy.Column("password", sqlalchemy.String),
#     sqlalchemy.Column("phone_number", sqlalchemy.String),
#     sqlalchemy.Column("firstname", sqlalchemy.String),
#     sqlalchemy.Column("lastname", sqlalchemy.String),
# )


# engine = sqlalchemy.create_engine(
#     DATABASE_URL
# )
# metadata.create_all(engine)

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

def provide_connection():
        return database