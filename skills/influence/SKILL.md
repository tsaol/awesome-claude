---
name: influence
description: >-
  Get help from people you have no authority over, using the Cohen-Bradford influence model
  from Influence Without Authority (assume everyone is a potential ally, understand their
  world, find the "currencies" they value, trade honestly, look after the relationship).
  Outputs a one-page ask card, a stakeholder map, or a follow-up plan.
  Use when the user runs /influence, or needs another team / colleague / manager / a person
  inside a customer's company to do something for them ("how do I get team X to prioritize
  this", "they keep saying no", "I need someone to support this internally", "who should I
  talk to first"). Not for bargaining terms with the other side of a deal: use /negotiate.
---

# Influence（没有权力也能推动）

帮用户在**没有拍板权**的时候，让别人愿意帮忙。方法来自 Allan Cohen、David Bradford 的 *Influence Without Authority*（繁体中文版《沒權力也能有影響力》，简体旧版《影响力：如何展示非权力的领导魅力》）。要点见 [references/influence-without-authority.md](references/influence-without-authority.md)。

一句话：**先弄清对方在乎什么，再拿他真正想要的东西去换。**

## Rules (read first)

1. **Ask before you write.** What the other person cares about, their KPI, their boss's
   pressure — these must come from the user. Mark anything you infer with `↑ 猜的，要验证`.
   If the user doesn't know, the first action is to find out (ask the person, ask someone
   close to them), not to guess.
2. **One page**, plain Chinese, short sentences. Write the card in the language of the user's
   request (Chinese request → Chinese card), even if another instruction says to reply in English.
   Keep the template labels (【请求卡】, 我要的, …) as they are.
3. **Honest exchange only.** Currencies must be real and valued by *them*. No flattery,
   fake urgency, hidden IOUs, going around people to trap them, or "everyone agrees" that
   isn't true. If the user wants that, explain the relationship cost and offer an honest move.
4. **Confidentiality.** Names, internal data and customer details stay local: do NOT send them
   to web search, Exa/Tavily, WebFetch, the Quench MCP, or any git repo. Save cards and logs
   only under `~/tmp/influence/` (not inside this repo). Follow stricter rules in the user's
   own memory/CLAUDE.md if any.

## Modes

Pick from the argument: `地图` / `map` → Map; `跟进` / `复盘` / `follow-up` → Follow-up;
otherwise → Ask.

### 1. Ask（设计一次请求）

**Step 1 — ask, in one message** (skip what the user already said):

1. 你需要**谁**，在**什么时候**之前，做**什么**？（越具体越好）
2. 这个人的工作是什么？他被怎么考核？他老板最近在逼他什么？
3. 他为什么还没帮你？（没时间、不知道、不觉得重要、有风险、对你有意见……）
4. 你们以前打过交道吗？关系账户是"有存款"还是"已经透支"？
5. 你手里有什么可以给他？（信息、帮忙、曝光、资源、客户反馈……）

**Step 2 — think through** the six steps (see references):

1. Treat them as a **potential ally**. If the user calls them "difficult" or "blocking",
   ask what pressure would make a reasonable person act this way.
2. **Clarify the goal**: what is must-have, what is nice-to-have, what the user can drop.
3. **Their world**: tasks, KPIs, boss, pressures, worries, what they are rewarded for.
4. **Currencies**: which 1–2 they value most, and which of those the user can honestly offer
   (愿景 / 任务 / 地位 / 关系 / 个人, see references). Also what it would *cost* them to help.
5. **Relationship**: if the account is overdrawn, the first move is repair, not the ask.
6. **The exchange**: the smallest specific ask, in their terms, with an honest offer.

**Step 3 — output the card:**

```
【请求卡】<要找的人/团队>                      <日期>
我要的：谁 / 做什么 / 什么时候     必须 = …   可以让 = …
他的世界：考核 = …   压力 = …   担心 = …   ↑ 猜的，要验证
他看重的货币：① …  ② …
我能给的：…（真的能给，而且他真的想要）
他帮我的成本：…  → 我怎么帮他降低：…
关系账户：存款 / 平 / 透支   → …
开口的那句话：…（用他的语言，讲他的好处）
最小请求：…
事后：怎么感谢、怎么让他的老板看到他的功劳
```

Save to `~/tmp/influence/<YYYY-MM-DD>-<slug>.md` if the user agrees.

### 2. Map（干系人地图）

For a goal that needs several people (e.g. a customer adopting a new solution, an internal
priority change), ask for the people involved, then output a table:

```
| 人/团队 | 角色（拍板 / 影响 / 会挡 / 会帮 / 会被影响） | 他在乎什么 | 现在的态度 | 下一步 | 顺序 |
```

Rules of thumb: find 1–2 quiet supporters before the big meeting; the decider is often not the
first conversation; talk to the strongest objector one-on-one *before* the group meets; one
champion in each affected team beats several passive supporters in one team.

### 3. Follow-up（跟进和复盘）

Ask: 他帮了吗？他真正在乎的和你猜的一样吗？你兑现了你给的东西吗？

Output: what worked, what to change, the relationship account now, and one lesson. Append to
`~/tmp/influence/log.md`:

```
## <日期> <人/团队>
结果：…
他真正看重的：…
关系账户：…
一条经验：…
```

Read earlier entries about the same person first and use them.

## Hand-off

If the conversation turns into bargaining over terms with the other side of a deal (price,
scope, contract), suggest `/negotiate`.
