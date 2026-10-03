"""Benchmark a model running on LM Studio's OpenAI-compatible API."""

import argparse
import json
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser(description="Benchmark an LM Studio model")
    parser.add_argument("--model", required=True, help="Model ID (from /v1/models)")
    parser.add_argument("--message", required=True, help="Prompt to send")
    parser.add_argument("--port", type=int, default=11440, help="LM Studio server port")
    parser.add_argument(
        "--maxtoken", type=int, default=300, help="Max tokens to generate"
    )
    parser.add_argument(
        "--reasoning",
        choices=["none", "low", "medium", "high"],
        default=None,
        help="Reasoning effort level (uses /v1/responses endpoint)",
    )
    parser.add_argument(
        "--endpoint",
        choices=["chat", "responses"],
        default=None,
        help="Target endpoint ('chat' for /v1/chat/completions, 'responses' for /v1/responses). Defaults to 'responses' if --reasoning is set, otherwise 'chat'.",
    )
    args = parser.parse_args()

    endpoint = args.endpoint or ("responses" if args.reasoning is not None else "chat")

    if endpoint == "responses":
        url = f"http://127.0.0.1:{args.port}/v1/responses"
        payload = {
            "model": args.model,
            "input": args.message,
            "max_output_tokens": args.maxtoken,
        }
        if args.reasoning is not None:
            payload["reasoning"] = {"effort": args.reasoning}
        data = json.dumps(payload).encode()
    else:
        url = f"http://127.0.0.1:{args.port}/v1/chat/completions"
        payload = {
            "model": args.model,
            "messages": [{"role": "user", "content": args.message}],
            "max_tokens": args.maxtoken,
        }
        data = json.dumps(payload).encode()

    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    start = time.time()
    with urllib.request.urlopen(req) as resp:
        r = json.loads(resp.read())
    elapsed = time.time() - start

    u = r.get("usage", {})
    if endpoint == "responses":
        toks = u.get("output_tokens", 0)
        prompt_toks = u.get("input_tokens", 0)
        reasoning_toks = (
            u.get("output_tokens_details", {}).get("reasoning_tokens", 0)
            if isinstance(u.get("output_tokens_details"), dict)
            else 0
        )
    else:
        toks = u.get("completion_tokens", 0)
        prompt_toks = u.get("prompt_tokens", 0)
        reasoning_toks = (
            u.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            if isinstance(u.get("completion_tokens_details"), dict)
            else 0
        )
    tps = toks / elapsed if elapsed > 0 else 0

    print()
    print(f"| {'Metric':<20} | {'Value':<20} |")
    print(f"|{'-' * 22}|{'-' * 22}|")
    print(f"| {'Model':<20} | {r.get('model', args.model):<20} |")
    print(f"| {'Endpoint':<20} | {url:<20} |")
    if args.reasoning is not None:
        print(f"| {'Reasoning Effort':<20} | {args.reasoning:<20} |")
    if reasoning_toks > 0:
        print(f"| {'Reasoning tokens':<20} | {reasoning_toks:<20} |")
    print(f"| {'Completion tokens':<20} | {toks:<20} |")
    print(f"| {'Wall-clock time':<20} | {f'{elapsed:.2f}s':<20} |")
    print(f"| {'Tokens/sec':<20} | {f'{tps:.1f}':<20} |")
    print(f"| {'Prompt tokens':<20} | {prompt_toks:<20} |")


if __name__ == "__main__":
    main()
