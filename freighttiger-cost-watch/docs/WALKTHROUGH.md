# 10-Minute Walkthrough Script

**0:00-1:00 Problem and Insight**
"Two things break naive anomaly detection approaches on this dataset: (1) Some routes (like Mumbai-Pune) are structurally more expensive than peers, so raw peer comparison flags them forever; (2) A slow creep hides inside an 8-week average. Also, context notes are traps: several say costs were NOT affected."

**1:00-4:00 Architecture**
"Here is the architecture flow: Deterministic core -> detector -> retrieval ranks notes -> a deterministic gate decides applicability -> evidence packet -> template/LLM reason -> validator. The key rule here is that **the LLM never decides the verdict**, it only rephrases decided facts. This guarantees reproducibility."

**4:00-7:00 Live Demo**
"Let's look at a few examples generated in our output.csv:
1. **Justified**: Ahmedabad-Mumbai 2025-01-20 -> Caught the N002 note (same Monday, festival, +29%).
2. **The trap**: Chennai-Bangalore 2025-03-10 is still +22% but N001's flood window ended 03-08 and N009 says normal -> This was correctly flagged as unexplained, not stretched to fit.
3. **Creep**: Mumbai-Pune Dec 2025 -> caught by our drift signal. The short-term average misses this."

**7:00-9:00 How I know it is right**
"Sample rows reproduce to the exact decimal. I have verification checks validating 4/4 explicit traps including injection backtests. The script runs deterministically so multiple runs yield the exact same output.csv hash."

**9:00-10:00 Cost and Limits**
"Since we fall back to a deterministic template generation, token cost is zero. In a live environment with an LLM, calls would be strictly bounded to candidate rows. The main limitation is that the drift thresholds were tuned on this specific dataset; scaling to 10x routes would provide richer per-route standard deviations for better dynamic thresholding."

## Questions to prepare for:
- **Why not let the LLM judge whether a note applies?** (Nondeterminism, hallucination risk; applicability is a rule-checkable fact.)
- **Why is a vector DB reasonable for 10 notes?** (Interface scales; hybrid metadata gate + semantic rank is what you would keep at 10,000 notes.)
- **How would this run streaming?** (Baselines are strictly backward-looking `shift(1)`, so we just process each new Monday incrementally.)
