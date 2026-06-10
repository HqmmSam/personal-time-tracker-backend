# Personal Time Tracker · Backend

> Python 3.11 · FastAPI 0.111 · SQLAlchemy 2.0 · MySQL 5.7 / 8.0 · Pydantic v2 · JWT
> 对应教学讲义《第五次课 - 后端功能实现》

---

## 环境要求

在开始之前，请确认本机已安装以下软件：

| 软件 | 最低版本 | 检查命令 |
|------|---------|---------|
| Python | 3.11 | `python3 --version` |
| pip | 23+ | `pip --version` |
| MySQL | 5.7 或 8.0 | `mysql --version` |

> **MySQL 安装参考**
> - macOS：`brew install mysql` 然后 `brew services start mysql`
> - Windows：从 [mysql.com](https://dev.mysql.com/downloads/installer/) 下载 MySQL Installer
> - Linux (Ubuntu)：`sudo apt install mysql-server && sudo systemctl start mysql`

---

## 第一步：获取代码

```bash
# 如果是独立仓库
git clone <your-repo-url>
cd backend

# 如果在 monorepo 中
cd personal-time-tracker/backend
```

---

## 第二步：创建并激活 Python 虚拟环境

虚拟环境可以隔离项目依赖，避免污染系统 Python。

```bash
# 创建虚拟环境（目录名 .venv）
python3.11 -m venv .venv

# 激活虚拟环境
# macOS / Linux：
source .venv/bin/activate

# Windows（CMD）：
# .venv\Scripts\activate.bat

# Windows（PowerShell）：
# .venv\Scripts\Activate.ps1
```

激活成功后，命令行提示符前会出现 `(.venv)` 字样。

---

## 第三步：安装依赖

```bash
pip install -r requirements.txt
```

安装完成后可以验证关键包：

```bash
pip show fastapi sqlalchemy pymysql
```

---

## 第四步：初始化数据库

### 4.1 启动 MySQL 并登录

```bash
# macOS（Homebrew）
brew services start mysql

# 验证 MySQL 是否在运行
mysql -uroot -p
# 输入密码后看到 mysql> 提示符即代表连接成功，输入 exit 退出
```

### 4.2 执行建表脚本

```bash
# 在 backend/ 目录下执行
mysql -uroot -p < db/init.sql
```

脚本会自动创建 `time_tracker` 数据库和 5 张表（users / projects / tasks / time_records / user_settings）。

验证是否创建成功：

```bash
mysql -uroot -p -e "USE time_tracker; SHOW TABLES;"
```

期望输出：

```
+------------------------+
| Tables_in_time_tracker |
+------------------------+
| projects               |
| tasks                  |
| time_records           |
| user_settings          |
| users                  |
+------------------------+
```

---

## 第五步：配置环境变量

```bash
# 复制示例文件
cp .env.example .env
```

用编辑器打开 `.env`，按照下面说明修改：

```ini
APP_ENV=dev
APP_DEBUG=true

# 数据库连接——将 your_password 改为你的 MySQL root 密码
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=time_tracker

# JWT 密钥——务必替换为一个随机字符串（32 位以上），生产环境不得使用默认值
JWT_SECRET_KEY=please-change-to-a-random-32-char-string
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# 允许跨域的前端地址（开发环境默认即可）
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

> **生成随机密钥的方法：**
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

---

## 第六步：启动开发服务器

```bash
uvicorn app.main:app --reload --port 8000
```

看到以下输出代表启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

`--reload` 参数开启热重载，修改代码后自动重启，无需手动停止。

---

## 第七步：验证服务正常

打开浏览器，访问以下地址：

| 地址 | 说明 |
|------|------|
| http://localhost:8000/health | 返回 `{"status":"ok"}` 即代表服务正常 |
| http://localhost:8000/docs | Swagger UI，可直接在页面测试所有接口 |
| http://localhost:8000/redoc | ReDoc 风格的接口文档 |

### 用 Swagger UI 快速冒烟测试

1. 访问 `http://localhost:8000/docs`
2. 展开 `POST /api/v1/auth/register`，点击 **Try it out**
3. 填入邮箱、密码、昵称，点击 **Execute**
4. 看到 `201 Created` 且响应体包含 `token` 字段
5. 点击页面右上角 **Authorize**，输入 `Bearer <刚才的token>`
6. 再试 `GET /api/v1/auth/me`，应返回当前用户信息

---

## 接口概览

| 模块 | 接口数 | 路径前缀 |
|------|--------|---------|
| 认证 | 4 | `/api/v1/auth` |
| 用户 | 3 | `/api/v1/users/me` |
| 项目 | 5 | `/api/v1/projects` |
| 任务 | 5 | `/api/v1/projects/{pid}/tasks` + `/api/v1/tasks/{id}` |
| 记录 | 4 | `/api/v1/records` |
| 统计 | 4 | `/api/v1/stats` |
| 预测 | 2 | `/api/v1/predictions` |
| 设置 | 2 | `/api/v1/users/me/settings` |

---

## 目录结构

```
backend/
├── app/
│   ├── main.py              入口（CORS / 路由 / 日志中间件 / 异常处理）
│   ├── config.py            pydantic-settings 配置类（读取 .env）
│   ├── database.py          SQLAlchemy 引擎 + Session 工厂 + Base
│   ├── deps.py              依赖注入：get_db / get_current_user
│   ├── exceptions.py        业务异常类：BusinessException / ResourceNotFound / PermissionDenied
│   ├── handlers.py          全局异常处理器（统一 JSON 格式响应）
│   ├── models/              ORM 模型（User / Project / Task / TimeRecord / UserSettings）
│   ├── schemas/             Pydantic 请求/响应 Schema
│   ├── services/            业务逻辑层（各模块 Service 类）
│   ├── routers/             路由层（各模块 router）
│   └── utils/security.py    bcrypt 密码哈希 + JWT 签发/验证
├── db/
│   └── init.sql             数据库建表脚本（5 张表，MySQL 5.7 / 8.0 兼容）
├── requirements.txt         Python 依赖列表
├── .env.example             环境变量示例（复制为 .env 后填写真实值）
└── README.md
```

---

## 技术栈

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 运行环境 |
| FastAPI | 0.111 | Web 框架，自动生成 Swagger |
| SQLAlchemy | 2.0 | ORM，Session 模式 |
| MySQL | 5.7 / 8.0 | 关系型数据库（两版本均兼容） |
| PyMySQL | 1.1 | Python MySQL 驱动 |
| Pydantic v2 | 2.7 | 请求/响应数据校验 |
| python-jose | 3.3 | JWT 签发与验证 |
| passlib[bcrypt] | 1.7 | 密码哈希（bcrypt，自动加盐）|

---

## 开发调试

```bash
# APP_DEBUG=true 时 SQLAlchemy 会自动打印所有 SQL
# 也可手动在代码中查看生成的 SQL：
print(query.statement.compile(compile_kwargs={"literal_binds": True}))
```

---

## 常见报错与解决

| 报错信息 | 原因 | 解决方法 |
|---------|------|---------|
| `Access denied for user 'root'@'localhost'` | 密码错误 | 检查 `.env` 中的 `DB_PASSWORD` |
| `Can't connect to MySQL server on '127.0.0.1'` | MySQL 未启动 | `brew services start mysql` 或 `sudo systemctl start mysql` |
| `Unknown database 'time_tracker'` | 建表脚本未执行 | 重新执行 `mysql -uroot -p < db/init.sql` |
| `No module named 'pymysql'` | 依赖未安装或虚拟环境未激活 | 激活 `.venv` 后重新 `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'app'` | 不在 `backend/` 目录下执行 | 确保在 `backend/` 目录内运行 `uvicorn` |
| `422 Unprocessable Entity` | 请求字段校验失败 | 查看响应体 `detail` 字段，确认传参格式 |
| `401 Unauthorized` | token 缺失或过期 | Swagger 页面重新 Authorize，或重新登录获取新 token |
| `password cannot be longer than 72 bytes` | bcrypt 版本或密码哈希依赖不一致 | 重新执行 `pip install -r requirements.txt`，并重启 `uvicorn` |
