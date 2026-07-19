# GotYou

> Your AI Academic Coach for Long-Term Learning.

GotYou is an AI academic coach designed to help students accomplish long-term academic goals.

Instead of simply answering questions, GotYou helps users plan, track, reflect, and complete complex academic tasks over weeks or even months.

The first version focuses on research assistance, but the long-term vision is to support every stage of academic learning.

---

## ✨ Vision

Most AI assistants answer questions.

GotYou goes one step further.

It remembers long-term goals, breaks large tasks into manageable steps, tracks progress over time, and continuously guides users toward completion.

Our goal is to build an AI coach that stays with students throughout their academic journey.

---

## 🚀 Current MVP

The first MVP focuses on academic research.

Current capabilities include:

- Research planning
- Literature review organization
- Paper revision guidance
- Daily research task generation

---

## 🛣 Roadmap

See:

docs/roadmap.md

---

## 🛠 Tech Stack

- Python
- OpenAI API (LLM-based planning)
- Git
- GitHub
- VS Code

(Additional LLM frameworks will be added in future versions.)

---

## ⚙️ Setup

The LLM planner (`LLMPlanner`) calls the OpenAI API and needs an API key.

1. Install dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

2. Configure your API key:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and set `OPENAI_API_KEY` to a key from
   [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
   `.env` is git-ignored — never commit it.

3. Run the sample planning workflow:

   ```bash
   python3 -m src.main
   ```

   Without a valid `OPENAI_API_KEY`, `LLMPlanner` still runs — it returns an
   empty plan with a warning explaining what's missing, instead of crashing.

---


## Author

Yirui Lu



                GotYou

         AI Academic Coach
                  │
    ┌─────────────┼──────────────┐
    │             │              │
Research      Coursework     Programming
 Coach          Coach           Coach
    │             │              │
    └─────────────┼──────────────┘
                  │
          Planning + Memory
          + Reflection + Tools