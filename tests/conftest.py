import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from main import app  # 引入你的主应用
from db.session import get_db

# 使用内存数据库进行测试，速度极快，且不会污染真实的 dev.db
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)


@pytest.fixture(name="session")
def session_fixture():
    # 建表
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # 测试结束删除表
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    # 覆盖原有的 get_db，让路由使用测试用的内存数据库
    def get_db_override():
        return session

    app.dependency_overrides[get_db] = get_db_override

    client = TestClient(app)
    yield client

    # 清理覆盖
    app.dependency_overrides.clear()