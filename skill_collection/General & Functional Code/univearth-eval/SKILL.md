---
name: "univearth-eval"
description: "This benchmark probes an LLM agent's ability to perform spatial-temporal reasoning and generate executable code for Earth Observation tasks. It evaluates whether models can correctly answer yes/no questions derived from scientific articles by leveraging remote sensing data via Google Earth Engine. Use when the user wants to benchmark on UnivEARTH, or asks about evaluating this task. Reports accuracy."
---

# univearth-eval

> Towards LLM Agents for Earth Observation — Kao et al. (2025) (arXiv:2504.12110, 2025)

## What this evaluates

This benchmark probes an LLM agent's ability to perform spatial-temporal reasoning and generate executable code for Earth Observation tasks. It evaluates whether models can correctly answer yes/no questions derived from scientific articles by leveraging remote sensing data via Google Earth Engine.

## Datasets

- **UnivEARTH** — total 140; splits: test (140)

## Metrics

- `accuracy` **(primary)** — range: [0, 1]
  - Calculated as the proportion of correctly answered yes/no questions out of the total number of questions. The paper also reports code executability rate for generated Google Earth Engine scripts.

## Input / output format

**Input**: Text from NASA Earth Observatory articles (with figures manually converted to text prompts) and a corresponding yes/no question requiring spatial or temporal comparison.

**Output**: A yes/no answer, optionally accompanied by executable Google Earth Engine JavaScript code to verify the answer.

## Scoring recipe

```python
correct = 0
for pred, gold in zip(predictions, gold_answers):
    if pred.strip().lower() in ['yes', 'no'] and pred.strip().lower() == gold.strip().lower():
        correct += 1
accuracy = correct / len(gold_answers)
```

## Common pitfalls

- Questions often require external geospatial data verification via Google Earth Engine, not just text comprehension.
- Many questions are derived from article figures that models do not see, requiring them to rely solely on text or generate code to access imagery.
- Dataset availability in GEE varies by sensor and time period; some questions are impossible to answer with standard GEE datasets.

## Evidence (verbatim from paper)

> LLM agents fail to generate executable code 58% of the time, resulting in only 33% accuracy—revealing critical gaps in grounding AI agents in domain-specific, spatial-temporal scientific queries.

## Citation

```bibtex
@misc{kao2025towards,
  title={Towards LLM Agents for Earth Observation},
  author={Kao et al. (2025)},
  year={2025},
  note={arXiv:2504.12110}
}
```

- arXiv: 2504.12110
