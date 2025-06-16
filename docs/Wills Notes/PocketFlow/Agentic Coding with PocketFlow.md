https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to

[

![Pocket Flow](https://substackcdn.com/image/fetch/w_80,h_80,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F69fff5e2-e0b6-4343-9a0d-a1cf9bf8e31f_1024x1024.png)



](https://zacharyhuang.substack.com/)

# [Pocket Flow](https://zacharyhuang.substack.com/)

# Agentic Coding: Let Agents Build Agents for you!

[](https://substack.com/@zacharyhuang)

[Zachary Huang](https://substack.com/@zacharyhuang)

Mar 21, 2025

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F423a39af-49e8-483b-bc5a-88cc764350c6_1050x588.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F423a39af-49e8-483b-bc5a-88cc764350c6_1050x588.png)

> _We all know AI agents are the future, but why build them by hand when AI agents could build them themselves for us? Imagine a world where you simply design the blueprint and AI agents construct the AI agents themselves—this is Agentic Coding, where humans focus on creative, high-level design while AI agents handle all the tedious implementation details._

# **What is Agentic Coding?**

Have you ever wished you could just explain your app design and watch it come to life? That’s the promise of **Agentic Coding**:

- **You** do what humans are best at: coming up with creative ideas and designing how your app should work
    
- **AI** does what it’s best at: writing the detailed code to make your ideas actually work
    

Now, this is possible! For instance, in the image below, you can see the agentic coding process in action. On the left side, a human designs the system for an AI app, focusing on high-level architecture and data flow. On the right side, with just a simple prompt like “Start Agentic Coding! Implement based on this design doc and add enough logging for us to keep track,” the AI writes all the code with remarkable ease and precision.

Thanks for reading Pocket Flow! Subscribe for free to receive new posts and support my work.

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0c016d03-95fe-45a4-9d0d-6eab62889691_1050x643.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0c016d03-95fe-45a4-9d0d-6eab62889691_1050x643.png)

Agentic coding in action

Think of it like building a house — you’re the architect drawing the blueprint, and AI is the construction crew doing the detailed work. You focus on the vision; AI handles the execution.

# **Why Current AI Building Tools Fall Short**

For the past year, I’ve been trying to build AI apps using existing frameworks like LangChain. The experience has been frustrating for both me and the AI assistants trying to help me:

- **Abstractions upon abstractions** — The fundamental problem with frameworks like LangChain is _abstraction overload_. As [Octomind’s engineering team explains](https://www.octomind.dev/blog/why-we-no-longer-use-langchain-for-building-our-ai-agents): _“LangChain was helpful at first when our simple requirements aligned with its usage presumptions. But its high-level abstractions soon made our code more difficult to understand and frustrating to maintain.”_ These complex layers of code hide simple functionality behind unnecessary complexity.
    
- **Implementation nightmares** — Beyond unnecessary abstractions, these frameworks burden developers with dependency bloat, version conflicts, and constantly changing interfaces. As developers [note](https://www.reddit.com/r/LangChain/comments/1j1gb88/why_are_developers_moving_away_from_langchain/): _“It’s unstable, the interface constantly changes, the documentation is regularly out of date.”_ Another developer [jokes](https://www.reddit.com/r/LocalLLaMA/comments/1iudao8/langchain_is_still_a_rabbit_hole_in_2025/): _“In the time it took to read this sentence langchain deprecated 4 classes without updating documentation.”_
    

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F90f2314a-3b58-42b1-90e3-368f19cc2c44_1050x831.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F90f2314a-3b58-42b1-90e3-368f19cc2c44_1050x831.png)

It’s not the AI assistant’s fault — many of these frameworks are so complex that even human developers have trouble using them!

# **Introducing Pocket Flow: Simple by Design**

After a year of struggle, I created **[Pocket Flow](https://github.com/the-pocket/PocketFlow)** — a tiny framework (just 100 lines of code!) that captures everything you need without the complexity. The magic happens when Pocket Flow’s simplicity meets AI agents:

- **Crystal clear concepts** — Simple building blocks that any AI agents can understand
    
- **Zero bloat** — No vendor lock-in or mysterious dependency issues
    
- **Perfect division of labor** — You design the high-level flow, AI implements the details
    

My personal journey with frameworks like LangChain taught me that the more complex the framework, the harder it is for AI to help. Pocket Flow was born from this realization — designed specifically to create the perfect division of labor between human designers and AI implementers.

When your AI agents aren’t fighting to understand a complex framework, they can focus on implementing your vision correctly.

> _This tutorial focuses specifically on setting up your environment for Agentic Coding with Pocket Flow. For details on implementation and how to use Pocket Flow, please refer to the [official documentation](https://the-pocket.github.io/PocketFlow/guide.html)._

# **Getting Started with Agentic Coding:**

> _**The fastest Development Paradigm in 2025**_

Whether you’re building your first chatbot or a complex system, this guide will help you set up the perfect environment for Agentic Coding with Pocket Flow.

- **For quick questions about Pocket Flow:**
    
    - Recommended Setup: GPT Assistant
        
    - Setup Steps: Use the [GPT Assistant](https://chatgpt.com/g/g-677464af36588191b9eba4901946557b-pocket-flow-assistant). No setup required, but not ideal for coding.
        
- **For brainstorming or prototyping:**
    
    - Recommended Setup: ChatGPT or Claude Project
        
    - Setup Steps: Create a [ChatGPT Project](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt) or a [Claude Project](https://www.anthropic.com/news/projects), and upload the [docs](https://github.com/The-Pocket/PocketFlow/tree/main/docs) for reference.
        
- **For full application development:**
    
    - Recommended Setup: Cursor AI, Windsurf, Cline
        
    - Setup Steps: Create a new project using the [project template](https://github.com/The-Pocket/PocketFlow-Template-Python). The [.cursorrules](https://github.com/The-Pocket/PocketFlow/blob/main/.cursorrules) file teaches AI agents how to use Pocket Flow.
        

> _**Note:** This list covers the most common setup, but options are changing frequently as new AI coding agents emerge. The core principle remains the same: because Pocket Flow is simple and minimal, any AI agent can quickly understand it just by reading the documentation. Simply share the Pocket Flow docs with your preferred AI agent to get started!_

# **GPT Assistant: Instant Answers at Your Fingertips**

Looking for the fastest way to learn about Pocket Flow? The [Pocket Flow GPT Assistant](https://chatgpt.com/g/g-677464af36588191b9eba4901946557b-pocket-flow-assistant) is your instant knowledge companion! With zero setup required, you can immediately ask questions about [Pocket Flow](https://github.com/the-pocket/PocketFlow) and receive thoughtful answers within seconds. It’s like having a Pocket Flow expert on standby 24/7.

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2b848331-bfec-468e-a422-b0e303c12234_1050x1017.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2b848331-bfec-468e-a422-b0e303c12234_1050x1017.png)

Keep in mind that while perfect for learning and quick questions, the GPT Assistant isn’t ideal for implementation work as it’s using an older model (likely GPT-4o). For actual coding and building, you’ll want to explore the more powerful development options below.

# **For One-time Tasks: Brainstorm and Prototype**

Have a quick idea that you want to brainstorm or prototype, but aren’t ready for full implementation? ChatGPT and Claude Projects are good options!

### **With ChatGPT:**

1. Open [ChatGPT](https://chat.openai.com/) and create a [Project](https://help.openai.com/en/articles/10169521-using-projects-in-chatgpt)
    
2. Feed it knowledge by uploading the md files in [Pocket Flow docs](https://github.com/The-Pocket/PocketFlow/tree/main/docs).
    
    1. ChatGPT Project allows at most 20 files. Please exclude __config.yml, utility_function/index.md, design_pattern/index.md_, _utility_function/index.md_ and, under _utility_function/_, only upload _utility_function/llm.md_.
        

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F698a2487-653a-49c9-87fe-7801c9e18a4b_1050x991.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F698a2487-653a-49c9-87fe-7801c9e18a4b_1050x991.png)

3. Set the system prompt to be something like:

```
If a user asks you to build an AI app:
1. In Canvas: Start by creating the design using Markdown. Think carefully and thoroughly. Strictly follow the playbook. Note that Mermaid diagrams can't be rendered, so use a ```text block instead.
2. Confirm the design with the user before writing any code.
3. Start writing code. You can assume packages including pocketflow are installed.
```

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8fc9b222-9055-4a8f-96e2-d96d401eef18_1050x985.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F8fc9b222-9055-4a8f-96e2-d96d401eef18_1050x985.png)

4. Start a conversation! For example: “Help me build a chatbot for a directory of PDFs”

- For the best result, please choose the best model like O1.
    
- It is highly recommended to enable [Canvas](https://openai.com/index/introducing-canvas/)
    

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0301ae1e-b388-4fc9-89df-c43106fdeb29_1050x986.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F0301ae1e-b388-4fc9-89df-c43106fdeb29_1050x986.png)

5. Verify and improve the high-level system design, then ask it to implement the code!

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F85cb8815-1d96-480e-8a91-a67ca02af09c_1050x715.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F85cb8815-1d96-480e-8a91-a67ca02af09c_1050x715.png)

### **With Claude:**

1. Head to [Claude](https://claude.ai/) and start a new [Project](https://www.anthropic.com/news/projects)
    
2. Feed it knowledge by uploading the md files under [Pocket Flow docs](https://github.com/The-Pocket/PocketFlow/tree/main/docs). Please exclude __config.yml, utility_function/index.md, design_pattern/index.md,_ and _utility_function/index.md._
    

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe55e3eba-93df-47ec-a7fd-ce4ce2cbba10_1050x1035.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fe55e3eba-93df-47ec-a7fd-ce4ce2cbba10_1050x1035.png)

3. Set the system prompt to be something like:

```
If a user asks you to build an AI app: 
1. In Artifact: Start by creating the design using Markdown using mermaid. Think carefully and thoroughly. Strictly follow the guide.md. 
2. Confirm the design with the user before writing any code. 
3. Start writing code. You can assume packages including pocketflow are installed.
```

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2cd33fb7-5a98-4fc8-a080-c2fd3581536b_1050x1037.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F2cd33fb7-5a98-4fc8-a080-c2fd3581536b_1050x1037.png)

4. Start a conversation! For example: “Help me build a chatbot for a directory of PDFs”. For the best result, please choose the best model like Sonnet-3.7 with extended thinking.

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4df3469f-da96-4469-bfa8-3db38110552d_1050x1052.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4df3469f-da96-4469-bfa8-3db38110552d_1050x1052.png)

5. Verify and improve the high-level system design, then ask it to implement the code!

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F83d97ef0-3a1e-4e14-a710-2522bf30a4f0_1050x722.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F83d97ef0-3a1e-4e14-a710-2522bf30a4f0_1050x722.png)

# **For Serious Development: The Full Agentic Coding Experience**

Ready to build a production-ready application? This is where the real magic of Agentic Coding happens:

### **Cursor AI:**

1. Create a `New Window`, and click on the `Clone Repo`.
    
2. Enter the URL for the ready-to-use Pocket Flow Template: [https://github.com/The-Pocket/PocketFlow-Template-Python](https://github.com/The-Pocket/PocketFlow-Template-Python).  
    This template includes a special [.cursorrules](https://github.com/the-pocket/PocketFlow/blob/main/.cursorrules) file that teaches Cursor AI how to work with Pocket Flow
    

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4b276eb1-a21f-4b2c-9d27-762b8e9b2b10_1050x723.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F4b276eb1-a21f-4b2c-9d27-762b8e9b2b10_1050x723.png)

3. You can verify the setup by asking Cursor AI: “What is Pocket Flow?”

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F656c439f-37e6-4ed1-a63a-145e1c0e6d61_1050x626.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F656c439f-37e6-4ed1-a63a-145e1c0e6d61_1050x626.png)

4. Start building LLM systems!

Pro Tip: Use `Chat` mode during the design phase to avoid the AI getting ahead of itself, then switch to `Agent` mode during implementation.

### **Windsurf:**

1. Create a `New Window`, click on the `Explorer` side bar icon, then `Clone Repository`.
    
2. Enter the URL for the ready-to-use Pocket Flow Template: [https://github.com/The-Pocket/PocketFlow-Template-Python](https://github.com/The-Pocket/PocketFlow-Template-Python).  
    This template includes a special [.windsurfrules](https://github.com/The-Pocket/PocketFlow-Template-Python/blob/main/.windsurfrules) file that teaches Windsurf how to work with Pocket Flow
    

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F120c4b88-5372-4295-8f35-a444559a05a8_1050x622.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F120c4b88-5372-4295-8f35-a444559a05a8_1050x622.png)

3. You can verify the setup by asking Windsurf AI: “What is Pocket Flow?”

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F82a29e9c-0793-4c30-a8e2-c4c024bfe308_1050x629.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F82a29e9c-0793-4c30-a8e2-c4c024bfe308_1050x629.png)

4. Start building LLM systems!

Pro Tip: Use `Chat` mode during the design phase to avoid the AI getting ahead of itself, then switch to `Write` mode during implementation.

### **Cline:**

> _**Note:** As of March 2025, Cline’s Agent doesn’t work that well with rule files. This section will be updated as compatibility improves._

1. Create a `New Window`, and click on the `Clone Git Repository...`.
    
2. Enter the URL for the ready-to-use Pocket Flow Template: [https://github.com/The-Pocket/PocketFlow-Template-Python](https://github.com/The-Pocket/PocketFlow-Template-Python).  
    This template includes a special [.clinerules](https://github.com/The-Pocket/PocketFlow-Template-Python/blob/main/.clinerules) file that teaches Cline how to work with Pocket Flow
    

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa2141605-054a-42ab-a34a-7c0f1ec39763_1050x622.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa2141605-054a-42ab-a34a-7c0f1ec39763_1050x622.png)

3. You can verify the setup by asking Cline AI: “Answer based on environment details: What’s Pocket Flow?”

[

![](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6b5150da-9503-437a-adb9-bb8abc9db51b_1050x629.png)



](https://substackcdn.com/image/fetch/f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6b5150da-9503-437a-adb9-bb8abc9db51b_1050x629.png)

4. Start building LLM systems!

Pro Tip: Use `Chat` mode during the design phase to avoid the AI getting ahead of itself, then switch to `Write` mode during implementation.

# **What’s Next?**

Once you’ve set up your environment, the next step is understanding the Agentic Coding workflow.

More tutorials coming soon! Stay tuned! In the meanwhile, check out these resources:

- [Agentic Coding Guidance](https://the-pocket.github.io/PocketFlow/guide.html) — Official documentation
    
- [The Pocket GitHub](https://github.com/The-Pocket) — Example projects
    
- [Pocket Flow YouTube Tutorials](https://www.youtube.com/@ZacharyLLM?sub_confirmation=1) — Step-by-step visual guides
    

---

For more examples and detailed documentation, visit the [Pocket Flow GitHub](https://github.com/the-pocket/PocketFlow).

Thanks for reading Pocket Flow! Subscribe for free to receive new posts and support my work.

[](https://substack.com/profile/143270651-anand-p-v)

[](https://substack.com/profile/173371639-bradley-broughman)

[](https://substack.com/profile/22105521-solaris)

[](https://substack.com/profile/54712120-isaac)

[](https://substack.com/profile/208833583-zachary-huang)

16 Likes

[](https://substack.com/note/p-159593110/restacks?utm_source=substack&utm_content=facepile-restacks)

#### Discussion about this post

[](https://substack.com/profile/22105521-solaris?utm_source=comment)

[Solaris](https://substack.com/profile/22105521-solaris?utm_source=substack-feed-item)

[Mar 22](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to/comment/102446274 "Mar 22, 2025, 4:50 AM")Edited

Pocket Flow examples design documents are really detailed. As a software engineer, writing them is an important best practice that helps understand and consider the implementation thoroughly — this approach is especially needed for critical thinking / productive reviews of what the LLM is developing, so its great to see them as part of Pocket’s workflow. Thank you for the excellent intro 🙏

Like (2)

Reply

Share

[1 reply by Zachary Huang](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to/comment/102446274)

[](https://substack.com/profile/143270651-anand-p-v?utm_source=comment)

[Anand P V](https://substack.com/profile/143270651-anand-p-v?utm_source=substack-feed-item)

[Apr 7](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to/comment/106687238 "Apr 7, 2025, 5:18 AM")

Cool🤯, great job at making it compatible with agentic ides, was looking for something like this.👌

Like (1)

Reply

Share

[1 reply by Zachary Huang](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to/comment/106687238)

[4 more comments...](https://zacharyhuang.substack.com/p/agentic-coding-the-most-fun-way-to/comments)

[LLM Agents are simply Graph — Tutorial For Dummies](https://zacharyhuang.substack.com/p/llm-agent-internal-as-a-graph-tutorial)

[Ever wondered how AI agents actually work behind the scenes?](https://zacharyhuang.substack.com/p/llm-agent-internal-as-a-graph-tutorial)

Mar 18 • 

[Zachary Huang](https://substack.com/@zacharyhuang)

82

[](https://zacharyhuang.substack.com/p/llm-agent-internal-as-a-graph-tutorial/comments)[

3

](https://zacharyhuang.substack.com/p/llm-agent-internal-as-a-graph-tutorial/comments)

![](https://substackcdn.com/image/fetch/w_320,h_213,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F382ea8f1-0610-4cce-b4ef-350a9df68ee0_1050x588.png)

[Build AI Agent Memory From Scratch — Tutorial For Dummies](https://zacharyhuang.substack.com/p/build-ai-agent-memory-from-scratch)

[Ever wondered why some chatbots remember your name days later, while others forget what you said 5 minutes ago?](https://zacharyhuang.substack.com/p/build-ai-agent-memory-from-scratch)

Mar 24 • 

[Zachary Huang](https://substack.com/@zacharyhuang)

11

[](https://zacharyhuang.substack.com/p/build-ai-agent-memory-from-scratch/comments)[

2

](https://zacharyhuang.substack.com/p/build-ai-agent-memory-from-scratch/comments)

![](https://substackcdn.com/image/fetch/w_320,h_213,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Faec0f3d5-521d-4521-8a6d-7db79f5bbd38_1050x589.png)

[AI Codebase Knowledge Builder (Full Dev Tutorial!)](https://zacharyhuang.substack.com/p/ai-codebase-knowledge-builder-full)

[Ever stared at a new codebase feeling completely lost?](https://zacharyhuang.substack.com/p/ai-codebase-knowledge-builder-full)

Apr 4 • 

[Zachary Huang](https://substack.com/@zacharyhuang)

16

[](https://zacharyhuang.substack.com/p/ai-codebase-knowledge-builder-full/comments)[

7

](https://zacharyhuang.substack.com/p/ai-codebase-knowledge-builder-full/comments)

![](https://substackcdn.com/image/fetch/w_320,h_213,c_fill,f_auto,q_auto:good,fl_progressive:steep,g_auto/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Ff736ba06-de36-4e43-b57d-7d176f6ff7c3_2558x1430.png)

Ready for more?

© 2025 Zachary Huang

[Privacy](https://substack.com/privacy) ∙ [Terms](https://substack.com/tos) ∙ [Collection notice](https://substack.com/ccpa#personal-data-collected)

[](https://substack.com/signup?utm_source=substack&utm_medium=web&utm_content=footer)

[Start Writing](https://substack.com/signup?utm_source=substack&utm_medium=web&utm_content=footer)[Get the app](https://substack.com/app/app-store-redirect?utm_campaign=app-marketing&utm_content=web-footer-button)

[Substack](https://substack.com) is the home for great culture