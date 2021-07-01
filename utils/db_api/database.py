from gino import Gino
from gino.schema import GinoSchemaVisitor

from data.config import DB_NAME, PG_USER, PG_PASS, PG_HOST

db = Gino()


async def create_db():
    await db.set_bind(f'postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}/{DB_NAME}')

    # Create tables
    db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    await db.gino.create_all()
