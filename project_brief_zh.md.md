# Netflix 内容目录策略分析

一个面向商业场景的深度数据分析项目，基于 Netflix 公开片库数据集构建，用于展示我在 Data Analysis 方向上的项目能力，并作为 Codex 辅助执行的项目蓝图。

---

## 1. 项目定位

这不是一个普通的 EDA notebook。  
这是一个**面向商业问题的内容目录（content catalog）分析项目**，目标是利用 Netflix 的公开片库元数据，回答更接近真实业务的问题，例如：

- Netflix 的内容供给结构到底是什么样的？
- 它的片库更偏向全球化供给，还是集中在少数国家/地区？
- 平台内容扩张的节奏，随着时间是如何变化的？
- 哪些内容类别明显过度集中，哪些则相对稀缺？
- 从片库结构中，能否提炼出关于内容广度、成熟度、集中度和组合策略的信号？

这个项目的目标，不是证明我“会做几张图”，而是证明我能做更接近商业环境的数据分析工作：

- 定义业务问题
- 把脏乱字段处理成可分析的数据结构
- 设计真正有用的指标
- 产出面向决策的信息
- 明确说明数据边界和不能支持的结论

---

## 2. 当前 notebook 已经做了什么

现有 notebook 主要包含：

- 基础数据读取
- 缺失值检查
- 重复值检查
- 简单的日期解析
- type 和 rating 的 countplot
- pie chart
- 针对 country / cast / director / categories 的词云

这些作为起点没问题，但本质上仍然只是**表层 EDA**。

### 当前 notebook 的主要问题

- 把探索过程和最终展示混在一起，结构不清晰
- 对缺失值删除过于激进，容易让后续分析产生偏差
- 把 `country`、`cast`、`listed_in` 这类多值字段当成普通字符串处理，而没有正规化
- 更关注“画图”，而不是“定义可用于决策的指标”
- 没有明确业务问题，也没有决策语境
- 容易说过头，因为这个数据集只有目录元数据，没有真实业务表现数据

---

## 3. 关键约束：这份数据能支持什么，不能支持什么

在打开 Codex 之前，必须先把这件事钉死。

### 这份数据**可以支持**的分析

- 内容目录结构分析
- 内容供给组合分析
- 地域覆盖与国际化分布分析
- 类型 / 类别结构分析
- 内容年龄、近期性、库龄、新鲜度分析
- Movie vs TV Show 结构分析
- 分级（maturity rating）结构分析
- 导演 / 演员 / 国家之间的网络关系分析
- 内容组合的集中度 / 多样性分析

### 这份数据**不能直接支持**的分析

- viewership（观看量）
- watch time（观看时长）
- retention（留存）
- conversion（转化）
- revenue（收入）
- title-level popularity（单片受欢迎程度）
- customer lifetime value
- recommendation performance

所以，这个项目必须被表述为：

> **Netflix 内容目录策略分析**  
> 而不是用户行为分析，更不是业务表现归因分析。

这一点如果不守住，整个项目会立刻变弱，因为你会开始对数据根本不支持的东西做假推断。

---

## 4. 适合放作品集的项目目标

### 推荐标题

**从基础 EDA 到商业分析：深入理解 Netflix 的内容目录策略**

### 推荐一句话简介

本项目基于 Netflix 公开内容目录元数据，分析其片库结构、本地化与国际化模式、内容新鲜度以及内容组合策略，采用更接近商业数据分析而不是 Kaggle 式可视化展示的方法来组织分析流程和产出结论。

---

## 5. 推荐的最终交付物

项目最终最好包含四层输出：

### A. Executive Summary

一份简明结论，回答：

- 最重要的 5–8 个发现是什么？
- 这些发现为什么对流媒体业务有意义？
- 它们可能支持什么样的决策？

### B. 可复现的分析 notebook

建议拆成多个 notebook，而不是把所有内容堆在一个文件里：

- `01_data_audit.ipynb`
- `02_feature_engineering.ipynb`
- `03_business_analysis.ipynb`
- `04_segmentation_and_networks.ipynb`
- `05_executive_summary.ipynb`

### C. 干净的分析表与资产

- cleaned master table
- normalized bridge tables
- KPI tables
- chart-ready outputs

### D. 适合个人主页展示的项目页面

用于个人网站时，应包含：

- 项目简介
- 用到的方法
- 3–5 张最强图表
- 商业含义
- 局限性与下一步方向

---

## 6. 打开 Codex 之前需要准备什么

下面是实际开工前必须做的准备。

### 6.1 先定义业务 framing

先用一段话写清楚：

- 这个项目的目标读者是谁？  
  例如：DA / BI / Analytics 岗位的 hiring manager
- 我想让别人觉得我是哪类 analyst？  
  例如：能够把模糊问题结构化、面向业务沟通的 analyst
- 我分析时站在什么决策视角？  
  例如：内容组合策略、片库规划、本地化供给策略

如果这一步没做，Codex 只会帮你写更多代码，不会帮你做出更强的项目。

### 6.2 先列出严格的问题清单

不要从“先看看数据”开始。  
要从一组优先级明确的问题开始。

### 推荐的核心问题

#### 内容组合结构

- Catalog 在 Movies 和 TV Shows 之间是怎么分布的？
- 两类内容的 genre / category 结构有什么差异？
- 这个片库是否被少数大类内容主导？

#### 新鲜度与上架时滞

- 整体片库有多“新”？
- 内容从原始发行到被加入 Netflix，中间相隔多久？
- 哪些类别 / 国家对应的内容更“新”，哪些更“旧”？

#### 本地化与国际化覆盖

- 哪些国家在目录中占主导？
- Netflix 的片库更像是集中于少数国家，还是广泛国际化？
- 哪些 genre 更本地化，哪些更全球化？

#### 受众与分级定位

- maturity rating 的结构反映了怎样的目标受众定位？
- 是否存在某些国家 / genre 更偏成熟向内容？

#### 集中度与多样性

- 片库在 top countries、top genres、top directors、top cast 上集中到什么程度？
- 它到底是“广而浅”的组合，还是围绕少数生产生态系统高度集中？

#### 结构关系

- 哪些 country、genre、rating、type 组合最常一起出现？
- 是否存在具有明显业务含义的 title cluster？

### 6.3 在编码前先决定实体模型

这份数据里有多个逗号分隔的多值字段。  
如果不先正规化，你的分析深度基本上上不去。

建议的数据模型如下：

### 基础表

`titles`

- `show_id`
- `title`
- `type`
- `release_year`
- `date_added`
- `rating`
- `duration`
- `description`

### Bridge tables

`title_country`

- `show_id`
- `country`

`title_genre`

- `show_id`
- `genre`

`title_cast`

- `show_id`
- `cast_member`

`title_director`

- `show_id`
- `director`

这一步非常关键，因为它直接体现你是不是懂真正的数据分析建模，而不只是会写 pandas。

### 6.4 提前确定清洗规则

当前 notebook 对缺失值删得太狠，这不是一个好的默认方案。

应该先写清楚 cleaning spec：

- 保留原始数据，不直接改动
- 基于规则创建 cleaned analysis table
- 不能因为 `director` 或 `cast` 缺失就整行删除
- 小心解析 `date_added`
- 标准化空格和分隔符
- 拆分多值字段
- 对 `country` / `cast` / `director` 的缺失，在合适场景下保留为明确的 missing category
- 每次关键转换前后都做 QA 检查，记录行数变化

### 6.5 先写指标字典

在真正分析前，先定义清楚每个指标是什么意思。

### 推荐指标

#### 内容组合

- Movies vs TV Shows 占比
- 各 rating 占比
- 各 genre 占比
- 各 country 占比

#### 新鲜度

- 中位 `release_year`
- 中位内容年龄 = `analysis_year - release_year`
- 上架时滞 = `year_added - release_year`
- 最近 1 / 3 / 5 年内发行内容占比

#### 集中度

- top-10 country share
- top-10 genre share
- top-10 director share
- 类似 Herfindahl 的集中度指标，或 cumulative share curve

#### 广度与多样性

- 每个 title 对应的国家数
- 每个 title 对应的 genre 数
- 每个 title 列出的 cast 成员数
- 按年份或内容类型计算 entropy-style diversity

#### 目录增长

- 每年新增 title 数
- 每月新增 title 数
- 按 `year_added` 看的新片占比
- country / genre mix 随时间的变化

没有指标定义的项目，最后很容易变成“图很多，但没说清楚到底在量化什么”。

### 6.6 提前规定什么才算“好 insight”

在打开 Codex 前，先立一条规则：

**一张图本身不算 insight。**

一个真正有用的 insight 至少要有三部分：

1. **Observation**：发生了什么变化 / 差异 / 集中现象？
2. **Interpretation**：这可能说明什么内容策略问题？
3. **Decision relevance**：业务方为什么会在意？

例如：

- Observation：TV Shows 在标题数量中的占比更低，但在某些 maturity band 上更集中。
- Interpretation：TV 内容可能不是广覆盖型供给，而是更有选择性的受众定位。
- Decision relevance：这对内容组合平衡、采买优先级、品牌定位都有参考意义。

### 6.7 先把 repo 结构搭干净

从第一天开始就把项目按作品集标准组织。

建议结构：

```text
netflix-catalog-strategy-analysis/
├─ README.md
├─ data/
│  ├─ raw/
│  │  └─ netflix_titles.csv
│  ├─ processed/
│  └─ external/
├─ notebooks/
│  ├─ 01_data_audit.ipynb
│  ├─ 02_feature_engineering.ipynb
│  ├─ 03_business_analysis.ipynb
│  ├─ 04_segmentation_networks.ipynb
│  └─ 05_executive_summary.ipynb
├─ src/
│  ├─ cleaning.py
│  ├─ feature_engineering.py
│  ├─ metrics.py
│  ├─ visualization.py
│  └─ utils.py
├─ outputs/
│  ├─ tables/
│  ├─ figures/
│  └─ summary/
├─ docs/
│  └─ project_brief.md
├─ requirements.txt
└─ .gitignore
```

哪怕这个项目主要还是 notebook 驱动，把可复用逻辑抽到 `src/` 里，也会显得专业很多。

---

## 7. 推荐的深度分析模块

下面是实际分析路线图。  
这里决定这个项目最后是“普通作业”，还是“真的像商业数据分析项目”。

### 模块 1 —— 数据审计与结构质量

**目的：** 先证明你理解这份数据，再开始分析。

**任务：**

- 按列分析缺失值
- 检查重复逻辑
- 检查多值字段结构
- 识别分类标签不一致
- 总结数据覆盖问题
- 记录分析风险

**输出：**

- data quality summary table
- cleaning decisions log

**商业角度：** 好 analyst 不会一上来就画图，而是先确认数据能不能被信。

---

### 模块 2 —— 内容组合与目录结构

**目的：** 定量刻画 Netflix 的片库到底长什么样。

**任务：**

- Movies vs TV Shows 占比
- 不同 type 下的 rating 结构
- 不同 type 下的 genre 结构
- duration 模式
- 头部类别与长尾结构
- major category 的 cumulative share curve

**输出：**

- content mix dashboard
- concentration visuals
- category hierarchy summary

**商业角度：** 这一层直接对应内容组合设计和供给侧定位。

---

### 模块 3 —— 新鲜度、上架时滞与库龄

**目的：** 分析片库看起来有多“新”。

**任务：**

- release year 分布
- year_added 分布
- release-to-added lag
- 按 type、genre、country、rating 分析 freshness
- 区分老牌 evergreen 内容集中区与近期内容密集区

**输出：**

- lag distribution tables
- freshness segments
- category-level comparison charts

**商业角度：** 可以近似反映平台内容更新节奏和 acquisition cadence。

---

### 模块 4 —— 地理覆盖与本地化策略

**目的：** 研究目录的国际化结构。

**任务：**

- 正规化 country
- 统计各 country title 数量
- 比较单国家 title 和多国家 title
- country × genre 分析
- country × rating 分析
- 国家构成随 `year_added` 的变化

**输出：**

- country ranking tables
- geographic concentration analysis
- localization / globalization commentary

**商业角度：** 这是这个数据集里最强的商业切入口之一。

---

### 模块 5 —— 基于 maturity rating 的受众定位

**目的：** 从分级结构推断内容面对的受众范围。

**任务：**

- 整体 rating 分布
- rating 按 type 分布
- rating 按 country 分布
- rating 按 genre 分布
- rating 随 `year_added` 的变化

**输出：**

- audience positioning matrix
- maturity profile by segment

**商业角度：** 有助于讨论片库定位、品牌受众、供给平衡。

---

### 模块 6 —— Genre 组合、多样性与白区扫描

**目的：** 找出目录中哪些区域很密，哪些相对稀疏。

**任务：**

- 正规化 `listed_in`
- 计算 genre share
- 分析 genre 共现关系
- 比较不同 type / country 下的 genre 集中度
- 识别相对稀缺的组合

**输出：**

- genre network / co-occurrence map
- concentration table
- candidate whitespace areas

**商业角度：** 这一步能把“genre 计数”升级成更像策略分析的东西。

**注意：**  
不能声称“这里是高市场机会”，你最多只能说：

> 这个组合在当前目录中相对欠代表（underrepresented）。

因为你没有市场需求数据。

---

### 模块 7 —— 人物网络分析（导演 / 演员）

**目的：** 展示更深一点的关系型分析能力。

**任务：**

- 正规化 cast 和 director
- 找出高频重复出现的导演 / 演员
- 分析 cast-director-country 或 cast-genre 的关系网络
- 检查重复合作模式
- 用 centrality measures 找出可见的生态中心

**输出：**

- network graph
- repeat-collaboration tables
- ecosystem commentary

**商业角度：** 可以支持对 production ecosystem 和内容 sourcing pattern 的讨论。

但要谨慎：  
如果只是做 graph theory 装饰，没有商业解释，这一模块反而会显得空。

---

### 模块 8 —— Title segmentation / clustering

**目的：** 从人工切片走向数据驱动分组。

### 可用特征

- type
- release year
- year added
- lag
- rating
- genre one-hot
- country features
- duration buckets

### 方法

- 基于 engineered features 做 clustering
- 维度压缩用于可视化
- 对 cluster 做 profile 总结

**输出：**

- 4–8 个可解释的 cluster
- 带业务标签的 cluster summary

### 示例标签

- “近期国际化成熟向剧情片”
- “偏老、家庭向电影”
- “连续剧型、偏犯罪题材内容”

**商业角度：** 这一块能明显提升项目层次，因为你不再只是做切分统计。

---

### 模块 9 —— 片库结构随时间的演化

**目的：** 展示内容组合如何随着时间变化。

**任务：**

- 每年 / 每月新增 title 数
- type mix 随 `year_added` 的变化
- rating mix 随 `year_added` 的变化
- genre mix 随 `year_added` 的变化
- country diversification 随 `year_added` 的变化

**输出：**

- trend lines
- decomposition tables
- phase interpretation

**商业角度：** 这一块能形成“片库如何演变”的战略叙事，比静态 EDA 强很多。

---

## 8. 值得做的强图表

如果是为了个人主页展示，应该追求“少而强”，不是“多而杂”。

### 推荐图表

- Catalog mix dashboard：type、rating、genre concentration
- release-to-add lag distribution by type
- country concentration curve（top countries cumulative share）
- genre co-occurrence heatmap / network
- catalog evolution over `year_added`
- cluster map with business labels
- freshness by country / genre matrix
- 单国家 vs 多国家 title 对比图

### 不建议保留

- pie charts
- word clouds
- 没有决策语境的重复 countplot

这些都很弱，不能有效证明分析能力。

---

## 9. 值得测试的商业化假设

Codex 在“有假设要检验”时，会比“你随便探索一下”更有用。

### 示例假设

- 虽然片库名义上国际化，但实际内容很可能高度集中在少数国家
- TV Shows 和 Movies 可能承担了不同的受众定位功能
- 近期新增内容可能比早期内容具有更高的国际多样性
- 某些 genre 在结构上更容易和成熟向分级绑定
- 少数 genre-country 组合可能支配了整个目录
- 表面上的“title 数量很多”可能掩盖了底层 production ecosystem 的集中

不是所有假设都会成立。  
这没关系。重点是你要严谨地验证，而不是模糊地看看。

---

## 10. 在 Codex 中建议使用的方法和工具

### 核心技术栈

- Python
- pandas
- numpy
- matplotlib / plotly
- scikit-learn
- networkx
- jupyter

### 推荐分析方法

- 多值字段正规化
- 描述性 KPI 设计
- 集中度分析
- cohort / time trend analysis
- clustering / segmentation
- network analysis
- 基于 `description` 的基础文本特征提取（可选）

### 可选的文本分析

`description` 字段可以支持：

- keyword extraction
- 轻量 topic grouping
- embedding-based title similarity
- 内容主题聚类

但这应该是可选增强项，不应该成为项目核心。  
做过头了会显得学术味太重，或者像炫技。

---

## 11. 必须避开的风险

### 风险 1：停留在可视化层面

如果项目最后只是“我做了一堆图”，它不会突出。

### 风险 2：假装自己知道业务结果

你没有 engagement 或 revenue 数据。  
不要对“什么内容表现更好”做结论。

### 风险 3：技术上复杂，但商业上空

例如：

- 过度复杂的 NLP
- 没有业务含义的 graph analysis
- 没法解释的 clustering

### 风险 4：因为懒而过度删行

这会扭曲片库画像。

### 风险 5：把探索、清洗、最终报告混成一个 notebook

这会让项目难以复现，也难以建立可信度。

---

## 12. 以后放到个人主页上时，应该怎么讲这个项目

适合的项目叙事应该是：

我从一个基础的 Netflix 公开元数据数据集出发，把它重构成了一个面向商业的内容目录策略分析项目。我没有停留在描述性 EDA，而是先对多实体字段进行了正规化，设计了内容组合指标，分析了片库新鲜度、地域集中度和内容结构差异，并用可解释的 segmentation 方法去挖掘更适合决策讨论的模式。

这比下面这种说法强得多：

> 我用 Python 分析了 Netflix 数据。

---

## 13. 打开 Codex 前的具体任务清单

下面这个列表才是你真正要执行的 pre-Codex checklist。

### 在打开 Codex 前必须完成

- [ ] 写出一段项目的 business framing
- [ ] 定义 6–10 个核心业务问题
- [ ] 决定实体模型（`titles`, `title_country`, `title_genre`, `title_cast`, `title_director`）
- [ ] 在编码前写好 cleaning rules
- [ ] 写出 metric dictionary
- [ ] 建立干净的 repo 结构
- [ ] 决定用于作品集 / 主页展示的最终交付物
- [ ] 决定最后保留哪 5–8 张强图表
- [ ] 先写好 data limitations 部分
- [ ] 先规定哪些结论可以说，哪些不能说

### 接下来适合做的事

- [ ] 准备 notebook 大纲
- [ ] 准备 figure style guide
- [ ] 准备 insight 模板：observation → implication → business relevance
- [ ] 准备 executive summary 模板
- [ ] 决定 clustering 和 network analysis 是否作为进阶模块加入

---

## 14. 一个实际可执行的实现顺序

下面是我认为最合理的开工顺序。

### Phase 1 —— 基础搭建

- 检查 schema 和缺失情况
- 建立 normalized tables
- 生成 cleaned analysis datasets
- 定义 metrics 和 QA checks

### Phase 2 —— 核心商业分析

- Catalog composition
- Freshness / lag analysis
- Geographic footprint
- Rating / audience positioning
- Genre concentration and co-occurrence

### Phase 3 —— 进阶分析

- Time evolution
- Clustering / segmentation
- People network analysis

### Phase 4 —— 包装输出

- Executive summary
- Final charts
- 重写 README
- 个人主页项目卡片 / 项目说明

---

## 15. “够好版本”和“优秀版本”的区别

### Minimum viable deep version

要让这个项目已经看起来不错，至少要有：

- normalized data model
- business questions
- metric dictionary
- freshness analysis
- geographic concentration analysis
- genre / rating portfolio analysis
- 明确的数据限制说明
- 一条清晰的项目叙事主线

### Excellent version

如果要让它更突出，再加上：

- title clustering
- co-occurrence / network analysis
- 内容组合随时间的演化分析
- polished executive summary
- 可直接放上网站的项目讲述方式

---

## 16. 最终判断

你现在手上的 notebook 可以当种子，但还远远不是一个成熟的作品集项目。

真正需要完成的转变是：

- 从 **EDA** 转向 **面向决策的分析**
- 从 **原始字符串字段** 转向 **正规化实体模型**
- 从 **堆图表** 转向 **设计指标**
- 从 **出于好奇的探索** 转向 **明确的业务问题**
- 从 **Kaggle 风格** 转向 **商业 analyst 风格**

如果这套东西做扎实了，这个项目完全可以成为一个有说服力的 DA / BI / Analytics 作品集项目。因为它展示的不只是编码，而是：

- 分析 framing
- 数据建模
- 指标设计
- 商业判断力
