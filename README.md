# alchemy-glyph-router

用于根据主题词或短语，经过最多两次 LLM 调用，生成可直接给视频 AI 使用的中文提示词。

## 安装

```bash
pip install -r requirements.txt
```

## `.env` 配置

只需要配置以下变量名：

```env
LLM_BASE_URL=
LLM_API_KEY=
OPENAI_COMPAT_MODEL=
LLM_TIMEOUT_SECONDS=
LOG_LEVEL=
```

## 运行

```bash
python app.py --theme "剑雨"
```

## 输出

每次运行会：
- 在 `outputs/` 下保存一份 JSON 结果
- 在 `logs/` 下写入简洁日志
- 在终端输出关键日志

## 当前支持的模板

- `A_container`
- `B2_rain`
- `B1_fallback`（命中后优先降级到 `B2_rain`）

## 当前限制

- 当前是 MVP，只做两阶段流程：路由一次、生成一次
- 不做多轮交互、不做复杂 agent、不做复杂调试系统
- 当前完整生成模板只有 `A_container_full` 和 `B2_rain_full`
