# demo-cli

一个极简 Python CLI 开发框架（`pyproject.toml + Typer`）。

## 1) 本地开发（极简）

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

运行：

```bash
demo --help
demo hello
demo hello Alice
demo version
demo config path
demo config init
demo config show
demo config get app.name
demo config set app.name my-cli
```

## 2) GitHub Public 分发 + pip 安装

把仓库公开后，用户可直接安装：

```bash
pip install "git+https://github.com/yourname/demo-cli.git"
```

如果使用 tag（推荐）：

```bash
pip install "git+https://gitee.com/zhaoxuefeng199508/demo-cli.git@v0.1.1"
```

## 3) 极简开发方式

- 所有命令都放在 `src/demo_cli/cli.py`
- 每个命令就是一个 `@app.command()` 函数
- 发布时只改 `pyproject.toml` 的 `version`

## 4) 用户配置文件（不受升级覆盖）

- 默认路径：`~/.demo-cli/config.toml`
- 初始化配置：

```bash
demo config init
```

- 查看配置路径：

```bash
demo config path
```

- 查看配置内容：

```bash
demo config show
```

说明：配置文件在用户主目录，`pip install -U` 升级包不会覆盖这个文件。

## 5) 配置优先级（默认 < 配置文件 < 环境变量）

- 生效顺序：
  - 默认值（代码内置）
  - `~/.demo-cli/config.toml`
  - 环境变量（最高优先级）
- 当前支持环境变量：`DEMO_CLI_APP_NAME`

示例：

```bash
demo config set app.name my-cli
demo hello Alice
# [my-cli] Hello, Alice!

DEMO_CLI_APP_NAME=prod demo hello Alice
# [prod] Hello, Alice!
```

## 6) 新增命令示例

```python
@app.command()
def add(x: int, y: int) -> None:
    typer.echo(x + y)
```

## 7) 可选：发布到 PyPI

```bash
pip install build twine
python -m build
python -m twine upload dist/*
```

发布后用户可直接：

```bash
pip install demo-cli
```
