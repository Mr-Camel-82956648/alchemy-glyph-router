# alchemy-glyph-router

一个面向“暗黑炼金风 2.5D 技能特效提示词生成”的轻量模板路由系统。当前版本坚持最多两次 LLM 调用：第一次做模板路由，第二次基于完整模板生成成品中文提示词；同时保留简洁日志、模板文件、环境变量配置和本地 smoke test，方便继续做小步迭代。

## 当前目标

- 维持轻量、可调试、工程化的模板路由流程。
- 当前主流程固定为两段：`route_theme` 一次，`generate_prompt` 一次。
- 优先巩固 A-F 主模板树的稳定性，不继续轻易扩类。

## 当前正式模板树

- `A`｜内聚型容器领域：主题核心是一个贴地展开的完整区域本体，重点是边界、内部能量面和整体气质成立，而不是强事件打击。
- `B1`｜单体降临裁决型：一个中央唯一主打击体从高处垂直降临，在区域内完成一次明确主命中或镇压。
- `B2`｜连续覆盖打击型：多个打击体在同一受击域内从上到下连续覆盖，重点是时间连续的洗地区域打击。
- `C`｜地涌生成型：结构或能量从地面内部向上生成、破土、裂出、喷涌，重点是自下而上的生成事件。
- `D`｜轨迹穿行型：某种意象在边界内沿路径穿行、回旋、掠过并留痕，重点是轨迹事件而不是区域本体。
- `E`｜爆发脉冲型：边界内部发生一次短促而受控的爆发、震爆、脉冲释放，重点是瞬时释放事件。
- `F`｜召现驻场型：一个单体主体在边界内部显现、落位并短暂停驻，重点是单体召现与存在感。

正式主流程当前对应的模板文件为：
- `templates/cards/A_container.md` 到 `templates/cards/F_manifest.md`
- `templates/full/A_container_full.md` 到 `templates/full/F_manifest_full.md`

## 当前不纳入正式能力的内容

- `G`｜群体构筑型：已做过探索，但当前稳定性不足，暂不纳入正式模板树。
- 若文件仍保留：[`templates/cards/G_construct.md`](</d:/projects/alchemy-glyph-router/templates/cards/G_construct.md>) 与 [`templates/full/G_construct_full.md`](</d:/projects/alchemy-glyph-router/templates/full/G_construct_full.md>) 仅作为实验性遗留参考，不参与当前正式路由、正式映射或正式 smoke test 口径。

## 当前项目状态

- A-F 主模板树已完成阶段性收束，并经过多轮联调。
- 当前系统可以稳定处理一批常见技能主题的路由与生成。
- 后续优化更适合继续做子题材补丁、路由词补充、边界收束和模板细修，而不是继续扩展新的主类别。

## 安装

```bash
pip install -r requirements.txt
```

## 环境变量

在项目根目录放置 `.env`，至少配置以下变量：

```env
LLM_BASE_URL=
LLM_API_KEY=
OPENAI_COMPAT_MODEL=
LLM_TIMEOUT_SECONDS=
LOG_LEVEL=
```

## 使用方式

基本运行命令：

```bash
python app.py --theme "剑雨"
```

执行后会：
- 在 `outputs/` 生成一份 JSON 结果。
- 在 `logs/app.log` 写入本次运行日志。
- 在终端输出关键日志字段。

## 日志与输出字段

常见字段包括：
- `route_selected`：路由阶段选中的正式模板代号。
- `route_reason`：路由原因的简短中文说明。
- `fallback_applied`：是否实际应用了 fallback。
- `final_template`：最终用于生成的 full template。
- `route_elapsed_ms`：路由耗时。
- `generation_elapsed_ms`：生成耗时。
- `total_elapsed_ms`：总耗时。
- `model`：实际调用的模型名。
- `output`：本次运行生成的结果文件路径。

## Smoke Test

运行本地 smoke test：

```bash
python smoke_test.py
```

当前 smoke test 以 A-F 正式主模板树为准，不把 G 作为正式通过口径的一部分。

## 阶段说明

- 本阶段完成了 A-F 主模板树收束。
- G 已暂停，不纳入正式流程，只保留实验性遗留文件。
- 当前版本适合作为一次阶段性里程碑，用于继续做稳定性修整和小范围补丁。
