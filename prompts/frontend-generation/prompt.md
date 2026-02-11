# AWS GPU 实例对比网站 - UI 改善方案

## 📚 参考资料

**文章来源：** [AI画的产品页面太难看了，我搓了个提示词让它秒变设计大师](https://www.woshipm.com/ai/6247928.html)

**作者：** 云舒
**发布时间：** 2025-07-28

---

## 🎯 核心方法论

### 提示词工程的关键要素

1. **明确的设计目标**
   - 定义项目类型和受众
   - 明确设计风格参考（如：AWS 官网、Linear.app）

2. **详细的设计规范**
   - 视觉规范：配色、字体、间距、圆角
   - 技术规范：框架选择、性能要求

3. **交互式引导流程**
   - 采用多轮对话，而非一次性输入
   - 逐步细化需求，让 AI 主动提问

4. **具体的技术实现细节**
   - 明确保留的元素和数据
   - 明确技术栈和限制条件

---

## 🚀 应用到 aws-gpu 项目的方案

### 方案 A：结构化提示词（推荐）

使用以下提示词模板与 Claude Code 进行多轮对话：

```
我有一个 AWS GPU 实例对比网站（/home/ubuntu/codes/aws-gpu/index.html），
当前是静态表格展示。请作为产品设计大师，帮我重新设计：

**设计目标：**
- 专业的云服务产品展示页面
- 参考 AWS 官网风格 + 现代化数据表格设计
- 保持所有现有数据和功能

**必须保留的元素：**
- P 系列、G 系列 GPU 实例数据（36 行数据）
- AWS 自研芯片 Trainium/Inferentia 数据
- 客户案例表格
- 工作负载标签（训练/推理）
- 区域标签（Global/China）

**改进方向（请逐步询问我）：**
1. 视觉设计：配色方案、卡片 vs 表格、间距优化
2. 交互功能：是否需要筛选、搜索、实例对比功能？
3. 响应式设计：移动端优化
4. 数据可视化：是否添加价格对比图表、性能雷达图？

**技术要求：**
- 纯 HTML + CSS（或建议升级到 Tailwind？）
- 不依赖 React/Vue 等框架（除非我同意）
- 保持轻量级，加载速度快

请先问我：您最想改进的是哪个方面？
```

---

### 方案 B：直接优化（快速实施）

#### 视觉优化
- ✅ 添加渐变背景和玻璃态效果（Glassmorphism）
- ✅ 优化表格间距和可读性
- ✅ 添加 hover 动画和交互效果
- ✅ 响应式布局优化（移动端适配）
- ✅ 深色模式切换

#### 功能增强
- ✅ 实例搜索功能（按名称/GPU 型号）
- ✅ 筛选器（按工作负载、区域、GPU 数量、价格范围）
- ✅ 价格排序功能（升序/降序）
- ✅ 对比模式（选择 2-4 个实例并排对比）
- ✅ 快速定位功能（跳转到 P 系列、G 系列、自研芯片）

#### 数据展示
- ✅ 顶部统计卡片
  - 总实例数量
  - 最新发布实例
  - 价格区间
  - 支持区域数
- ✅ 可折叠分组（按代际或用途分组）
- ✅ 实例详情页优化（点击实例名称展开更多信息）

---

## 🎨 设计风格参考

### 推荐配色方案

**AWS 官方风格：**
- 主色：`#232F3E`（深蓝灰）
- 强调色：`#FF9900`（橙色）
- 背景：`#F5F5F5`（浅灰）
- 文字：`#16191F`（深灰黑）

**现代化方案（Glassmorphism）：**
- 主色：`#1E293B`（石板蓝）
- 次要色：`#F8FAFC`（浅白）
- 玻璃态效果：`rgba(255, 255, 255, 0.1)` + `backdrop-filter: blur(10px)`
- 渐变背景：`linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

### 布局参考

- **AWS 官网：** 简洁、专业、大量留白
- **Linear.app：** 现代、扁平、微交互动画
- **Notion：** 清晰的层级结构、舒适的阅读体验

---

## 📐 设计规范（从 index.html 提取）

### 圆角规范

| 元素类型 | 圆角大小 | 说明 |
|---------|---------|------|
| 大容器/Section | `20px` | header, section, 主要卡片 |
| 中等卡片 | `16px` | stat-card, toolbar |
| 输入框/按钮 | `10-12px` | search input, filter-select |
| 标签 (胶囊形) | `20px` | tag, quick-nav-btn |
| 小元素 | `6px` | 链接悬停背景, 小按钮 |

### 间距规范

| 元素 | 间距 | 说明 |
|-----|------|------|
| 容器内边距 | `20-30px` | section padding |
| 卡片内边距 | `20-24px` | stat-card padding |
| 元素间距 | `16px` | gap between cards |
| 表格单元格 | `14-16px` | td/th padding |
| 组件间距 | `25px` | section margin-bottom |

### 字体规范

```css
/* 主字体 */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* 代码/实例名 */
font-family: 'Fira Code', monospace;

/* 字号层级 */
--font-xs: 0.78rem;   /* 标签 */
--font-sm: 0.85-0.9rem; /* 辅助文字 */
--font-base: 0.92-0.95rem; /* 正文 */
--font-lg: 1.5rem;    /* Section 标题 */
--font-xl: 1.8rem;    /* 统计数字 */
--font-2xl: 2.2rem;   /* 主标题 */
```

### 阴影规范

```css
/* 玻璃态阴影 */
--glass-shadow: 0 8px 32px rgba(31, 38, 135, 0.12);

/* 悬停增强阴影 */
--hover-shadow: 0 12px 40px rgba(31, 38, 135, 0.18);
```

### 过渡动画

```css
/* 默认过渡 */
transition: all 0.2s ease;

/* 背景/颜色过渡 */
transition: background 0.3s ease, color 0.3s ease;

/* 悬停上浮效果 */
transform: translateY(-3px);
```

### 标签颜色编码

| 标签类型 | 背景色 | 文字色 |
|---------|-------|-------|
| Training (训练) | `#f3e5f5` | `#7b1fa2` |
| Inference (推理) | `#e8f5e9` | `#2e7d32` |
| Global (全球) | `#e3f2fd` | `#1565c0` |
| China (中国) | `#fff3e0` | `#e65100` |

### 深色模式变量

```css
[data-theme="dark"] {
  --primary-bg: #0f172a;
  --glass-bg: rgba(30, 41, 59, 0.8);
  --glass-border: rgba(255, 255, 255, 0.08);
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --card-bg: rgba(30, 41, 59, 0.9);
}
```

---

## 📝 实施步骤

### Step 1: 评估现状
```bash
# 查看当前文件结构
ls -lh /home/ubuntu/codes/aws-gpu/
```

当前状态：
- ✅ 静态 HTML + CSS
- ✅ 表格式数据展示
- ✅ 基础响应式设计
- ❌ 无交互功能
- ❌ 无数据筛选
- ❌ 无可视化图表

### Step 2: 选择技术方案

**选项 1：保持纯静态（推荐）**
- HTML + CSS + Vanilla JavaScript
- 优点：轻量、快速、无依赖
- 适合：当前项目规模

**选项 2：引入 Tailwind CSS**
- 需要 npm + build 流程
- 优点：快速开发、一致的设计系统
- 适合：未来扩展需求

**选项 3：升级到 React/Next.js**
- 需要重构整个项目
- 优点：组件化、动态数据加载
- 适合：需要复杂交互和后端集成

### Step 3: 渐进式改进

**第一阶段：视觉优化（1-2 小时）**
1. 更新配色方案
2. 优化字体和间距
3. 添加 hover 效果
4. 响应式优化

**第二阶段：功能增强（2-4 小时）**
1. 添加搜索框（JavaScript 实现）
2. 添加筛选器（下拉菜单）
3. 添加排序功能（点击表头）

**第三阶段：高级功能（4-8 小时）**
1. 实例对比功能
2. 数据可视化图表（Chart.js）
3. 深色模式切换
4. 动画和微交互

---

## 💡 提示词模板库

### 模板 1：视觉优化

```
优化 /home/ubuntu/codes/aws-gpu/index.html 的视觉设计：

1. 配色方案：使用 AWS 官方配色（#232F3E + #FF9900）
2. 表格优化：增加行高、优化对齐、添加斑马纹
3. 添加效果：hover 高亮、平滑过渡动画
4. 响应式：移动端自动切换为卡片布局

要求：
- 只修改 CSS，不改变 HTML 结构
- 保持所有现有功能
- 代码注释清晰
```

### 模板 2：功能增强

```
为 /home/ubuntu/codes/aws-gpu/index.html 添加交互功能：

功能需求：
1. 搜索框：实时过滤实例（按名称或 GPU 型号）
2. 筛选器：
   - 工作负载（训练/推理）
   - 区域（Global/China）
   - GPU 数量范围（1-8, 8+）
3. 排序功能：点击表头按价格/GPU 数量排序

技术要求：
- 使用 Vanilla JavaScript（不引入框架）
- 不破坏现有样式
- 添加清空筛选按钮
- 显示筛选结果数量
```

### 模板 3：数据可视化

```
为 /home/ubuntu/codes/aws-gpu/index.html 添加数据可视化：

需求：
1. 顶部统计卡片：总实例数、最新发布、价格区间
2. 价格对比柱状图（Chart.js）：横向对比各系列平均价格
3. GPU 性能雷达图：对比 P5/P6/G5/G6 的性能指标

设计要求：
- 图表配色与网站主题一致
- 响应式图表（移动端自适应）
- 可交互（hover 显示详细数据）
```

---

## 🔗 相关资源

### 设计灵感
- [AWS 官网](https://aws.amazon.com/)
- [Linear.app](https://linear.app/)
- [Notion](https://www.notion.so/)
- [Tailwind UI](https://tailwindui.com/)

### 技术工具
- [Chart.js](https://www.chartjs.org/) - 图表库
- [Alpine.js](https://alpinejs.dev/) - 轻量级 JavaScript 框架
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架
- [instances.vantage.sh](https://instances.vantage.sh/) - AWS 实例数据源

### 提示词工程
- [Claude Prompt Library](https://docs.anthropic.com/claude/prompt-library)
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)

---

## 📊 改进效果评估

### 评估指标

**视觉体验：**
- [ ] 配色是否统一、专业
- [ ] 间距是否舒适
- [ ] 移动端是否友好

**功能性：**
- [ ] 用户能否快速找到目标实例
- [ ] 筛选和搜索是否流畅
- [ ] 数据对比是否清晰

**性能：**
- [ ] 页面加载时间 < 2 秒
- [ ] 交互响应时间 < 100ms
- [ ] 文件大小是否合理

---

## 🚧 待完成任务

- [ ] 与 AI 进行多轮对话，细化设计需求
- [ ] 实施视觉优化（配色、间距、动画）
- [ ] 添加搜索和筛选功能
- [ ] 添加实例对比功能
- [ ] 添加数据可视化图表
- [ ] 移动端适配测试
- [ ] 性能优化和代码压缩

---

**最后更新：** 2025-12-21
**维护者：** Claude Code
