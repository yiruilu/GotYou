# GotYou Architecture

## Current MVP

The first MVP focuses on helping users revise an academic paper through structured coaching and related-paper discovery.

---

## User Input

The user provides:

- The paper or draft
- Reviewer comments
- Revision deadline
- Personal requirements or concerns
- Optional research topic or keywords

---

## Agent Workflow

1. Understand the user's revision goal
2. Read the paper and reviewer comments
3. Identify the main research topic and keywords
4. Identify the main revision issues
5. Search for related academic papers
6. Summarize the most relevant papers
7. Explain how each paper relates to the user's paper
8. Rank revision issues by priority
9. Break the revision into manageable tasks
10. Generate the first recommended task
11. Wait for the user's progress update
12. Adjust the next task based on the result

---

## Related Paper Discovery

For each related paper, GotYou should provide:

- Paper title
- Authors
- Publication year
- Source or link
- Short summary
- Main method or argument
- Key findings
- Relevance to the user's paper
- Possible use in the revision

Possible uses include:

- Supporting an argument
- Improving the literature review
- Identifying a research gap
- Comparing methods
- Strengthening evidence
- Finding missing citations

---

## Output

GotYou provides:

- A prioritized revision checklist
- A list of related papers
- A summary of each paper
- An explanation of its relevance
- Suggestions for how the paper may support the revision
- A clear first revision task
- An updated plan after the user reports progress

---

## Initial Flow

```text
User
  ↓
Provides paper, comments, and deadline
  ↓
GotYou understands the research goal
  ↓
Extracts topic and keywords
  ↓
Analyzes revision needs
  ↓
Searches for related papers
  ↓
Summarizes and compares the papers
  ↓
Creates a prioritized revision plan
  ↓
Assigns the first task
  ↓
User reports progress
  ↓
GotYou adjusts the next task