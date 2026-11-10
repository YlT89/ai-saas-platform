# 🚀 FastAPI 企业级后端基础脚手架 (Enterprise FastAPI Scaffold)

本项目是一个基于 FastAPI 构建的生产级后端基础架构模板。从最初的单文件脚本，逐步重构演进为**高内聚、低耦合**的企业级标准分层架构。涵盖了 JWT 鉴权、数据库 ORM、全局异常处理、自动化测试及容器化部署等核心企业级特性。

## ✨ 核心技术栈

*   **Web 框架**: FastAPI (高性能异步 Web 框架)
*   **数据校验**: Pydantic V2 (强类型校验，支持自定义 Validator 与 ConfigDict)
*   **数据库 ORM**: SQLModel + SQLite (支持连接池与线程安全)
*   **身份认证**: JWT (JSON Web Token) + OAuth2 密码流
*   **密码安全**: Passlib (PBKDF2 算法加盐哈希)
*   **自动化测试**: Pytest + HTTPX (内存级隔离测试)
*   **容器化部署**: Docker + Uvicorn

## 📁 项目架构说明

采用标准的企业级模块化目录结构：

```text
fastapi-final-project/
├── core/                 # 核心配置层 (无业务逻辑)
│   ├── config.py         # Pydantic-settings 全局环境变量配置
│   ├── exceptions.py     # 全局异常拦截与统一格式返回
│   ├── middlewares.py    # 跨域 (CORS) 与请求日志记录中间件
│   └── response.py       # 统一响应模型 (ApiResp) 
├── crud/                 # 数据访问层 (业务逻辑与数据库操作解耦)
│   ├── base.py           # 泛型基础 CRUD 类 (封装通用增删改查)
│   └── user_crud.py      # 针对 User 表的业务 CRUD
├── db/                   # 数据库基础设施
│   └── session.py        # Engine 引擎与 get_db 依赖注入
├── dependencies/         # 全局依赖注入
│   └── auth.py           # JWT Token 生成与解析守卫
├── models/               # 数据库 ORM 实体 (SQLModel, table=True)
│   └── user.py           # 用户表结构定义
├── routers/              # 路由控制层
│   ├── auth_routers.py   # 登录、注册接口
│   └── user_routers.py   # 用户信息、权限校验接口
├── schemas/              # DTO 数据传输模型 (Pydantic)
│   └── user_schemas.py   # UserCreate, UserPublic 等
├── tests/                # 自动化测试目录
│   ├── conftest.py       # 内存数据库隔离与 TestClient 夹具
│   └── test_auth.py      # 注册与 JWT 鉴权全链路测试
├── .env7                 # 本地环境变量 (已被 .gitignore 忽略)
├── Dockerfile            # 生产级多阶段构建镜像脚本
├── pytest.ini            # Pytest 运行配置
└── requirements.txt      # 生产环境依赖清单


核心特性亮点
1、彻底的分层架构：将 API 路由 (routers)、数据校验 (schemas)、数据库实体 (models) 和 业务逻辑 (crud) 严格分离，符合 RESTful 设计规范。

2、全局异常兜底机制：通过 core/exceptions.py 全局拦截 ValidationError、HTTPException 及未预料的 Exception，保证前端永远收到格式统一的 { code, msg, data } JSON 响应，隐藏底层报错堆栈。

3、安全防护：使用 OAuth2PasswordBearer 实现标准的 JWT 鉴权；密码拒绝明文存储，使用 passlib 进行不可逆哈希；登录接口加入了时序攻击防护（即使账号不存在也会进行虚假哈希校验消耗时间）。

4、高质量的自动化测试：利用 conftest.py 动态覆盖依赖，生成内存级 SQLite 数据库，实现测试环境与开发环境的完全隔离。测试覆盖率达核心接口 100%。

5、Docker 容器化：支持一键构建镜像，利用 .dockerignore 排除冗余文件，实现开箱即用的云端部署


本地开发指南
1. 环境准备
确保你已安装 Python 3.10+，并克隆本项目：
git clone <你的GitHub仓库地址>
cd fastapi-final-project

2. 安装依赖
建议使用虚拟环境：
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
# 本地开发/测试环境安装额外依赖：
pip install -r requirements-dev.txt 

3. 配置环境变量
在根目录新建 .env7 文件，填入你的配置信息：
APP=dev
DB_URL=sqlite:///./dev.db
SECRET_KEY=your_super_secret_key_change_me_in_production
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

4. 启动服务
uvicorn main9:app --reload



自动化测试
本项目包含完整的接口测试与鉴权链路测试。在根目录执行：
pytest
(测试使用内存数据库隔离，不会污染本地开发数据)

🐳 Docker 部署
项目已配置标准 Dockerfile，在根目录执行以下命令进行构建与启动：

# 1. 构建镜像
docker build -t my-fastapi-app .

# 2. 启动容器 (映射 8000 端口)
docker run -d -p 8000:8000 --name my-api my-fastapi-app
⭐ 如果这个架构对你有帮助，欢迎点个 Star！