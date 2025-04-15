# Liars Bar LLM

一个由大语言模型驱动的AI版骗子酒馆对战框架

## 文件结构

程序主要分为两部分，游戏主体和分析工具

Directory Structure
.
├── Core Game Components
│   ├── game.py                    # Main game logic and rules
│   ├── player.py                  # Player behavior and decision making
│   └── llm_client.py             # LLM API integration
├── Record Management
│   ├── game_record.py            # Game state recording
│   └── json_convert.py           # Record format conversion
├── Analysis Tools
│   ├── game_analyze.py           # Game statistics analysis
│   ├── player_matchup_analyze.py # Player matchup analysis
│   └── multi_game_runner.py      # Multiple game execution
├── prompt/                       # LLM prompt templates
│   ├── challenge_prompt_template.txt
│   ├── play_card_prompt_template.txt
│   ├── reflect_prompt_template.txt
│   └── rule_base.txt
└── demo_records/                 # Game record storage
    ├── game_records/            # JSON format records
    ├── converted_game_records/  # Text format records
    └── matchup_records/        # Player matchup analysis

# Key Components

1. **Core Game Components**:
   - `game.py`: Manages game flow, rules, card dealing, and round management
   - `player.py`: Handles player actions, decision making, and interaction with LLMs
   - `llm_client.py`: Interfaces with LLM APIs for player decisions

2. **Game Record Management**:
   - `game_record.py`: Records game states, actions, and outcomes
   - `json_convert.py`: Converts JSON records to readable text format

3. **Analysis Tools**:
   - `game_analyze.py`: Analyzes game statistics and outcomes
   - `player_matchup_analyze.py`: Analyzes player vs player performance
   - `multi_game_runner.py`: Runs multiple games for analysis

4. **Support Directories**:
   - `prompt/`: Contains templates for LLM interactions
   - `demo_records/`: Stores game records in various formats

The system is designed to:
1. Run card games between different LLM models
2. Record detailed game states and decisions
3. Analyze performance and strategies
4. Convert game records to human-readable format
5. Track player matchups and statistics

Each component is modular and serves a specific purpose in the overall game system architecture.

### 游戏主体

`game.py` 骗子酒馆游戏主程序

`player.py` 参与游戏的LLM智能体

`game_record.py` 用于保存和提取游戏记录

`llm_client.py` 用于配置模型接口和发起LLM请求

`multi_game_runner.py` 用于批量运行多轮游戏

### 分析工具

`game_analyze.py` 用于统计所有对局数据

`player_matchup_analyze.py` 用于提取互为对手的AI间的对局记录进行分析

`json_convert.py` 用于将json游戏记录转为可读文本

## 配置

推荐使用 uv 作为包管理工具:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装依赖包：

```bash
uv pip install openai python-dotenv
```

本项目的API配置在`llm_client.py`中。

本项目利用了New API https://github.com/Calcium-Ion/new-api?tab=readme-ov-file 配置了统一的接口调用格式。使用时需自行配置相应模型的API接口。

也可以采用类似的API管理项目One API https://github.com/songquanpeng/one-api 实现统一的接口调用。

## 使用方法

### 运行

完成项目配置后，在`game.py`和`multi_game_runner.py`主程序入口的`player_configs`中设置正确的模型名称

运行单局游戏：
```
python game.py
```

运行多局游戏：
```
python multi_game_runner.py -n 10
```
在`-n`后指定你希望运行的游戏局数，默认为10局

### 分析

游戏记录会以json形式保存在目录下的`game_records`文件夹中

将json文件转为可读性更强的文本格式，转换后的文件会保存在目录下的`converted_game_records`文件夹中

```
python json_convert.py
```

提取所有游戏中AI之间两两对决的对局，转换后的文件会保存在目录下的`matchup_records`文件夹中

```
python player_matchup_analyze.py
```

统计并打印所有的对局数据

```
python game_analyze.py
```

## Demo

项目已将 DeepSeek-R1、o3-mini、Gemini-2-flash-thinking、Claude-3.7-Sonnet 四个模型作为玩家运行了50局，记录存放在`demo_records`文件夹中。

## 已知问题

模型在出牌和质疑阶段的输出可能不稳定，当输出无法满足游戏规定时，会自动重试。如果多次因为输出问题中断运行，可在`player.py`的`choose_cards_to_play`和`decide_challenge`中增加调用大模型的重试次数，或修改`prompt`文件夹中的`play_card_prompt_template.txt`和`challenge_prompt_template.txt`提示词强化对输出格式的限制（可能对模型的推理能力有一定影响）。
