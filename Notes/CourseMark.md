## Course 1

This lecture introduce the 

## Course 2


## Course 3


## Course 4


## Course 5 Compound AI Systems & the DSPy Framework, Omar Khattab

### Compound AI System

- To solve the problem, the compound AI system is built for
  
  - Turning monolithic LMs into reliable AI systems remains challenging

  - The monolithic nature of LMs makes them hard to control, debug and improve

![alt text](image.png)

### DsPy

DsPy is kind of natural language Python, 

![alt text](image-1.png)


- multi-hop behavior

  - It's a process LLM ask query and det context and use the context to ask more queries to figure out a problem step by step.

  - The MultiHop can be expressed as DSPy program

```python
class MultiHop(dspy.Module):
    def __init__(self):
        self.generate_query = dspy.ChainOfThought("context, question -> query")
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")
    def forward(self, question):
        context = []
        for hop in range(2):
            query = self.generate_query(context, question).query
            context += dspy.Retrieve(k=3)(query).passages
        answer = self.generate_answer(context, question)
        return answer
```
> Example:

DSPy provide an more intellectual method to divide QA into multiple tasks:

- Retrival Module

- Summarize Module


```python
import dspy  # 导入 DSPy 框架

# 定义一个 LLM（例如 GPT-4o）
llm = dspy.OpenAI(model='gpt-4o')

# 定义 DSPy 的问答模块
class QAProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        # 定义检索器（用于从搜索引擎或文档库获取相关信息）
        self.retrieve = dspy.Retrieve(k=5)  
        # 定义总结模块（用于从检索的内容中提取答案）
        self.summarize = dspy.Summarize()

    def forward(self, question):
        """问答逻辑"""
        docs = self.retrieve(question)  # 1. 先检索相关文档
        answer = self.summarize(docs, question)  # 2. 再总结答案
        return answer

# 创建 DSPy 问答系统
qa_system = QAProgram()

# 运行问答
question = "拿破仑是在哪一年去世的？"
answer = qa_system.forward(question)

print(answer)  # 预期输出："1821年"

```


Why DSPy is better than GPT-4?

- Modular design (reusable)

- Self-Improving

  - If DSPy finds that a module is not performing well, it can automatically adjust the Prompt or model call to improve the quality of the answer.

- Improved accuracy

- For code generation tasks, the code testing and fixing can be included as part of the modularisation process. 


### MIPRO

> [Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs](https://arxiv.org/abs/2406.11695)
>
> [Fine-Tuning and Prompt Optimization: Two Great Steps that Work Better Together](https://arxiv.org/abs/2407.10930)

#### Promblem Settings

- **Input**: Questions and developer build LM Program P + metric (label / non-label)

- **Output**: An optimized LM System

- **Metaology**: optimize prompts

#### Constraints:

- No access to lof-probs or model weights

- No intermediate metrics/labels

- Budget-coonscious

#### Methods

1. Bootstrap Few-shot 

Start with a smaller labeled dataset (support set) containing input-output pairs or use a model with reasonable accuracy to generate candidate examples, which are then filtered for quality. From this pool, randomly select a few examples (typically 2 to 8) to form a few-shot prompt, and evaluate its performance on a development/validation set using metrics like accuracy, BLEU, or ROUGE. Repeat this random sampling process many times—10, 100, or more iterations—while tracking performance, and retain the best-performing example combinations. These top combinations can then be further refined through merging or cross-validation in a bootstrapping loop, similar to reinforcement learning or evolutionary algorithms, gradually optimizing the selection. Finally, once satisfactory performance is achieved, finalize the prompt template by incorporating these chosen examples into your inference system, ensuring improved responses for similar questions.

2. Extending OPRO (Optimization through Prompting)

- Basic OPRO

Using prompting Proposals like: "Think step by step", "Take a deep breath and think step by step", "Carefully solve the problem", "Let's do the math"

Evaluate their performance one by one and rank them base on the socres and using the backward to adjust the prompts

- Extending OPRO

  - Initial extension to multi-stage: CA-OPRO (Coordinate-Ascent OPRO)
    
    - Generate large scale prompt proposals
    
    - Freeze all the parts except the agent you want to optimize

    - Repeat trying the proposals one by one until get the optimized one

    - The Coordinate-Ascent's complexity $O(ND^2M)$

Because Coordinate-Ascent for each is very expensive, and we don't need to make the credit assignment explicit. So we can update multiple prompts at one time. 

This is essentially similar to the concept of searching, iteratively deepening, to find the most optimal combination in all spaces. However, it is easy to fail to find an optimal solution or to iterate to a local maximum. Solutions include Random Restarts, Exploratory Search and Simulated Annealing, Early Stopping / Fallback, Heuristics/Constraints and Partial Rollback / Sub-Module Optimization.

Next step: Grounding

> Grounding: Provide the proposer with more contextual information or examples relevant to the task to help it produce a more focused, higher quality Prompt.

![alt text](image-3.png)

3. MIPRO

>Identify the optimal or better prompts and examples for each module in a multi-module, multi-prompt/demo set scenario;
>
>Efficiently assigning ‘contributions’ or ‘credits’, i.e., knowing which Prompts or Demo Sets play a key role in the overall performance improvement.

- Bootstrap Task Demonstrations: Prepare an initial Demo Set for a specific task or module to provide a few-shot sample or context in the Prompt.

- Propose Instruction Candidates using an LM Program: Using an ‘LM Program’ or ‘Proposer’ model, a number of candidate instructions are generated for each module. This will help us get a candidate pool.

- Jointly Tune with a Bayesian Hyperparameter Optimizer: 
  - Consider the ‘which instructions + which demo examples’ combination as ‘hyperparameters’;
  - Use Bayesian optimisation to decide which new combinations to try at each iteration and evaluate their performance (Score).
  - Continuously update the Bayesian Surrogate Model based on the evaluation scores, so that it gradually learns to estimate how ‘certain instruction-example’ combinations are likely to perform under different modules.


> 假设我们有一个双模块的问答系统，分别是：
>
> Module 1：检索（Retrieve）
> Module 2：回答（Answer）
> 
> Step 1：准备示例（Bootstrap Demonstrations）
> 为检索模块准备了一些示例（Demo Set 1）：
> 示例 1：问题 “Who wrote ‘Pride and Prejudice’?” → 查询 “author of Pride and Prejudice”
> 示例 2：问题 “What is the capital of France?” → 查询 “capital of France”
> 为回答模块准备了一些示例（Demo Set 2）：
> 示例 1：已检索到上下文 “…(Jane Austen…)…” → 回答：“The author is Jane Austen.”
> 示例 2：已检索到上下文 “…(Paris is the capital of France)…” → 回答：“The capital is Paris.”
>
> Step 2：提出候选指令（Propose Instruction Candidates）
> 对检索模块，MIPRO 生成了 3 个候选指令：
> Instruction 1.A："Given a question, produce a direct keyword-based search query."
> Instruction 1.B："Generate a comprehensive search query that covers all relevant entities."
> Instruction 1.C："Rewrite the question in a short format for efficient retrieval."
> 对回答模块，MIPRO 也生成了 3 个候选指令：
> Instruction 2.A："Given the context, provide a concise answer focusing on key facts."
> Instruction 2.B："Answer the question in one sentence, referencing the relevant detail."
> Instruction 2.C："Summarize the context to derive a straightforward, factual answer."
> 与此同时，每个指令都可以搭配对应的一组示例（Demo Set 1.x、Demo Set 2.x），形成许多可能的组合。
>
> Step 3：贝叶斯优化（Jointly Tune with Bayesian Optimizer）
> 初始化：
> 
> 贝叶斯优化器随机挑选一个组合，例如：
> 检索模块：Instruction 1.A + Demo Set 1.A
> 回答模块：Instruction 2.B + Demo Set 2.C
> 让 LM Program 在验证集上跑出一个总得分（如 70%）。
> 迭代试验：
> 
> 根据试验结果，优化器更新其代理模型，对其他可能的组合进行打分预测，并选择最有潜力的一批组合进行下一次测试。
> 例如在第 2 次试验中选择：
> 检索模块：Instruction 1.B + Demo Set 1.C
> 回答模块：Instruction 2.A + Demo Set 2.B
> 得分可能变成 80%，更高了！
>
> 持续更新：
> 随着试验次数增加，贝叶斯优化器不断更新对“哪些指令与示例组合最有效”的认识。
> 它会试图平衡“探索”（尝试新组合）和“利用”（在已有数据上优化）之间的关系。
> 输出最优配置：
>
> 在若干次试验后，发现某个组合比如：Instruction 1.B + Demo Set 1.A + Instruction 2.A + Demo Set 2.B 得分 85% ，是最好的。
> MIPRO 最终返回这个组合作为“最佳 LM Program”配置。