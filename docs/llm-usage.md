# LLM usage

| # | Stage | Model | Tokens in | Tokens out | Cost |
|---|-------|-------|-----------|------------|------|
| 1 | generation ([prompt 01](prompts/01-generation.md)) | deepseek/deepseek-v4-flash | 373k | 64k | $0.138 |
| **Σ** | | | **373k** | **64k** | **$0.138** |

Spec size: **861 tokens** (measured with [TokenCount](https://token-count.streamlit.app)).

Evidence — pi harness status line at the end of the session:

```
↑373k ↓64k R2.4M CH0.0% $0.138 9.6%/1.0M (auto)    (openrouter) deepseek/deepseek-v4-flash • high
```

Note: input includes the agent loop overhead (tool schemas, file reads,
iteration context) — the spec itself is only 861 tokens of it.
