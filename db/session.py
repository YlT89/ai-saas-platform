from sqlmodel import create_engine, Session
from core.config import settings

if settings.app == 'dev':
    engine = create_engine(
        settings.db_url,
        echo=True,

        connect_args={'check_same_thread': False}
    )


else:
    engine = create_engine(
        settings.db_url,
        echo=False,
        pool_size=15
    )


def get_db():
    with Session(engine) as session:
        yield session