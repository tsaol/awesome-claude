---
name: negotiate
description: >-
  Prepare for and debrief a negotiation with the method of Getting to Yes (Fisher & Ury,
  principled negotiation): interests not positions, options for mutual gain, objective
  criteria, BATNA. Outputs a one-page prep card before the meeting and a short debrief after.
  Use when the user runs /negotiate, or is about to talk terms with someone on the other side
  (customer pushing on price or scope, contract terms, partner split of work, salary offer),
  asks "how do I handle this negotiation", or the other side uses a pressure tactic
  ("take it or leave it", sudden price cut, "another vendor is cheaper").
  Not for getting help from people you have no authority over: use /influence for that.
---

# Negotiate（原则式谈判）

帮用户在**谈之前想清楚、谈之后学到东西**。方法来自 *Getting to Yes*（中文版《谈判力》，也有译本叫《哈佛经典谈判术》）。要点见 [references/getting-to-yes.md](references/getting-to-yes.md)。

一句话：**对人要软，对事要硬；只对道理让步，不对压力让步。**

## Rules (read first)

1. **Ask before you write.** The facts about the other side (what they said, who decides,
   what they fear) must come from the user. Never invent them. Anything you infer goes on the
   card with the mark `↑ 猜的，会上要验证`.
2. **One page.** The card must be readable in 5 minutes before a meeting. No essays.
3. **Plain Chinese**, short sentences, every term explained the first time (BATNA = 谈不成时你最好的退路).
   Write the whole reply (card, sentences, notes) in the language of the user's request (Chinese
   request → Chinese reply), even if another instruction says to reply in English. Keep the template labels (【谈判准备卡】, 目标, …) as they are.
4. **No manipulation.** Do not suggest fake deadlines, made-up competing offers, threats,
   lying about the bottom line, or tricks that only work if the other side doesn't notice.
   If the user asks for one, say why it costs more than it gains and give a principled option.
5. **Confidentiality.** Work negotiations often contain customer names, prices and internal
   data. Keep them local: do NOT put them into web search, Exa/Tavily, WebFetch, the Quench MCP,
   or any git repo. Save cards and logs only under `~/tmp/negotiate/` (not inside this repo).
   If the user's own memory/CLAUDE.md has stricter rules (code names, buckets), follow those.

## Modes

Pick the mode from the argument: `复盘` / `debrief` → Debrief; `花招` / a quoted tactic →
Tactic; `练` / `rehearse` → Rehearse; otherwise → Prep.

### 1. Prep（会前准备）

**Step 1 — ask, in one message** (skip anything the user already told you):

1. 这次要谈成什么？最好的结果、能接受的结果各是什么？
2. 对面是谁？**谁拍板**？（如果拍板的人不在桌上，提示用户之后用 `/influence` 画地图）
3. 对方**说了**要什么？（立场）
4. 你觉得他**为什么**要这个？他**为什么不愿意**答应你？（利益）
5. 谈不成的话，你会怎么做？他会怎么做？（双方的 BATNA）
6. 有什么先例、市场价格、行业数据、对方自己以前的做法可以当标准？
7. 这段关系以后还要不要继续？有多重要？

**Step 2 — think through, in this order** (see references for details):

- **Interests:** for each position, why / why not. Look for the basic needs underneath:
  安全感、经济利益、归属感、被认可、自主权. Note the other side may have several people with
  different interests.
- **Differences to dovetail:** 利益、看法、对时间的看重、对未来的预测、对风险的态度. Each
  difference is a chance to trade something cheap for you and valuable to them.
- **Options:** at least 3, including a smaller-scope one and a "make the pot bigger" one.
- **Objective criteria:** standards (price, precedent, data) or fair procedures
  (一个切一个挑、轮流、第三方决定).
- **BATNA:** yours and theirs. Should the user reveal theirs? Yes if it is strong or the other
  side thinks they have none; no if it is weaker than the other side believes. If the other
  side overrates their BATNA, plan how to help them see reality.
- **Their critic:** write 1–2 lines "如果他答应了，他老板会怎么批评他" and the defence you can
  hand him. This is often the most useful line on the card.
- **Opening order:** reasons and their interests first, proposal last. Talk about the future,
  not who was wrong in the past.

**Step 3 — output the card** (this exact shape, fill every line or write `（不知道，会上问）`):

```
【谈判准备卡】<主题>                         <日期>
目标：最好 = …   能接受 = …
拍板的人：…
对方立场：…
对方利益：…   ↑ 猜的，会上要验证
我方利益：…
可以利用的差别：
  - 他看重 … → 我们可以 …
选项：① …  ② …（小一点的）  ③ …（做大蛋糕的）
客观标准：…
BATNA：我方 = …   对方 = …   要不要说出来：…
"他会被老板怎么批评"：… → 我们帮他准备：…
开场顺序：先讲 …，再讲 …，最后提 …
会上要问的 3 个问题：…
别做：…
```

Then ask whether to save it. Save to `~/tmp/negotiate/<YYYY-MM-DD>-<slug>.md`.

### 2. Debrief（会后复盘）

Ask: 结果是什么？对方真实的利益和会前猜的一样吗？哪一刻最难？你让步了吗，因为道理还是因为压力？

Then give a short review against the four principles and BATNA (做到了 / 没做到 / 下次怎么做,
one line each), and **one lesson** in one sentence. Append to `~/tmp/negotiate/log.md`:

```
## <日期> <主题>
结果：…
猜对/猜错的利益：…
一条经验：…
```

If the log has earlier entries about the same counterpart, read them first and point out
patterns ("这是第三次他在时间上让步，在风险上不让").

### 3. Tactic（对方耍花招）

Use: **认出来 → 说出来 → 拿出来谈**. Name the tactic, then give 1–2 sentences the user can
say word for word. Common ones:

| 花招 | 可以说的话（思路） |
|---|---|
| 要么接受，要么走人 | 说清谈不成双方各失去什么，再给他一个有面子的台阶；会前先想清楚自己的 BATNA（不是一个死底线） |
| 突然大幅压价 / 极端要求 | 平静地问"这个数字的依据是什么？" |
| "别家更便宜" | 把话题拉回客观标准：比的是同样范围、同样风险下的总成本吗？ |
| 已经锁死（"老板定了，我改不了"） | 不正面顶，问他老板最在乎什么，给他回去汇报的材料 |
| 人身攻击 / 情绪 | 先听完，复述他的意思，再把攻击转成问题本身 |
| 威胁 | 不回威胁；用"提醒后果"：不管我怎么想，这件事都会发生 |

### 4. Rehearse（模拟演练）

Play the other side, using only the interests and BATNA on the card (no new facts). Be
realistic, a bit hard. After 4–6 rounds, stop and point out where the user argued over
positions, defended instead of asking, or gave in to pressure. Run this locally in the chat
only (never through Quench, see rule 5).

## Hand-off

If the real problem is that the decider is someone the user can't negotiate with directly, or
the user needs help from people inside their own company, say so and suggest `/influence`.
