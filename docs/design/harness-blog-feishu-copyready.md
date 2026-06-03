# 从 AI Coding Demo 到 Harness Engineering（From AI Coding Demo To Harness Engineering）

> 如何理解、搭建并评估一个真正可用的 coding harness
>
> 阅读信息：约 1.8 万字符，预计阅读 15 到 20 分钟

## 先看核心判断

如果只先记住四句话，最值得记的是这些：

1. Harness 不是更大的提示词（prompt），而是模型外部的控制系统。
2. 一个系统从 demo 走向工程，关键不在模型更强，而在控制闭环更完整。
3. 第一版 harness 最重要的目标不是“惊艳”，而是“可信”。
4. 学习 harness 时，最值得先看的不是平台功能有多少，而是骨架是否已经足够清楚。

## 为什么这篇值得往下读

这两年，大家已经看过太多 AI 写代码的演示。一个提示词（prompt）发出去，模型回一段代码，或者直接改几个文件，看起来很惊艳；再往前走一步，它还能读仓库、跑命令、补测试，甚至给你一个“我已经完成”的总结。第一次看到这类系统时，很多人的直觉都是：“这不就是未来的软件开发方式吗？”这个直觉并没有错，但一旦你真的开始把它接进工程流程，问题几乎总会立刻出现。

真正麻烦的不是“模型会不会写”，而是下面这些事几乎都会失控：

1. 用户只说一句“继续”，系统到底应该继续什么
2. 一个任务应该看多少上下文，哪些文件才是相关的
3. 哪些命令可以直接执行，哪些操作必须被拦住
4. 改完代码以后，什么才算真正完成
5. 测试失败以后，是该自动修复、自动重试，还是停下来
6. 过了两天再回来看，能不能知道上一次到底做了什么

这些问题和“模型会不会写代码”其实已经不是一回事。它们问的其实是同一件事：**你有没有把模型放进一个可控、可验证、可复盘的工程系统里。**这个工程系统，就是 harness。下面这篇文章不会只停在概念层，而会把问题继续往下压到更实际的位置：

1. 一个最小可用 harness 通常长什么样。
2. 第一版最值得先抓什么。
3. 怎样判断一个项目到底是不是在做 harness。
4. 放到一个真实工程里，这些控制点通常会落在哪些地方。

## 一个足够准确的定义

如果只用一句话来概括，就是：**Agent 是执行者，Harness 是运行环境。**模型负责生成、判断和推理，Harness 负责把一次 AI 执行变成一个工程闭环。

- 普通 AI coding demo 更像：`prompt -> model -> output`
- 一个最小可用 harness 更像：`request -> context -> plan -> policy -> runtime -> verify -> repair -> replay`

两者的本质差别，不在于是否“调用了模型”，而在于是否具备以下能力：

- 接收并解释任务
- 在执行前施加约束
- 在执行后进行验证
- 在失败时进行恢复或停止
- 在结束后留下可回看的证据

因此，harness 的价值不在于“让模型更聪明”，而在于“让系统更可控”。

## 为什么很多 AI Coding 项目最后停在 Demo 阶段（Why Many AI Coding Projects Stall At The Demo Stage）

**问题不在于模型不够会写代码，而在于系统没有把执行前、执行中、执行后这三段控制起来。**

很多项目的早期演化路径都很像：

1. 先有一个提示词（prompt）。
2. 再补一些仓库文件（repo files）。
3. 再接入 shell 工具或文件修改能力。
4. 最后开始堆更多规则、模板和例外逻辑。

表面上看，系统能力越来越多；但真正进入工程环境后，结果往往没有随着复杂度同步变好，反而更难预测、更难验证、也更难复盘。

这通常不是因为模型不够强，而是因为系统一直停留在 demo 思维里。

所谓 demo 思维，就是默认下面这些问题都还可以继续交给提示词（prompt）解决：

1. 意图澄清。
2. 上下文选择。
3. 权限边界。
4. 风险判断。
5. 完成定义。
6. 失败恢复。
7. 运行记录。

这会带来几个很典型的问题。

### 1. 行为不可预测

同一句用户输入，在不同模型、不同提示词版本、不同上下文残留条件下，可能触发完全不同的动作。比如用户只说一句“继续”，如果没有 harness 层，这句话通常会再次被当作自然语言交给模型推断；但一个真正的 harness 会先判断：

- 这是在继续上一轮任务，还是新任务
- 最近是否存在多个可能的续轮候选
- 当前是否必须先停下来澄清

归根结底，这类判断属于交互控制，不属于语言生成。

### 2. 边界不清晰

如果没有显式策略层（policy），系统就会默认“模型懂了就可以做”。但真实工程里，核心问题之一恰恰是：

> **什么可以做，什么不可以做。**

最典型的就是这几类：

1. 哪些命令可以直接执行。
2. 哪些文件写入需要确认。
3. 哪些网络行为必须被拦截。
4. 哪些 git 相关动作应该统一收敛到专门封装中。

没有 harness 接管这些边界，能力越强，风险越高。

### 3. 没有完成定义

很多 demo 默认“模型说完成了”就是完成，但工程里的完成至少意味着：

1. 目标文件确实发生了预期变化。
2. 相关测试确实被添加或更新。
3. 验证命令确实执行过。
4. 失败时能明确区分实现失败、环境失败还是瞬时失败。

因此，验证机制（verification）和完成定义（completion contract）必须属于 harness，而不能只属于提示词。

### 4. 没有复盘能力

如果系统没有回放机制（replay），就很难回答这些问题：

1. 上一轮到底做了什么。
2. 为什么这次会继续那个任务。
3. 是执行提供方（provider）暂时超时，还是实现本身错误。
4. 这次结果到底如何产生。

没有回放机制（replay），调试和复盘都会退化成猜测。

## 和 Vibecoding 相比，Harness 具体多了什么

**如果说 vibecoding 解决的是“先做出来”，那么 harness 解决的是“以后还能稳定地反复做出来”。**

这里说的 vibecoding，可以先把它理解成一种“先凭感觉做出来”的工作方式：先让模型试、先让代码跑、先把结果堆出来，至于边界、验证、复盘，往往留到后面再说。

而 harness 带来的变化，不只是多了几个模块，而是把一次 AI coding 执行从“碰运气”变成了“有控制闭环的工程过程”。最容易理解的方式，不是抽象讲定义，而是看同一类任务在两种模式下会发生什么。

### 例子 1：一句“继续”，系统会不会跑偏

在 vibecoding 里，用户只说一句“继续”，模型通常会直接猜：
- 是继续刚才改代码
- 还是继续写文档
- 还是继续跑测试

如果上下文里候选任务不止一个，这种猜测很容易跑偏。换成 harness，系统会先判断：
- 这是在继续上一轮任务，还是新任务
- 最近是不是只有一个明确候选
- 如果有多个合理候选，是否应该先停下来澄清

真正多出来的优势是：
- 短输入不再直接触发猜测执行
- 续轮任务（continuation）更稳
- 长任务更不容易因为一句模糊输入而偏航

### 例子 2：模型说“我改好了”，但系统能不能证明

在 vibecoding 里，一个很常见的场景是：
- 模型改了几行代码
- 回复一句“已经修复”
- 但测试没跑，或者跑了却没过
- 甚至架构边界已经被打破

换成 harness，完成不再由模型一句话宣布，而是要经过：
- 完成定义（completion contract）
- 验证门（verification gates）
- 测试、lint 和架构检查

这样带来的优势是：
- “完成”有证据，不只是说法
- 假完成更容易被拦下来
- 失败时能明确知道是哪一道 gate 没过

所以这里真正多出来的，不是更会写代码，而是更会判断“到底有没有真的做完”。

### 例子 3：危险操作不会直接变成系统行为

在 vibecoding 里，如果模型判断下一步应该：
- 删除文件
- 跑网络命令
- push 代码
- 调外部执行提供方（provider）

很多时候它就会直接建议甚至直接做。换成 harness，系统会先经过策略层（policy）：
- 允许（allow）
- 确认（confirm）
- 拒绝（deny）

这带来的优势是：
- 低风险操作可以顺畅放行
- 高风险操作会被显式拦住或要求确认
- “模型一时冲动”不会直接变成“系统已经执行”

这也是从 demo 走向真实工程环境时，最早必须补上的能力之一。

### 例子 4：修一个很小的 bug，也能看出差别

一个很小的练习靶子就足以说明这种差异。如果让一个纯 vibecoding 流程去修一个很小的 bug，常见路径会是：
1. 先拍脑袋改代码
2. 顺手重构一堆没要求的东西
3. 最后回复“应该好了”

如果按 harness 的方式走，通常更像：
1. 先跑测试
2. 看失败点
3. 只读相关文件
4. 做最小修复
5. 再跑验证
6. 留下回放记录（replay）或结果记录

两者都可能把 bug 修好，但后者明显更：
- 可解释
- 可验证
- 可复盘
- 适合团队复用

### 例子 5：为什么 Harness 更适合长期工程

vibecoding 的强项通常是“先快速试出来”，但它有一个天然问题：很多经验不会自动沉淀下来。上一次踩过的坑，下次还会踩；上一次做过的任务类型，下次还要重新猜一次。

harness 的不同在于，它可以把重复行为逐步沉淀成：

- 工作流（workflows）
- 规则（rules）
- 模板（templates）
- 验证模式（verification patterns）

这带来的优势不是某一次更快，而是：
- 下一次同类任务不用从零开始
- 团队知识会变成可复用资产
- 系统会越来越稳，而不是越做越乱

如果把这件事压成一句话：
> **vibecoding 解决的是“先做出来”；harness 解决的是“以后还能稳定地反复做出来”。**

## Harness 真正解决的是什么

**换句话说，harness 关心的不是“这次能不能生成”，而是“这次能不能被控制、被验证、被复盘”。**它不是提示词（prompt）的扩展，也不是模型调用的壳，而是一套把执行过程变成工程闭环的控制系统。一个最小可用 harness，至少要把下面八个问题回答清楚。

### 1. 入口（Entry）

任务从哪里进来？第一版通常是命令行入口（CLI）；更成熟一些，也可能来自接口（API）、后台常驻进程（daemon）、编辑器扩展（IDE extension）或聊天入口（chat entrypoint）。关键不在入口形式，而在于系统是否有稳定的控制面。

### 2. 上下文（Context）

上下文如何组织？不是把整个仓库一股脑塞进去，而是构造一个有边界的、与当前任务真正相关的上下文。

### 3. 意图解释（Intent Interpretation）

用户意图如何被解释？系统要能分清，用户是在修 bug、做 feature、排查问题，还是只是在继续上一轮任务。

### 4. 策略控制（Policy）

哪些行为允许执行？这就是策略层（policy）要解决的事。它至少应该能给出三种明确结果：

- 允许执行（allow）
- 需要确认（confirm）
- 直接拒绝（deny）

### 5. 运行执行（Runtime）

实际执行如何发生？这就是运行时层（runtime）要处理的事。它应该把本地执行、CLI 委托、API 提供方（provider）等路径抽象开，而不是把所有执行细节都堆在入口层。

### 6. 结果验证（Verification）

结果如何验证？完成不应只依赖模型自述，而应依赖测试、架构检查、产物检查、git 摘要或 acceptance 流程。

### 7. 失败处理（Repair / Stop）

失败之后如何处理？重试、修复还是停止，应该有清晰的失败分类和停止条件。

### 8. 过程留痕（Replay）

过程如何留痕？系统需要保留足够的运行证据，用于续轮任务（continuation）、事后复盘（postmortem）和调试。

总结来说，harness 的关注点不是“生成更多”，而是“控制更多”。

## 一个最小可用 Harness 通常长什么样

**第一版不需要大而全，但必须先长出最小控制骨架。**如果目标是实现第一版，而不是复刻最终产品，那么一个最小可用 harness 通常只需要七个部件。

### 1. 入口（Entry）

一个稳定的任务入口，最常见的第一版就是命令行入口（CLI）。

### 2. 上下文（Context）

一个能够构造仓库感知上下文（repo-aware context）的模块，至少应该知道：

- 当前仓库在哪里
- 当前 git 状态是什么
- 哪些文件可能相关
- 哪些文档（docs）应优先读取

### 3. 规划（Planning）

一个很轻的任务分类和步骤生成器。第一版通常只需要稳定分清几种任务形状：

- 修 bug（fix bug）
- 做功能（implement feature）
- 写测试（write tests）
- 查问题（investigate issue）

### 4. 策略（Policy）

一个在运行时层（runtime）之前做风险分类的控制点。

### 5. 运行时（Runtime）

一个负责文件修改、命令调用、git 操作和提供方委托（provider delegation）的抽象层。

### 6. 验证与修复（Verification and Repair）

至少有一条可重复的验证检查（deterministic check），例如：

- 单元测试（unit tests）
- 架构检查脚本
- lint 检查

并在失败时有最基础的“修复或停止”（repair or stop）逻辑。

### 7. 回放（Replay）

哪怕只是最简单的 JSON 记录，也应该把一次运行（run）的关键信息存下来。

如果这七个部件都在，系统就已经不是演示，而是一个真实的第一版 harness。

> **第一版 harness 的目标不是“惊艳”，而是“可信”。**

## 如果真的开始搭，最该先抓什么

如果真的动手做第一版 harness，最容易出问题的地方不是“少了某个高级能力”，而是顺序错了。更稳妥的做法，通常不是一开始就追求复杂度，而是先把最关键的几个控制点长出来。

### 先把入口立住，不要先堆提示词

先把控制面立住，至少先想清楚四件事：

- 命令怎么进来
- 仓库（repo）怎么指定
- 输出怎么展示
- 运行时（runtime）怎么选择

### 再做一个有边界的上下文构造器

第一版只要能提供下面这些信息，就已经足够有用：

- 仓库根目录（repo root）
- git 状态摘要（git status summary）
- 候选文件（candidate files）
- 关键文档（docs）

### 然后做一个很轻的规划器

第一版规划器（planner）不需要复杂计划，只要能稳定区分几种任务形状。

### 把策略层放到运行时层前面

这是从 demo 走向 harness 的关键一步。至少应该在执行前判断：

- 文件写入风险
- 命令执行风险
- 网络访问风险
- git 相关行为风险

### 尽早把验证接进来

第一版就应该选一条最稳定的验证路径，例如：

- 单元测试
- 架构检查脚本
- lint 检查

### 给系统留一层很薄的回放机制

哪怕只是一个 JSON 文件，也值得先做，至少记录：

- 原始提示词（prompt）
- 任务类型
- 关键步骤
- 验证结果（verification）
- 最终状态

### 最后再考虑更厚的资产层

当行为开始重复时，再引入：

- 工作流资产（workflows）
- 规则资产（rules）
- 模板资产（templates）

不要在第一版还没跑通的时候，就先设计一层很重的工作流引擎（workflow engine）。

## 从提示词包装器走到 Harness 的常见路径

很多团队在做 AI coding 时最大的困难，不是“看不懂概念”，而是“跨度太大”。一边是极简 demo，一边是看起来像完整产品的平台，中间缺少分阶段成长的路径。更稳的理解方式，是把它看成一条逐步增加控制点的演进链：

```
阶段 0（Stage 0）
提示词 -> 模型 -> 输出

阶段 1（Stage 1）
CLI 入口 -> 模型 -> 输出

阶段 2（Stage 2）
CLI 入口 -> 上下文 -> 模型 -> 输出

阶段 3（Stage 3）
CLI 入口 -> 上下文 -> 规划 -> 运行执行 -> 验证

阶段 4（Stage 4）
CLI 入口 -> 上下文 -> 规划 -> 策略控制 -> 运行执行 -> 验证 -> 回放

阶段 5（Stage 5）
CLI 入口 -> 上下文 -> 规划 -> 策略控制 -> 运行执行 -> 验证 -> 修复 -> 回放

阶段 6（Stage 6）
CLI 入口 -> 上下文 -> 规划 -> 策略控制 -> 工作流资产 -> 运行执行 -> 验证 -> 修复 -> 回放
```

> 注：这不是要求你一步做到第 6 阶段，而是用来说明 harness 的成长方式，本质上是逐步增加控制点，而不是单纯增加提示词长度。

这条演进链说明了两件事：

1. harness 的成长方式，是增加控制点，而不是无限堆提示词
2. 第一版做到阶段 4（Stage 4）或阶段 5（Stage 5），就已经是很强的结果

大多数团队真正卡住的原因，不是做不到，而是一下子想做得太像最终产品。

## 什么样的第一版，已经值得继续投入

第一版不需要一步到位，但至少应该让人看到：这个系统已经不只是演示，而是有了真实控制闭环。一个很实用的判断标准是：

1. 一条 CLI 命令可以稳定接收提示词和仓库目录
2. harness 能构造有边界的仓库上下文
3. 能识别至少一种任务形状并执行到底
4. 风险行为在执行前被分类
5. 自动跑一条验证命令
6. 运行结束后写出回放记录（replay）
7. 有 4 到 6 个聚焦测试（focused tests）保护核心控制点

如果这七条都满足，做出来的已经不是演示，而是一个值得继续迭代的第一版 harness。

## 最常见的几个坑

第一版最常见的问题，通常不是模型不够强，而是系统边界还没立住。最典型的坑包括：把提示词当系统，结果所有行为变化都只能靠改提示词完成；让 CLI 越长越胖，慢慢堆进规划逻辑、git 逻辑和工作流分支；误以为上下文越多越好，最后塞进去的大多是噪音而不是信号；把验证放到很后面，导致系统长期停留在“看起来像完成”；在主闭环还没跑顺时就急着上厚重的工作流引擎（workflow engine）和复杂的 agent 图编排；没有失败分类（failure typing），让每一次重试都变成礼貌但混乱的循环；以及没有回放机制（replay），让很多问题最后只能靠猜，续轮任务（continuation）也变得越来越不可靠。

## 怎么快速判断一个 Harness 项目值不值得看

**判断一个项目值不值得学，不要先看功能清单，要先看控制闭环。**如果你不是自己从零开始搭，而是在看一个现成项目值不值得花时间，最有效的方式不是先看它“功能多不多”，而是先看它有没有形成真实控制闭环。

### 第一层：它是不是在做真实 Harness

优先看这八件事是否存在：

1. 有没有稳定入口
2. 有没有有边界的上下文（bounded context）
3. 有没有任务解释层
4. 有没有显式策略层（policy）
5. 有没有运行时抽象（runtime abstraction）
6. 有没有验证机制（verification）
7. 有没有修复决策（repair decision）
8. 有没有回放机制（replay）

如果这八项里缺掉一半以上，它大概率还更接近 demo，而不是工程系统。

### 第二层：它是不是“只是个 demo”

更可靠的判断方式，是看它有没有下面这些特征：完成不是靠模型自述，而是靠外部验证；风险边界不是藏在提示词里，而是被独立控制；失败以后不是只能重试，而是能区分修复、重试和停止；做完以后不是只剩聊天记录，而是有可回看的结构化证据。

### 第三层：工程边界是不是健康

即使一个项目已经开始做 harness，也不代表它的结构就是健康的。更进一步要看：CLI 有没有慢慢长成巨石，git 相关能力有没有统一收敛，验证逻辑有没有独立成层，风险行为有没有显式分类，资产层有没有开始承接重复行为。

### 第四层：哪些是 MVP 必需，哪些是后续增强

如果只想判断一个项目是不是已经长出了 harness 的基本骨架，更值得先看的通常不是功能清单，而是这几类控制点是否已经在位：稳定入口、有边界的上下文、明确的规划（planning）、显式策略层（policy）、可重复的验证（verification），以及最基本的回放（replay）。

相对来说，工作流资产（workflow assets）、规则资产（rule assets）、模板资产（template assets）、记忆检索（memory retrieval）、daemon / API 控制面、多代理编排（multi-agent orchestration）、仪表盘以及成本 / 缓存平台层（dashboard / cost / cache platform）这些东西，更像是第二阶段才会逐步长出来的增强层。

也就是说，一个项目没有多代理，不代表它不成熟；但如果它连验证（verification）和回放（replay）都没有，那它大概率还停留在 demo 阶段。需要特别说明的是，在样本工程这一层面，记忆检索（memory retrieval）、daemon / API 控制面、多代理编排（multi-agent orchestration）这些方向即使已经出现第一版实现，也仍然更适合被理解为 **MVP 之后的增强层**，而不是学习第一版 harness 时必须先做厚的部分。

### 一个实用的评估问题清单

如果只想快速判断一个项目值不值得深入看，可以直接问这几个问题：

1. 任务是怎么进入系统的？
2. 上下文是怎么被选择和裁剪的？
3. 风险行为是怎么被分类的？
4. 完成是怎么被证明的？
5. 失败以后系统怎么决定下一步？
6. 一轮运行结束后留下了什么证据？
7. 这些控制点是代码结构的一部分，还是只靠提示词维持？

## 放到一个真实项目里看，Harness 会长成什么样

**前面讲的是抽象骨架，下面看它在一个真实工程里通常长成什么样。**只讲概念，很容易让 harness 一直停留在“好像懂了”的状态。真正有帮助的，通常不是再补更多定义，而是看一个真实项目怎么把这些控制点拆成工程结构。这里用一个真实样本工程来对照说明，它之所以值得看，不是因为它功能最全，而是因为它刚好处在一个比较适合观察骨架的位置：

- 已经有完整闭环
- 还没有厚到把骨架完全遮住

### 先看一棵简化过的项目树

```
Claude_Code_MVP/
  app/
    cli/
      main.py                  # 入口，参数解析，运行模式选择
    agent/
      loop.py                  # 主控制闭环
      intent_clarifier.py      # 短输入、续轮、模糊输入澄清
      planner.py               # 任务形状识别与轻量规划
      policies.py              # allow / confirm / deny 风险控制
      verification_gates.py    # 验证门（verification gates）
      completion_contracts.py  # 完成定义
    runtime/
      adapter_factory.py       # 本地 / provider 运行时选择
      local_runtime.py         # 本地执行
      git_tool.py              # git 相关统一封装
    superpowers/
      failure_classifier.py    # 失败分类
      repair_policy.py         # 重试 / 修复 / 停止决策
    evals/
      replay.py                # 运行留痕与回放
  specs/
    workflows/                 # 工作流资产
    rules/                     # 规则资产
    templates/                 # 模板资产
  examples/
    harness-lab/               # 小练习靶子
```

> 注：这是一棵“为了教学而压缩过”的项目树，重点是让读者先看清控制闭环的骨架，而不是一开始就陷进所有实现细节。

只看这棵树，其实已经能看出一个比较典型的 harness 形状：

- `cli/` 负责把请求接进来
- `agent/` 负责控制闭环
- `runtime/` 负责真正执行
- `superpowers/` 负责失败恢复
- `evals/` 负责回放和复盘
- `specs/` 负责逐步把行为从硬编码迁移到资产层

为了让结构更容易读，这里故意省略了几块已经在本工程里出现第一版实现、但不属于“先看骨架”主线的模块，例如：

- `app/acceptance/`：面向 provider 的 acceptance 与报告生成
- `app/core/memory_store.py`：轻量记忆 / 检索（memory / retrieval）存储
- `app/agent/orchestrator.py`：第一版多代理编排
- `app/daemon/service.py`：第一版本地 daemon / API 控制面
- `app/core/tool_registry.py`、`app/runtime/artifact_readers.py`：更靠后的工具注册与产物可读层

### 1. 入口是怎样接住请求的

入口层大致会做下面这些事：

```
def main():
    # 解析用户输入与仓库位置
    args = parse_cli_args()
    repo_path = resolve_repo(args.repo)

    # 选择运行时，并准备澄清与权限控制部件
    adapter = build_runtime_adapter(args.provider)
    clarifier = IntentClarifier(...)
    permission_pipeline = PermissionPipeline(...)

    # 先判断任务是否足够清楚，不清楚就停下来问
    clarification = clarifier.clarify_with_context(args.prompt, repo_path)
    if clarification.status == "needs_clarification":
        return render_questions(clarification)

    # 进入真正的执行闭环
    loop = CodingAgentLoop(...)
    result = loop.run(
        prompt=clarification.normalized_prompt,
        repo_path=repo_path,
        task_type=clarification.inferred_task_type,
    )
    return render_result(result)
```

> 注：这段伪代码想强调的是调用顺序：先接住请求，再做澄清和权限判断，最后才进入执行闭环。

这段骨架背后的重点不是语法，而是顺序：

- 请求先进入稳定入口
- 再经过澄清和权限判断
- 最后才真正进入执行闭环

### 2. 澄清层是怎样拦住模糊输入的

澄清层的骨架大致像这样：

```
def clarify_with_context(prompt, repo_path, recent_runs):
    # 先把用户输入规范化，避免短输入直接进入执行阶段
    normalized_prompt = normalize(prompt)
    continuation_target = infer_continuation_target(normalized_prompt, recent_runs)
    inferred_task_type = infer_task_type(normalized_prompt, continuation_target)

    # 如果只是“继续”之类的短输入，但没有唯一续轮对象，就先澄清
    if short_continuation_but_no_clear_target(normalized_prompt, recent_runs):
        return needs_clarification("Which task should continue?")

    # 如果目标对象不明确，也先停下来问
    if target_is_missing(normalized_prompt, inferred_task_type):
        return needs_clarification("Which file, module, or behavior should change?")

    # 信息足够时，才把规范化后的任务送入后续闭环
    return ready(
        normalized_prompt=normalized_prompt,
        inferred_task_type=inferred_task_type,
    )
```

> 注：这段不是在展示语言理解技巧，而是在说明 harness 如何在真正执行前拦住模糊输入，避免系统“猜着干活”。

这个部件要解决的，不是语言能力，而是控制问题：

- 用户是不是只说了“继续”
- 这句话有没有明确续轮对象
- 这个任务到底是在修 bug、加 feature，还是在调查问题

### 3. 策略层是怎样把“能做什么”显式化的

`policies.py` 展示的是 harness 的第二个核心能力：不要把权限边界藏在提示词里。

它的大致形状可以抽象成：

```
class PermissionPipeline:
    def assess(operation, policy_mode, provider_info):
        # 纯查看类操作通常可以直接放行
        if operation == "inspect":
            return allow(low_risk=True)
        # 本地闭环执行允许在工作区内写入
        if operation == "local_loop":
            return allow(workspace_write=True)
        # 外部 provider 委托要先看 provider 是否可用，再决定是否确认
        if operation == "delegated_provider":
            if provider_unavailable(provider_info):
                return deny("provider unavailable")
            if policy_mode == "dangerous":
                return allow("full bypass")
            if policy_mode == "auto":
                return allow("auto approved")
            return confirm("external execution requires approval")
        return deny("unknown operation")
```

> 注：这段的重点不是具体分支名，而是说明权限判断应该是一个独立控制点，系统需要显式产出“允许 / 确认 / 拒绝（allow / confirm / deny）”这样的明确结果。

这里只展示了非常小的一部分，但已经足够说明 harness 的关键差别：

- 权限判断是独立控制点
- 风险会被分类
- 系统会明确产出“允许 / 确认 / 拒绝（allow / confirm / deny）”
- “是否执行”不应该依赖模型临场判断

### 4. 验证层是怎样把“模型说做完了”变成“系统证明做完了”

验证层的大致逻辑可以被理解成：

```
def run_post_execute(state):
    # 先根据任务类型和结果，计算这次是否满足完成定义
    completion_check = evaluate_completion_contract(state)
    gate_results = []

    # 再逐个执行验证门，而不是只听模型说“我做完了”
    gate_results.append(check_tests_passed(state))
    gate_results.append(check_changed_files_recorded(state))
    gate_results.append(check_completion_contract(completion_check))
    gate_results.append(check_no_architecture_violation(state))

    # 最后把验证结果和失败门一起返回，供 repair 或 stop 逻辑使用
    return {
        "completion_check": completion_check,
        "gate_results": gate_results,
        "gate_failures": [g for g in gate_results if not g.passed],
    }
```

> 注：这段用来说明“完成”不该由模型一句话宣布，而应该由一组可检查的 gate 来共同证明。

这层的核心意义在于：

- 完成不是模型自述
- 完成要经过一组可重复的验证门
- “没通过”时要知道是哪道 gate 失败了

如果一个系统没有这层，它本质上仍然更像 demo，而不是工程系统。

### 5. 回放为什么是闭环的一部分

很多人第一次做 agent 时，会把回放机制（replay）当作“高级增强”。但真正从 harness 角度看，回放机制（replay）不是锦上添花，而是闭环的一部分。

因为没有回放机制（replay），就很难回答下面这些问题：

- 上一轮到底做了什么
- 为什么这次会继续那个任务
- 上次失败是环境问题、实现问题，还是瞬时问题
- 这次结果到底是怎样产生的

从 harness 角度看，回放机制（replay）的意义不是“记录日志”，而是让续轮任务（continuation）、调试（debug）和事后复盘（postmortem）有证据可追。

### 6. `specs/` 为什么重要

在这个样本里，`specs/` 的价值不是“文档放在这里”。更重要的是，它代表了一条工程演进方向：

- 先用代码把闭环搭起来
- 然后把稳定重复的行为抽成工作流、规则和模板
- 再让这些资产反过来驱动规划（planning）、验证（verification）以及 critic / verifier 判断

这说明 harness 的工程化不只是“把代码写出来”，还包括把行为逐步沉淀成可复用资产。

## 为什么一个不过厚的样本工程反而更值得看

**学习样本最重要的不是功能最多，而是骨架足够清楚。**很多人会问：“为什么不直接去研究一个更大的 agent 平台？”答案很简单：在学习阶段，过厚的系统会遮住真正重要的骨架。

这个样本工程适合作为学习样本，不是因为它功能最全，而是因为它已经长出了一个 harness 最关键的骨架：入口、上下文组织、规划、策略控制、运行时抽象、验证、修复、回放，以及第一波开始接管行为的资产层。

与此同时，它又还没有厚到让学习成本一下子失控。你在这里暂时看不到一个很重的长期记忆 / 检索（memory / retrieval）系统，看不到丰富的仪表盘或成本 / 缓存平台层（dashboard / cost / cache platform），也看不到已经产品化完成的 daemon / API 控制面，或者一套完全定型的重型多代理系统。

更准确地说，这些方向在当前工程里已经出现了第一版入口，但还没有成长到会遮住学习主线的程度。这反而很适合作为学习入口，因为它能清楚展示：

- 一个 harness 应该先长出什么
- 哪些是 MVP 必需
- 哪些是后续增强
- 为什么控制闭环比功能堆叠更重要

## 最后的判断

从“AI 能帮我写代码”到“我能做一个 AI coding system”，中间真正要跨过去的，不是模型能力，而是工程控制能力。这层工程控制能力，就是 harness。如果真的要动手做第一版，最重要的不是模仿一个最终产品，而是先做出一个小而清楚的闭环：

- 有入口
- 有上下文
- 有计划
- 有策略
- 有运行时
- 有验证
- 有回放机制（replay）

当这些东西都长出来之后，系统才真正从 demo 进入了工程，而这一步，往往比换一个更强的模型更重要。如果用一句话收住全文，大概就是：

**真正值得学习的，不是某个单独模块，而是一个系统如何把入口、上下文、边界、执行、验证、修复和回放串成一个完整闭环。**
