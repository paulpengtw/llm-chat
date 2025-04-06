# AI Debate Framework

一个由大语言模型驱动的AI辩论对战框架

## 文件结构

程序主要分为两部分，游戏主体和分析工具

### 游戏主体

`game.py` 辩论游戏主程序

`player.py` 参与辩论的LLM智能体

`game_record.py` 用于保存和提取辩论记录

`llm_client.py` 用于配置模型接口和发起LLM请求

`multi_game_runner.py` 用于批量运行多轮辩论

### 分析工具

`game_analyze.py` 用于统计所有辩论数据

`player_matchup_analyze.py` 用于提取互为对手的AI间的辩论记录进行分析

`json_convert.py` 用于将json辩论记录转为可读文本

## 配置

使用 uv 安装相应依赖包：

```bash
# 如果没有安装 uv，先安装 uv
pip install uv

# 使用 uv 安装依赖
uv pip install openai
```

```
pip install openai
```

本项目的API配置在`llm_client.py`中。

本项目利用了New API https://github.com/Calcium-Ion/new-api?tab=readme-ov-file 配置了统一的接口调用格式。使用时需自行配置相应模型的API接口。

也可以采用类似的API管理项目One API https://github.com/songquanpeng/one-api 实现统一的接口调用。

## Configuration
1. Create a copy of `llm_client.py.example` (if exists) to `llm_client.py`
2. Add your API keys and endpoints in `llm_client.py`
3. Configure your preferred models in `player_configs` within `game.py` or `multi_game_runner.py`

## 使用方法

### 运行

完成项目配置后，在`game.py`和`multi_game_runner.py`主程序入口的`player_configs`中设置正确的模型名称

运行单场辩论：
```
python game.py
```

运行多场辩论：
```
python multi_game_runner.py -n 10
```
在`-n`后指定你希望运行的辩论场次，默认为10场

### 分析

辩论记录会以json形式保存在目录下的`game_records`文件夹中

将json文件转为可读性更强的文本格式，转换后的文件会保存在目录下的`converted_game_records`文件夹中

```
python json_convert.py
```

提取所有辩论中AI之间两两对决的记录，转换后的文件会保存在目录下的`matchup_records`文件夹中

```
python player_matchup_analyze.py
```

统计并打印所有的辩论数据

```
python game_analyze.py
```

## Demo

项目已将 DeepSeek-R1、o3-mini、Gemini-2-flash-thinking、Claude-3.7-Sonnet 四个模型作为辩论者运行了50场，记录存放在`demo_records`文件夹中。

## 已知问题

模型在陈述观点和质疑阶段的输出可能不稳定，当输出无法满足辩论规定时，会自动重试。如果多次因为输出问题中断运行，可在`player.py`的`choose_cards_to_play`和`decide_challenge`中增加调用大模型的重试次数，或修改`prompt`文件夹中的`play_card_prompt_template.txt`和`challenge_prompt_template.txt`提示词强化对输出格式的限制（可能对模型的推理能力有一定影响）。

## 游戏规则

每场辩论包含以下要素：
- 每位参与者获得立场牌（Support/Oppose/Neutral）
- 随机选择辩论主题（如AI伦理、气候变化等）
- 轮流陈述观点并使用立场牌
- 可对其他参与者的论证提出质疑
- 通过10轮辩论展示逻辑思维和论证能力

参与者需要：
1. 合理运用立场牌构建论证
2. 分析对手的论证是否合理
3. 在适当时机提出质疑
4. 展现对复杂话题的理解

游戏过程会记录每位参与者的表现，包括论证方式、立场选择和互动策略，以评估AI在结构化辩论中的表现。
