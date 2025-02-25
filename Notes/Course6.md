## Course 6 Agents for Software Development


Challenges in Coding Agents

- How we build, How we evaluate

- Define the Environment & Design an Observation/Actions & Code Generation & File Localization & Planning Error Recovery & Safety


**BenchMarks**

- CoNaLa/ODEX

- ARCADE

- SWEBench

- Multimodal coding bench:  Design2Code

  - Metric: High-level similarity: visual embeddings between genrated lists. Low-level similarity: Recal of each individual element
  

**Metric: Pass@K**

- 当我们让模型生成 K 个不同的答案时，这 K 个答案中是否至少有一个能通过预先设定的测试（例如单元测试）

- 假设场景：你有一个编程题，要求编写一个函数满足给定的输入输出要求。你让模型生成 K 个解答（比如 5 个不同的函数实现）。

- 测试方式：对这 K 个解答分别进行单元测试，判断它们是否正确。

- Pass@K：如果这 K 个解答里至少有一个能通过测试，我们就说“Pass”；否则“Fail”。在统计上，我们想知道“有多少比例的题目，能在 K 个解答里至少出现一个正确的？”这就是 Pass@K 的值。

- If we generate K examples, will at least one of them pass the unit tests.

- Generating only K will result in high variance, so we generate N > K with C correct answers, and then calculate the correct expected value

- $pass@k=E_{Problems} \left[1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}\right]$

- 这里解释了为什么会有一个较复杂的公式：如果只生成 K 个解答去直接统计是否通过，结果不够稳定。因此通常会先生成一个更大的样本（N 个解答），标注其中哪些是正确的 (C 个)，然后再用组合概率的方法估计出对于 K 个解答时的通过率期望。

- 假设你有一个模型，用来解 100 道编程题。你希望知道 Pass@5（即一次让模型给出 5 个答案的情况下，通过率是多少）。 

    - 收集数据：让模型对每道编程题分别生成 N=100 个候选解答，共有 100 道题，所以一共生成了 100 × 100 = 10,000 个解答。

    - 统计正确数：对每道题的 100 个解答进行单元测试，假设其中有 c_i 个是正确的（i 表示题目编号，c_i 在 0~100 之间）。

    - 计算 Pass@5：对每道题，用公式： $pass@5= \left[1 - \frac{\binom{100-c_i}{k}}{\binom{100}{5}}\right]$

    - 如果 c_i 很大（比如 50），那么pass@5相对较小，意味着至少有一个正确解答的概率高。
    
    - 平均得到最终值：对 100 道题分别计算 pass@5，然后取平均值，就得到在这 100 道题上的整体 Pass@5。

**Metric: Lexical/Semantic Overlap**

-  Commonly BLUE, CodeBlue, CodeBERTScore ...




### Actual modeling 

- Understand repo structure

- Read in existing code

- Modify or produce code

- Run code and debug




**Example SWE-Agent**

假设我们有一个名为 solvers/dioptime.py 的文件，其中包含若干处理数学问题的函数。我们希望 SWE-Agent 帮忙添加新功能并修复一个已知错误：

- 代码库中有一个函数 diop_type，根据输入的字符串决定要计算何种数学运算（比如 “cubic_thue”、“general_sum_even”等）。
- 我们发现一个 Bug：当 diop_type == "general_sum_even" 时，程序没有正确处理输入，导致结果错误。
- 我们还想在同一个函数里添加对 “general_sum_odd” 的支持。

step 1： Prompt

用户：“你好，请帮我修复 diop_type == "general_sum_even" 的问题，并且在同一个文件里添加对 general_sum_odd 的处理。修复完后，请运行测试并告诉我结果。”

step 2: SWE-Agent 调用“开发者工具”定位并打开文件

1. navigate_repo：SWE-Agent 先在代码仓库中搜索与 “diop_type” 相关的文件。

2. search_files("diop_type")：搜索关键字，发现 solvers/dioptime.py 有相关定义。

3. open_file("solvers/dioptime.py")：查看文件内容，获取当前函数实现。

step 3: SWE-Agent 生成修改方案并执行编辑命令, 在内部“思考”（LM Agent）：

- 分析当前 general_sum_even 的错误所在。也许它忘记对输入列表中的元素进行偶数判断，只是简单累加。

- 为 general_sum_odd 编写类似逻辑，只是针对奇数。

- edit_file("solvers/dioptime.py", changes)：执行编辑操作，插入或修改相应代码片段。例如：

step 4: 运行测试并观察结果

```python
# response
Tests results:
===================
10 passed in 2.45s

No failures detected.
```



### Code Generation LLM

1. Basic Method: Code geration LM
    
    1. Feed instruction and code to an LM

    2. All serious LMs are trained on code

    3. code pre-training dataset: *The Stack 2* (licences cleaned)

2. Code Infilling

    1. Train for fill code in existing codes: add \<MASK:0> and \<EOM> at the begining and the end of the position you want to fill code to train the model.

3. Long-Context Extension 

    1. “Long-context Extension”就指的是一种让模型能够“扩展”其可处理的上下文长度的方法，尽量保持模型原有性能的同时，减少在极长上下文输入下出现的退化或失效问题。

    2. Rotary Position Embedding (RoPE) 是一种特殊的相对位置编码方法， 但是存在缺陷。它通过在二维坐标平面进行旋转变换，将 token 在序列中的位置映射到向量的相位上，从而让模型可以捕捉到更丰富的相对位置信息。但是，在训练时，RoPE 只能在特定长度（比如 2K 或 4K tokens）上进行旋转位置编码；当我们直接将输入长度扩展到超过训练时的长度（比如 8K、16K 或更多）时，RoPE 的原始设计并不一定能很好地“外推”（extrapolate）。模型可能会出现性能下降或者注意力分布异常的问题。

    3. 通过调整 RoPE 或其他位置编码策略，或者通过插值、缩放、重参数化等手段，让模型能够在更长的上下文范围内继续发挥作用。以下是一个例子，展示了对特征向量的偶数维和奇数维进行正余弦变换。
    $$
    \mathbf{R}(\theta, i) = \begin{pmatrix} 
    \cos i\theta_1 & -\sin i\theta_1 & \cdots & 0 & 0 \\
    \sin i\theta_1 & \cos i\theta_1 & \cdots & 0 & 0 \\
    \vdots & \vdots & \ddots & \vdots & \vdots \\
    0 & 0 & \cdots & \cos i\theta_{\frac{d_k}{2}} & -\sin i\theta_{\frac{d_k}{2}} \\
    0 & 0 & \cdots & \sin i\theta_{\frac{d_k}{2}} & \cos i\theta_{\frac{d_k}{2}}
    \end{pmatrix}
    $$

    - Example:你有一篇学术论文或一份报告，长度约 10,000 个 token（比如有 20 页、3 万字）。但是你的模型（如某个大语言模型）在训练时，最大上下文长度只有 4,096 个 token。如果你直接把整篇文档扔进去，模型会截断或者性能下降严重。
    
      - 如何做 Long-context Extension

      - 插值/缩放 RoPE: 如果你的模型本身使用了 RoPE 进行位置编码，就可以对 RoPE 的“频率”进行缩放。例如，原来第 4,096 个 token 的旋转频率是某个固定值，你把它“挤压”或“拉伸”到更长的区间，让模型在 8,192、16,384 等更高位置上也能比较平滑地过渡。这样做可以让模型对超出原训练范围的 token 位置有更合理的编码，而不是完全在一个未知的频率区域工作。


### File localization

**Scenario**: 

Find the correct file base on user's intension

**Issue**: 

In confirmation mode, user can't insert any instructions. And if the user wants to change or add a new command in the middle of the process, the system can only indicate this by ‘rejecting’ an action. 

However, after rejecting the action, the model seems to be ‘unaware’ that the action has been rejected, leading to subsequent behaviour of the system which may still assume that the previous step has been successfully executed.

**Observations**: 

Lack of clear feedback and logging of ‘rejected’ status: the system should know that an action has been rejected in order to adjust the next steps.

Lack of a more flexible interaction: before or after confirming (or rejecting) an action, the user may want to give additional guidance or instructions, but the current process does not support this kind of inserted feedback.

**Solution**:

1. Confirm action and wait

2. Prompt the Agent with search tools

3. A-priori Map the Repo

4. RAG Code Generation: (the conection between Python and English)


### Planning and Error Recovery

- Hard-coded Task Completion Process (Agentless, in fixed four steps)

    - File Localization
    
    - Function Localization
    
    - Patch Generation

    - Patch Application

- LLM Generated Plan

- Fixing Based on Error Messages

![alt text](image-1.png)


### Safety

- Sandboxing: 将执行环境限制在一个安全边界内，防止对外部系统或资源造成危害。

- Credentialing: 采用最小权限原则（principle of least privilege），确保模型只拥有它完成任务所需的最小权限。

- Post-hoc Auditing: 当模型执行完操作后，使用日志或其他监控手段对操作进行审查，一旦发现异常操作，及时回滚或阻断。

[Github](Github.com/All-Hands-AI/OpenHands)

