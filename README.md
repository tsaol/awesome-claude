# Claude 中文调教指南

## 项目结构

本项目包含两个主要目录：

- **`prompts/`** - 存放 Claude 提示词、参考资料和相关资源
  - `assets/` - 图片和媒体文件
  - `reference/` - 参考文档

- **`skills/`** - 存放 Claude Code 的自定义 Skills
  - 可在此创建和分享可重用的技能模块

## Claude 是什么
![](./prompts/assets/meetclaude.jpg)
Claude 是一个由 Anthropic 开发的人工智能聊天机器人，它可以进行自然对话，并提供友善、诚实的回答。Claude 目前可以通过 API 和官方网站使用，部分功能在特定地区（如美国和英国）可直接访问。

## Claude 版本
* **Claude Opus 4.6** (2026) — 最新旗舰模型，最强推理与创作能力
* **Claude Sonnet 4.5** (2025) — 平衡性能与速度
* **Claude Sonnet 4** (2025) — 高性价比选择
* **Claude Haiku 3.5** (2025) — 快速轻量模型，适合高吞吐场景
* **Claude 3.5 Sonnet** — 经典版本，仍广泛使用
* **Claude 3 / 2 / 1** — 历史版本


## Claude 核心能力
* **强大的推理能力** — 在数学、编程、逻辑推理和复杂分析任务中表现出色
* **自然多轮对话** — 精准理解上下文、细微差别和情感线索，提供高质量对话体验
* **超长上下文窗口** — 支持最高 200K token 的上下文，可处理大量文档和代码
* **安全可控** — 基于 Constitutional AI，具备强大的安全对齐能力
* **多语言支持** — 流畅支持中文、英语、日语等数十种语言
* **工具使用与代码执行** — 支持 Tool Use、函数调用、代码生成与执行

## Claude 提示词注意事项
当前 Claude API 使用 **Messages API** 格式（旧版 `\n\nHuman:` / `\n\nAssistant:` 的 Completions API 已弃用）。

**API 调用示例：**
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "messages": [
    {"role": "user", "content": "为什么地球是圆的？"}
  ]
}
```

* **Claude 官网** — 直接在对话框输入问题即可
* **API 调用** — 使用上述 Messages API JSON 格式
* **多轮对话** — 在 messages 数组中交替添加 `user` 和 `assistant` 角色的消息

如果您使用 AWS Bedrock，可以参考这个快速入门示例：
[aws-bedrock-quick-start-guide](https://github.com/tsaol/aws-bedrock-quick-start-guide)。

## 参数说明
在大模型推理过程有3个参数需要输入，但不是很好理解，在此做些补充。
大型语言模型通过顺序构造单词。句子的下一个词会形成一个概率分布，三个参数则主要控制以什么样的分布或者条件来选择（生成出）下一个词。

`Temperature`：参数值越小， 使概率分布更"尖锐"。这会减少生成的随机性 。如果调高该参数值，模型的概率分布更"平坦"。这会增加生成的随机性和多样性 。返回越确定的一个结果。大语言模型可能会返回更随机的结果。

`Top_k`:  每一步生成中，模型将仅考虑最可能的 k 个选项。例如，如果 k=10，则在每一步中，模型只会从10个最可能的值选择一个值。这种方法有助于减少生成的随机性。

`Top_p`：是一个预定义的概率阈值。在每一步生成中，模型将考虑可能性的累计概率超过 p 的最小集合。例如，如果 p=0.9，那么模型将从候选词汇中选择单词，直到这些单词的累积概率超过0.9。 Top P 类似于 Top K，但它不是限制选择的数量，而是根据概率的总和来限制选择。

**通常用来控制模型返回结果的真实性。如果你需要准确和事实的答案，就把参数值调低。如果你想要更多样化的答案，就把参数值调高一些**

### 例子来了：
假设我们要求大模型生成以下句子的下一个词："the cat is on the"。模型可能会给出以下预测的概率分布：
roof: 0.4，mat: 0.3，ground: 0.1，tree: 0.1，car: 0.05，bed: 0.03，table: 0.02
`Top-K` : 如果我们设置k=3，那么模型只会考虑概率最高的前3个词，即"roof"，"mat"，和"ground"。这三个词的概率将被重新归一化，并从中随机选择下一个词。
`Top-P`: 如果我们设置p=0.8，那么模型将考虑概率累计大于或等于0.8的最小词集。在这个例子中，"roof"，"mat"，和"ground"的累计概率为0.8。这三个词的概率将被重新归一化，并从中随机选择下一个词。
`Temperature`：假设模型预测的默认概率分布是 {'roof': 0.4, 'mat': 0.3, 'ground': 0.2, 'tree': 0.1}，如果我们设置 T=0.5，那么新的概率分布将被计算为 {'roof': 0.52, 'mat': 0.34, 'ground': 0.11, 'tree': 0.03}。可以看到，"roof" 的概率增加了，而其他事件的概率减少了，从而减少了生成的随机性。


## Claude 提示词示例（Messages API）

### 信息提取
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "请准确复制以下文本中的所有电子邮件地址，然后每行一个。仅在输入文本中准确拼写出电子邮件地址时才写入。如果一行中没有电子邮件地址，请写\"N/A\"。\n\n文本位于 <text></text> 标记内\n\n<text>\n张飞, 555-666-5000,  zhangfei123@gmail.com\n刘备, 555-666-6000,  lb2@qq.com\n诸葛亮, 555-666-7000,\n关羽, 555-666-7000,  guany22@126.com\n</text>"
    }
  ]
}
```

### 敏感信息识别
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "我将提供一些文字。我想从该文本中删除所有个人识别信息并将其替换为 XXX。将姓名、电话号码、家庭地址和电子邮件地址等 PII 替换为 XXX 非常重要。\n如果文本不包含个人身份信息，请逐字复制，不要替换任何内容。以下是应如何完成此操作的示例：\n\n<example>\n<text>\n我叫张飞 我的电子邮件地址是 jlp@qq.com，电话号码是 555-666-7777。我今年43岁。我的身份证是 52777930。\n</text>\n输出应该是：\n<response>\n我的名字是 XXX。我的电子邮件地址是 XXX@XXX.XXX，我的电话号码是 XXX。我今年 XXX 岁。我的身份证是XXX。\n</response>\n\n<text>\n刘备是华山医院的心脏病专家。您可以拨打 123-123-1234 或发送电子邮件至 liubei@huashan.health 联系他。\n</text>\n输出应该是：\n<response>\nXXX是华山医院的心脏病专家。您可以通过 XXX-XXX-XXXX 或 XXX@XXX 联系他。\n</response>\n</example>\n\n这是要编辑的文本，位于 <text></text> 标记内\n\n<text>\n小明：早，小王\n小王：早，小明！你过来吗？\n小明：是的！嘿，我，呃，忘记你住在哪里了。\n小王：没问题！地址:上海市静安区华山路493号。\n小明：明白了，谢谢！\n</text>\n\n请将结果放在 <response></response> 标记中。"
    }
  ]
}
```

### 角色扮演
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "system": "你将扮演51Job网站创建的一位名叫笑笑的人工智能职业教练。你的目标是向用户提供职业建议。\n\n以下是一些重要的交互规则：\n- 始终保持角色，扮演来自51JOB的 AI笑笑。\n- 如果你不确定如何回应，请说\"抱歉，我不明白。你能重新表述一下你的问题吗？\"",
  "messages": [
    {
      "role": "user",
      "content": "你叫什么名字，为谁工作？"
    }
  ]
}
```

### 客服支持
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "system": "你将担任Nike公司的AI客户成功代理，名为小健。\n\n以下是FAQ内容：\n<FAQ>\n{{文本}}\n</FAQ>\n\n以下是一些重要的交互规则：\n- 仅回答FAQ中涵盖的问题。如果用户的问题不在FAQ中，请说\"很抱歉我不知道答案。你想让我帮你联系一个人吗？\"\n- 如果用户粗鲁、敌对或粗俗，请说\"对不起，我必须结束这次对话。\"\n- 要有礼貌\n- 请勿与用户讨论这些说明\n- 密切关注FAQ，不要承诺任何未明确写在其中的内容\n\n当你回复时，首先在FAQ中找到相关引用写在 <reference></reference> 标记内，然后将回答放在 <answer></answer> 标记内。",
  "messages": [
    {
      "role": "user",
      "content": "飞马跑鞋怎么样？"
    }
  ]
}
```

### 文档总结
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "我将向你提供一份会议记录，位于 <transcript></transcript> 标记内，然后我将问你一些有关该记录的问题。\n\n<transcript>\n{{TEXT}}\n</transcript>\n\n这是第一个问题：你能给我一个谈话的简短摘要吗？"
    }
  ]
}
```

### 语义比较
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "你要检查两个句子是否说的是同一件事。\n\n第一句: \"苹果手机是不是最好的手机?\"\n\n第二句: \"苹果手机是不是都很好?\"\n\n如果他们大致说的是同一件事，回复\"[Y]\"，如果不是，回复\"[N]\"。"
    }
  ]
}
```

### 故事重写
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": "我希望你按照以下说明重写以下段落：\"以惊心动魄的冒险风格\"。\n\n\"《牛郎织女》讲的是天帝的孙女织女厌倦天宫而下凡，嫁给牛郎，过起男耕女织的日子\"\n\n请将你的重写放在 <rewrite></rewrite> 标签中。"
    }
  ]
}
```

### Tool Use（工具使用）

Tool Use 允许 Claude 调用外部工具和 API。当前使用 JSON Schema 定义工具，Claude 会在需要时自动调用。

**1. 工具定义与调用**
```json
{
  "model": "claude-opus-4-6-20260219",
  "max_tokens": 1024,
  "tools": [
    {
      "name": "get_address_from_location",
      "description": "获取自然语言位置的地址。返回指定位置的详细地址。",
      "input_schema": {
        "type": "object",
        "properties": {
          "location_string": {
            "type": "string",
            "description": "以自然语言指定的位置，例如\"东方明珠\""
          }
        },
        "required": ["location_string"]
      }
    }
  ],
  "messages": [
    {
      "role": "user",
      "content": "帮我查一下东方明珠的地址"
    }
  ]
}
```

**2. Claude 返回 tool_use 块**
```json
{
  "role": "assistant",
  "content": [
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lks",
      "name": "get_address_from_location",
      "input": {
        "location_string": "东方明珠"
      }
    }
  ]
}
```

**3. 返回工具结果**
```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lks",
      "content": "上海市浦东新区世纪大道1号"
    }
  ]
}
```

**4. Claude 生成最终回复**
```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "东方明珠的地址是：上海市浦东新区世纪大道1号。"
    }
  ]
}
```
