# garak (NVIDIA LLM vulnerability scanner)

Placeholder. garak scans the model itself (not the whole app) for known weaknesses
such as jailbreaks, encoding tricks and data leakage.

Planned first run against the local Ollama model:

```bash
uv run --with garak python -m garak --model_type ollama --model_name llama3.2:3b --probes promptinject,dan
```

Results will be summarized in `reports/`.
