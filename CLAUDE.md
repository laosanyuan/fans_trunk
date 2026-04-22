# CLAUDE.md

## 项目概述

`fans_trunk` 是一个用于 Telegram 频道互推的 Python 机器人项目。

当前核心职责：

- 通过 Telegram 机器人处理用户与频道接入
- 根据频道评分将频道分配到不同车队
- 定时向频道发布互推消息
- 在权限异常或发送失败时处理频道移除或降级
- 通过 WxPusher 发送日报或异常通知

当前仓库文档中使用的镜像版本是 `fans_trunk:1.0.13`。

## 技术栈

- Python
- `python-telegram-bot==21.11.1`
- Peewee + SQLite
- APScheduler
- `inject` 依赖注入
- Docker 基础镜像：`python:3.10-alpine`

## 目录结构

- `main.py`：程序入口与依赖注入配置
- `services/`：业务服务与调度逻辑
- `services/telegram/`：Telegram 相关交互、消息发布、用户流程
- `db/`：数据库连接、模型、DAO
- `models/`：DTO 数据对象
- `templates/`：模板配置与初始数据
- `tests/services_tests/core_logic_test.py`：当前核心回归测试

## 运行时关键文件

- `configs/settings.json`：机器人 token、管理员、代理、WxPusher 配置
- `configs/fleets.json`：车队分数区间配置
- `configs/ad_settings.json`：广告位配置，支持 `head`、`tail`、`button`
- `configs/data.db`：运行时 SQLite 数据库

注意：

- 仓库中默认提供的是 `templates/` 下的模板文件
- 实际运行时读取的是 `configs/` 目录

## 启动流程

程序启动顺序如下：

1. `main.py` 配置依赖注入
2. `DbService.init_db()` 初始化数据库并绑定 Peewee 模型
3. `FleetManager.init()` 将车队配置写入数据库
4. `SchedulerManager.start()` 启动定时任务
5. `BotManager.run()` 启动 Telegram 轮询

补充：

- 在 Windows 环境下，`main.py` 会从配置中读取代理并设置 `http_proxy` / `https_proxy`

## 核心逻辑位置

### 频道与车队分配

- `db/daos/fleet_dao.py`：根据分数匹配车队
- `db/daos/channel_dao.py`：筛选可用频道、查询互推候选频道
- `services/telegram/score_service.py`：根据频道数据计算评分

### Telegram 用户流程

- `services/telegram/user_service.py`：处理 `/start`、`/help`、按钮回调、频道成员变更
- `services/telegram/admin_service.py`：处理 `/admin`
- `services/telegram/menu_strategies/`：菜单与按钮文案/结构

### 消息发布流程

- `services/telegram/chat_service.py` 是当前最需要谨慎修改的模块

它负责：

- 判断当前频道是否已有互推消息
- 决定是更新旧消息还是直接发布新消息
- 处理 `BadRequest` 场景下的延迟移除逻辑
- 在 `Forbidden` 或发布失败时通知用户并移除频道

修改这个文件时要特别保持以下规则：

- 连续 `BadRequest` 时的延迟移除缓存逻辑不能破坏
- 用户可见文案中的表情、`【】`、现有风格不要随意改
- 旧消息删除失败时，不能继续直接发布新消息，否则会出现重复发车

## 测试命令

建议使用如下命令：

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p '*test.py' -v
python -m compileall main.py services db models
```

说明：

- `unittest discover` 如果不加 `-s tests`，当前仓库里默认可能发现不到测试
- 如果当前环境里 `python` 不在 `PATH`，请改用该环境实际可用的 Python 解释器执行

## Docker 说明

项目当前 Docker 相关命令应保持与 README 中一致：

```powershell
docker build -t fans_trunk:1.0.13 .
docker save -o fans_trunk_1.0.13.tar fans_trunk:1.0.13
```

如果本机 Docker 无法构建 Linux 镜像，优先检查：

- BIOS/固件中是否开启虚拟化
- WSL2 是否可用
- Docker Desktop 后端是否正常启动

## 当前已知状态

- 车队匹配、有效频道筛选、成员状态判断、消息发布失败处理，已经有基础回归测试
- `/admin` 目前仍然没有访问控制，这一点是已知状态，最近没有改动
- README 在部分终端中可能显示乱码，但代码本身可以编译，测试也可通过

## 后续修改建议

- 优先做最小修改，避免无关重构
- 以下文件属于高风险区域，修改前应先读清楚：
  - `services/telegram/chat_service.py`
  - `services/telegram/user_service.py`
  - `db/daos/channel_dao.py`
  - `db/daos/fleet_dao.py`
- Peewee 条件表达式必须使用 `&`，不要误用 Python 的 `and`
- 如果改动了发布/移除逻辑，请同步补充或更新 `tests/services_tests/core_logic_test.py`
- 在未确认本机虚拟化正常前，不要默认 Docker 一定可以成功构建

## 开始修改前的建议检查项

1. 先阅读 `main.py` 和目标模块对应的 service/dao
2. 先跑目标测试，再跑完整测试：`python -m unittest discover -s tests -p '*test.py' -v`
3. 如果改动了导入、字符串或运行路径，补跑 `compileall`
4. 如果改动了 Docker 文档或版本号，确保 README 中的镜像 tag 和 tar 文件名保持一致
