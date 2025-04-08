# 价格数据获取工具

本项目提供一组 Python 脚本用于从不同 API 平台获取价格数据并合并处理。

## 脚本功能概览

| 脚本名称                  | 功能描述                 | 运行方式                                                                     | 输出文件                                               |
| ------------------------- | ------------------------ | ---------------------------------------------------------------------------- | ------------------------------------------------------ |
| get_ownedby.py            | 获取 ownedby 数据        | `python get_ownedby.py`                                                      | ownedby.json                                           |
| get_siliconflow_prices.py | 获取硅基流动平台价格数据 | `export SILICONFLOW_API_KEY=your_key`<br>`python get_siliconflow_prices.py`  | siliconflow_prices.json<br>~~siliconflow_models.json~~ |
| get_openrouter_prices.py  | 获取 OpenRouter 价格数据 | `python get_openrouter_prices.py`                                            | openrouter_prices.json                                 |
| merge_prices.py           | 合并所有价格数据         | `python merge_prices.py`                                                     | oneapi_prices.json<br>onehub_only_prices.json          |
| sync_pricing.py           | 同步价格数据             | `python sync_pricing.py [--json_file=path/to/json] [--json_url=url/to/json]` | 更新后的价格表文件                                     |

Note: `sync_pricing.py` 脚本支持通过以下环境变量进行配置，并支持以下参数：

- `--json_file`: 指定 JSON 文件路径
- `--json_url`: 指定 JSON 数据的 URL
- 优先使用 url，其次使用文件

- `ONEHUB_URL`: API 基础 URL
- `ONEHUB_ADMIN_TOKEN`: 管理员认证令牌
- `SYNC_PRICE_OVERWRITE`: 是否覆盖现有价格（默认为 `True`）

## 详细使用说明

### 环境准备

1. 最低要求 Python 3.6+ （github action 需要更高版本，目前使用 3.12）
2. 安装依赖: `pip install -r ../requirements.txt`

### 手动执行流程

```bash
# 1. 设置API密钥(仅Siliconflow需要)
export SILICONFLOW_API_KEY=your_api_key_here

# 2. 按顺序执行所有脚本
python get_ownedby.py
python get_siliconflow_prices.py
python get_openrouter_prices.py
python merge_prices.py
```

### 价格同步流程

```bash
export ONEHUB_URL="https://onehub.your.link" # 仅基础url,不要附带api subpath
export ONEHUB_ADMIN_TOKEN="your_admin_token" # 网页管理后台获得
export SYNC_PRICE_OVERWRITE=True # 是否覆盖现有价格

python src/sync_pricing.py [--json_file=./oneapi_prices.json] [--json_url=https://cdn.jsdelivr.net/gh/Oaklight/onehub_prices@master/oneapi_prices.json]
```

### 自动执行

项目已配置 GitHub Actions 工作流(.github/workflows/run_get_prices.yml)，每日自动执行并提交数据更新。

## 注意事项

1. Siliconflow 脚本需要有效的 API 密钥
2. 合并脚本依赖前三个脚本的输出文件
3. 所有输出 JSON 文件会保存在项目根目录
