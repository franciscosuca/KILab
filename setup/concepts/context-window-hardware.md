# Context Window vs. Hardware: How Much Can You Actually Use?

The context length slider in LM Studio is not free. Every token in the context
window consumes RAM for the model's **KV cache**. This file gives you the
formula to compute the largest context your machine can hold.

## The formula

```text
max_context_tokens = memory_available_for_kv_cache / kv_bytes_per_token
```

### Step 1 — Memory available for the KV cache

On Apple Silicon (unified memory), the GPU can use roughly 70% of total RAM:

```text
memory_available_for_kv_cache = (total_RAM x 0.7) - model_weights_size - ~2 GB (OS/apps overhead)
```

`model_weights_size` is the size shown next to the loaded model in LM Studio
(e.g. 1.66 GB for `qwen2.5-coder-1.5b-instruct-mlx`).

Example with 16 GB RAM and a 1.7 GB model:

```text
(16 GB x 0.7) - 1.7 GB - 2 GB = ~7.5 GB available for KV cache
```

### Step 2 — KV cache bytes per token

```text
kv_bytes_per_token = 2 (K and V) x num_layers x num_kv_heads x head_dim x dtype_bytes
```

- `dtype_bytes` = 2 for fp16 (LM Studio default), 1 for 8-bit KV quantization.
- Get `num_layers` (`num_hidden_layers`), `num_kv_heads`
  (`num_key_value_heads`), and `head_dim` (`hidden_size / num_attention_heads`)
  from the model's `config.json` on Hugging Face.

Worked examples (fp16 KV cache):

| Model | Layers | KV heads | head_dim | KiB/token | Tokens per GiB |
| --- | --- | --- | --- | --- | --- |
| Qwen2.5-Coder-1.5B | 28 | 2 | 128 | ~28 KiB | ~37,000 |
| Llama-3.1-8B | 32 | 8 | 128 | ~128 KiB | ~8,200 |
| Qwen2.5-32B | 64 | 8 | 128 | ~256 KiB | ~4,100 |

### Step 3 — Divide

Continuing the 16 GB example with the 1.5B model:

```text
7.5 GiB / 28 KiB per token = ~280,000 tokens
```

The hardware would allow more than the model's 128k maximum — so the context
slider, not RAM, is the limit. With an 8B model the same machine allows only:

```text
7.5 GiB / 128 KiB per token = ~61,000 tokens
```

Setting the slider to 128k there would overflow into swap and crawl.

### Step 4 - Estimate RAM for a chosen context

Once you know the approximate KV-cache cost per token, multiply it by the
number of tokens:

```text
KV_cache_MiB ~= context_tokens x KiB_per_token / 1,024
KV_cache_GiB ~= context_tokens x KiB_per_token / 1,048,576
```

The following table uses the fp16 estimates above. MiB and GiB are the binary
versions of the MB and GB labels commonly shown by system monitors.

| Model | 8k tokens | 16k tokens | 32k tokens | 64k tokens | 128k tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen2.5-Coder-1.5B (~28 KiB/token) | ~224 MiB (0.22 GiB) | ~448 MiB (0.44 GiB) | ~896 MiB (0.88 GiB) | ~1.75 GiB | ~3.5 GiB |
| Llama-3.1-8B (~128 KiB/token) | ~1 GiB | ~2 GiB | ~4 GiB | ~8 GiB | ~16 GiB |
| Qwen2.5-32B (~256 KiB/token) | ~2 GiB | ~4 GiB | ~8 GiB | ~16 GiB | ~32 GiB |

These numbers are for the KV cache only. Add model weights, runtime buffers,
the operating system, applications, and backend-specific overhead before
comparing the total with the RAM installed in the machine.

## Shortcuts (@thesis)

- **Empirical check (easiest):** set the context length in LM Studio, load the
  model, and watch the memory estimate LM Studio shows. If total usage exceeds
  ~70% of your RAM, lower the slider.
- Enable **Flash Attention** in LM Studio — required for efficient long
  contexts.
- KV cache quantization (when available) halves or quarters the per-token cost.
- Keep `maxInputTokens + maxOutputTokens` in VS Code's
  `chatLanguageModels.json` at or below the value you validated here. See
  [vscode/vscode-context-requirements.md](vscode/vscode-context-requirements.md).

## Rules of thumb (@thesis)

| Total RAM | Practical context (7-9B model) | Approx. KV cache (7-9B) | Practical context (1-3B model) | Approx. KV cache (1-3B) |
| --- | --- | ---: | --- | ---: |
| 8 GB | 8k-16k | ~1-2 GiB | 32k | ~0.9 GiB |
| 16 GB | 32k-64k | ~4-8 GiB | 64k-128k | ~1.75-3.5 GiB |
| 32 GB | 64k-128k | ~8-16 GiB | 128k | ~3.5 GiB |
| 64 GB+ | 128k | ~16 GiB | 128k+ | >=3.5 GiB |

The 7-9B cache column uses the Llama-3.1-8B estimate of 128 KiB per token.
The 1-3B cache column uses the Qwen2.5-Coder-1.5B estimate of 28 KiB per
token. All cache figures exclude model weights and the other memory described
in Step 4.

## Sources

- [Hugging Face Transformers - Caching](https://huggingface.co/docs/transformers/main/en/cache_explanation) explains why key and value tensors are stored per layer and why cache memory grows with sequence length.
- [Qwen2.5-Coder-1.5B-Instruct config.json](https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct/raw/main/config.json) provides the layer, attention-head, and KV-head values used for the 1.5B estimate.
- [Qwen2.5-32B config.json](https://huggingface.co/Qwen/Qwen2.5-32B/raw/main/config.json) provides the corresponding architecture values used for the 32B estimate.
- [Meta Llama 3.1 8B model page](https://huggingface.co/meta-llama/Llama-3.1-8B) provides the reference model information used for the 8B estimate.
- [LM Studio documentation](https://lmstudio.ai/docs) covers local model loading and runtime configuration, including context-length choices.
