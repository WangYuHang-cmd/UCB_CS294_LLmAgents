# Lab 02: LLM Security, Writing Attack Prompts
## Why Does LLM Security Matter?
As LLMs continue to become more accessible and integrated into critical everyday systems, having guarantees about the level of robustness and security properties is beneficial.

In modern LLM systems, here are some of the potential risks that are present:
- **Data Leakage:** The training data may include sensitive information. Ensuring that such information remains protected and secure is essential.
- **Illegal Content:** Through LLMs, illegal content or information may be generated.
- **Promotion of Bias:** Current biases may be spread and deepened through misaligned and biased models.
- **Fraud:** Generative AI could be used to create realistic yet convincing fraudulent content, such as in scams, phishing, or identity theft.

Addressing the security of LLMs and improving robustness against adversarial attacks is currently still an ongoing topic of research.

## Lab Context 
Within this lab, you will be writing attacks against an LLM system that we set up. Although you don't have immediate access to the LLM system itself, one piece of information that you're aware of is that the system message contains a secret key, which is an alphanumeric string. The attacks that you write will need to leak this key. **You will not be writing code within this lab.** You will write a total of two attacks, which you should place in `attack-1.txt` and `attack-2.txt`. **Do not modify the names of these files**.

## Common Prompt Hacking Techniques
To get you started, here are a few common techniques that have been noted to work against LLMs. They include the following:
- **Payload Splitting:** Separating the attack into multiple payloads, then forcing the model at the end to put all individual parts together.
- **Virtualization:** Describing a virtual setting that makes the LLM believe that the scene is purely fictional.
- **Obfuscation:** Adding additional layers of complexity/encoding to potentially banned tokens/questions.
- **Code Injection:** Forcing the LLM to either execute or generate code that may be harmful.

To get a better understanding and intuition of what each attack may look like, here are some relevant references:
- Link: [Summary of all prompt hacking techniques.](https://learnprompting.org/docs/prompt_hacking/introduction)
- Link: [A popular Medium article that summarizes the prompt hacking techniques.](https://medium.com/@austin-stubbs/llm-security-types-of-prompt-injection-d7ad8d7d75a3)
- Link: [Prompt injection with more detail about how GPT works.](https://hiddenlayer.com/research/prompt-injection-attacks-on-llms/)
- Link: [AWS guide on prompt engineering, which also discusses jailbreaks in the beginning.](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/llm-prompt-engineering-best-practices/llm-prompt-engineering-best-practices.pdf)

## Instructions and Task Description
You will be writing 2 attacks to extract a secret key hidden somewhere in the system message of the model. Getting the second attack correct is more challenging than writing the first attack. Write your attacks in the files `attack-1.txt` and `attack-2.txt`.

**Hint:** The staff solution attacks are part of the ones listed in "Common Prompt Hacking Techniques".

## Recommended Approach
The recommended workflow is to use the [OpenAI playground](https://platform.openai.com/playground/chat?models=gpt-4o-mini) to create a testing environment, where you can fill out a system message with a mock secret key. Please use the GPT-4o-mini model within the OpenAI playground. Within the OpenAI playground, you can iterate your attack prompts. Here is what the user interface of the OpenAI Playground looks like:

![alt text](openai-playground-mock-environment.png)

As seen in the above image, you can insert a system key into the system prompt (blue box). Keep the Temperature setting and the Top P setting at 1. You can write your attack prompts in the green box, where it says "Enter User Message". To reset the chat, you can click the clean button (brush icon).

**Hint: To create attack prompt 1, the defense system message is similar to the one in the image. For attack prompt 2, you may want to have a more comprehensive defensive system instruction when simulating your attack. We recommend appending additional lines to the system message, which inform the LLM to specifically look out for virtualization and token obfuscation techniques.**

## Grading and Submission
### UC Berkeley Students
Once you have completed the lab, zip the entire folder and submit it to Gradescope. You will be able to immediately see your score. **Be sure to fill out** `student_info.json` with your student information. Once again, be careful not to change the name of any of the files provided in the starter code folder for this lab. We will run your attacks on two defense prompts. Your score will be determined by how many of your attacks succeed. You will not see your score immediately. 

### MOOC Students
We will release a Google Form where you can write your attack contents. The limit per each attack is generous, sitting at 50,000 characters. Submit your attack prompt through this Google Form.