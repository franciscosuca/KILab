# Local Model Inventory: LM Studio and oMLX

A machine-specific snapshot of local models and provider visibility, based on the live LM Studio and oMLX model APIs and the current `~/.lmstudio/models` folders. This is a working inventory, not a benchmark.

## Machine and provider notes

- Machine: Apple M5, 32 GB unified memory.
- LM Studio endpoint: `http://localhost:11440/v1`.
- oMLX endpoint: `http://127.0.0.1:8000/v1`.
- The live LM Studio API currently reports **8 generative models** and an embedding model.
- The live oMLX API exposes **7 generative models**. It discovers compatible MLX/safetensors models in `~/.lmstudio/models`; the GGUF Qwen3.6 model and custom Splash/Yuzu bundle are not currently in its API list.
- LM Studio currently does not list the Gemma 4 12B folder, while oMLX does.
- Pi's chat model list should omit Nomic Embed Text: it is for embeddings/RAG, not text generation.
- MoE reduces the parameters used per token; it does not reduce the need to load the model's full weights. Large models plus a long context can still pressure 32 GB unified memory. oMLX is currently configured with a 32K context-window limit.

## Model table

| Model / local folder | Suggested purpose | Architecture | LM Studio model ID | oMLX model ID | My biased take |
|---|---|---|---|---|---|
| `mlx-community/gpt-oss-20b-MXFP4-Q8` | Text-first agent: reasoning and tool calls | **MoE** — 32 experts, 4 selected per token | `openai/gpt-oss-20b` | `gpt-oss-20b-MXFP4-Q8` | My text-agent pick. Strong tool-use fit, but no vision. |
| `lmstudio-community/Qwen3.8-27B-MLX-4bit` | General agent, harder coding/planning, image/video input | **Dense** | `qwen/qwen3.8-27b` | `Qwen3.8-27B-MLX-4bit` | My all-rounder pick across both providers. Good breadth, but treat it as a one-large-model-at-a-time choice. |
| `lmstudio-community/Qwen3.5-9B-MLX-4bit` | Faster, lighter agent or routine sub-agent | **Dense** | `qwen/qwen3.5-9b` | `Qwen3.5-9B-MLX-4bit` | Best lightweight option here. I would not rely on it alone for the hardest multi-step tasks. |
| `lmstudio-community/Qwen3.6-35B-A3B-GGUF` | Heavy coding, multimodal and tool-use tasks | **MoE** — 35B total, A3B | `qwen/qwen3.6-35b-a3b` | — | Attractive architecture on paper, but its roughly 22 GB GGUF leaves limited room for context and other apps on this machine. LM Studio only. |
| `lmstudio-community/gemma-4-26B-A4B-it-QAT-MLX-4bit` | Multimodal general-purpose agent | **MoE** — 26B total, A4B | `google/gemma-4-26b-a4b-qat` | `gemma-4-26B-A4B-it-QAT-MLX-4bit` | A credible Qwen3.8 alternative. I would compare both on actual tasks rather than keep both loaded/selected as main models. |
| `incoai/Qwen3.8-27B-Splash` | Speed-oriented Qwen3.8 inference with a bundled draft model | **Dense** — same target architecture as Qwen3.8 | `qwen3.8-27b-splash` | — | Specialized Splash/Yuzu format, not a new capability. Try it in LM Studio if it is faster for you; it is not exposed by oMLX. |
| `mlx-community/QwQ-DeepSeek-R1-SkyT1-Flash-Lightest-32B-mlx-4Bit` | Deep reasoning or a second opinion | **Dense** — Qwen2-based | `qwq-deepseek-r1-skyt1-flash-lightest-32b-mlx` | `QwQ-DeepSeek-R1-SkyT1-Flash-Lightest-32B-mlx-4Bit` | A reasoning specialist, not my default agent. It is a large model and has no vision. |
| `BlueMoonlight/deepseek-moe-16b-chat-mlx-4Bit` | General chat | **MoE** — config routes 6 experts per token | `deepseek-moe-16b-chat-mlx` | `deepseek-moe-16b-chat-mlx-4Bit` | I would not pick it for agentic work: LM Studio marks it as not trained for tool use, and its configured context is only 4K. |
| `lmstudio-community/gemma-4-12B-it-MLX-8bit` | Mid-size multimodal assistant | **Dense** | — (not listed by LM Studio currently) | `gemma-4-12B-it-MLX-8bit` | oMLX sees it, LM Studio does not currently list it. I would choose the 9B Qwen for a lighter everyday agent unless you prefer Gemma's behavior. |
| Nomic Embed Text v1.5 (LM Studio-indexed GGUF embedding model) | Embeddings for retrieval/RAG | **Dense encoder** | `text-embedding-nomic-embed-text-v1.5` | — | Useful for local retrieval, but it is not a chat or agent model. |

## Reading the architecture column

- **Dense:** most model weights participate in each forward pass.
- **MoE:** a router selects a subset of experts per token. The A3B/A4B labels indicate the approximate active parameter scale, not the full weight memory required.
- Architecture is only one factor in agent quality. Tool-call formatting, the provider runtime, context budget, and the agent's tool configuration matter too.
