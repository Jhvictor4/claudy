# From 5 to 100 Points: Solving Korean Olympiad in Informatics Problems with Gemini 2.5 Pro

## Overview

This document describes how to improve Gemini 2.5 Pro's performance from 5 points to 100 points (perfect score) on Korean Olympiad in Informatics (KOI) algorithm problems using prompt engineering and a structured workflow based on the IMO 2025 gold medal paper.

**Problem**: Korean Olympiad in Informatics 2024 High School Division - "Ascending Order" problem
- **Initial Result**: 5 points out of 100
- **Final Result**: 100 points out of 100 (perfect score)

**Key Reference**: [Gemini Goes to IMO 2025 Paper](https://arxiv.org/pdf/2507.15855)

## Background

### Initial Attempts
- Multiple attempts with various LLMs (Grok 4, o3 pro, etc.) yielded at most 15 points
- Multi-turn conversations and detailed prompts did not improve results
- The author has no competitive programming expertise to provide feedback on generated code

### IMO 2025 Paper Summary

The paper describes how Gemini 2.5 Pro achieved a gold medal at IMO 2025 by solving 5 out of 6 problems using:
- Structured prompting
- Multi-stage verification pipeline
- Self-refinement loops

**Pipeline from the paper**:
1. Initial solution generation
2. Self-improvement
3. Verification and bug report generation
4. Bug report review
5. Solution correction/improvement (iterate back to step 3)
6. Accept or reject

**Settings**:
- Temperature: 0.1
- Thinking Budget: 32,768 tokens

## Adapted 5-Stage Workflow for Algorithm Problems

### Workflow Structure

```
[Problem Input]
    ↓
[Step 1: Initial Algorithm Design & Code Generation] → (Initial Solution)
    ↓
[Step 2: Self-Improvement] → (Improved Solution)
    ↓
[Step 3: Multi-faceted Verification] → (Verification Report)
    ↓
[Step 4: Verification Analysis] → (Confirmed Fix List)
    ↓
[Step 5: Code Correction & Optimization] → (Fixed Solution) ───┐
    ↑                                                           │
    │                         (Iterate)                         │
    └───────────────────────────────────────────────────────────┘
    ↓
[Final Submission]
```

### Step 1: Initial Algorithm Design & Code Generation

**Goal**: Generate the first complete solution with correct algorithm and efficient implementation.

**Key Instructions**:
1. Correctness and Efficiency are Paramount
2. Honesty About Completeness - don't guess, explain limitations if unsure
3. Use Python 3 with standard library only
4. Explain thought process clearly

**Output Format**:
1. Problem Analysis
2. Core Idea & Algorithm
3. Time & Space Complexity Analysis
4. Python Code
5. Key Edge Cases

### Step 2: Self-Improvement

**Goal**: Critically review and refine the initial solution.

**Review Dimensions**:
1. **Logical Robustness**: Any logical gaps or hidden assumptions?
2. **Code Efficiency**: Can time/space complexity be improved?
3. **Readability & Structure**: Are variables/functions clearly named?

**Output Format**:
1. Summary of Improvements
2. Refined Algorithm Explanation
3. Refined Python Code

### Step 3: Multi-faceted Verification

**Goal**: Act as a strict verifier (IOI coaching staff + automated judge) to find all issues.

**Issue Categories**:

**a. Critical Logic Error**:
- Fundamental approach is wrong
- Cannot produce correct answer in any case

**b. Time/Space Complexity Exceeded**:
- Logic is correct but exceeds constraints
- Will get "Time Limit Exceeded" or "Memory Limit Exceeded"

**c. Implementation Bug**:
- Algorithm idea is good but code has defects
- Examples: off-by-one errors, wrong variable usage, initialization issues

**d. Missed Edge Case**:
- Works for general cases but fails on boundary values
- Examples: N=0, sorted array, etc.

**Output Format**:
1. **Summary**:
   - Final Verdict (one sentence)
   - List of Findings (Location, Issue, Category)
2. **Detailed Verification Log**:
   - Step-by-step verification with quoted code sections

### Step 4: Verification Analysis

**Goal**: Act as senior coach to judge validity of verification report findings.

**Judgment**:
- **Valid Finding**: Accurate issue that requires fixing
- **False Positive**: Verifier misunderstood code, no fix needed

**Output Format**:
- Final List of Confirmed Issues with justification for each

### Step 5: Code Correction & Optimization

**Goal**: Fix all confirmed issues from Step 4.

**Instructions**:
1. Resolve all issues from verification report
2. Explain how each issue was fixed
3. Propose better algorithms/data structures if possible

**Output Format**:
1. Summary of Changes
2. Corrected Code (with comments on changes)

## Implementation Setup

### Google AI Studio Configuration
- **Model**: Gemini 2.5 Pro
- **Temperature**: 0.1
- **Thinking Budget**: 32,768 tokens
- **Tabs**: 5 separate tabs (one per step)

### Why Separate Tabs?
- **Prevent context pollution**: Each prompt has different goals
- **Clear data flow**: Explicit control over what context each stage sees
- **Avoid confusion**: Prevents mixing of different analytical perspectives

## The Final Breakthrough: Context Integration

### Problem After Step 5
- After completing steps 1-5: **27 points** (improvement from 5, but far from 100)
- Partial problems 1, 2, 4, 5: correct
- Partial problems 3, 6, 7: time limit exceeded

### Insight from Research
Paper: ["LLMs Get Lost In Multi-Turn Conversation"](https://arxiv.org/abs/2505.06120)
- Single-turn with comprehensive context > multi-turn conversation
- Context quality matters more than conversation length

### Solution: Unified Context Prompt

**Structure**:
```
<Core Instructions from Step 1>
[ Emphasize correctness, efficiency, honesty requirements ]

=================================================================
Based on the following thought process and context, write code.

<Problem>
{ Problem text }
</Problem>

<1st Generated Code>
{ Full Step 1 output }
</1st Generated Code>

<Self-Improvement of 1st Code>
{ Full Step 2 output }
</Self-Improvement of 1st Code>

<1st Verification of Improved Code>
{ Full Step 3 output }
</1st Verification of Improved Code>

<Evaluation & Improvement Plan>
{ Full Step 4 output }
</Evaluation & Improvement Plan>

<Improved Code (Code A)>
{ Full Step 5 output }
</Improved Code (Code A)>

<Test Results for Code A>
Score: 27 out of 100
- Partial Problem 1: Correct (5/5)
- Partial Problem 2: Correct (7/7)
- Partial Problem 3: Time Limit Exceeded on test 49 (0/28)
- Partial Problem 4: Correct (10/10)
- Partial Problem 5: Correct (5/5)
- Partial Problem 6: Time Limit Exceeded on test 64 (0/10)
- Partial Problem 7: Time Limit Exceeded on test 133 (0/35)
</Test Results for Code A>
```

### Result
**Using this unified context prompt: 100 points (perfect score)!**

## Key Findings & Insights

### 1. Test Results as Feedback
**Question**: Would it work without test results?

**Experiment**: Same unified prompt without test results section
- **Result**: 55 points (doubled from 27, but not 100)
- **Conclusion**: Test results are critical but not "cheating" - without the refined thought process from steps 1-5, adding test results alone doesn't help

### 2. Context Quality Over Quantity
- Previous attempts with multi-turn feedback led to performance degradation
- High-quality, structured context enables the model to reason about next steps
- XML tags provide clear semantic boundaries

### 3. Separation of Concerns
- Using 5 separate chat instances prevented context pollution
- Each stage focuses on its specific objective
- Final stage synthesizes all perspectives

### 4. Why It Worked
The breakthrough came from:
1. **Refined thought process** (Steps 1-5): Creates high-quality reasoning context
2. **Clear feedback** (test results): Provides concrete error signals
3. **Single-turn synthesis**: Allows model to reason holistically

## Practical Applications

This methodology can be applied to:
- Competitive programming problems (IOI, ICPC, etc.)
- Complex coding challenges
- Algorithm optimization tasks
- Any problem requiring iterative refinement with verification

## Future Work

Potential improvements:
1. **Automate the pipeline**: Build multi-agent system to execute all steps
2. **Generalize prompts**: Adapt for different problem domains
3. **Optimize iterations**: Determine when to stop refining
4. **Cost analysis**: Balance quality vs. token usage

## Conclusion

By combining:
- **Structured reasoning** (5-stage pipeline)
- **Context management** (separate instances + final synthesis)
- **Clear feedback** (test results)

We achieved a **20x improvement** (5 → 100 points) on a competitive programming problem using only prompt engineering, without any domain expertise or code modifications.

The key insight: LLMs need both **high-quality reasoning context** and **clear error signals** to perform complex problem-solving tasks.

---

**Note**: This approach demonstrates the power of prompt engineering and context management in maximizing LLM capabilities for complex technical tasks.