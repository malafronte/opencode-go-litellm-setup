import argparse
import json
import sys
import urllib.error
import urllib.request


def send_request(base_url: str, auth_token: str, payload: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        base_url.rstrip("/") + "/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {auth_token}",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw}") from exc


def extract_text_blocks(response: dict) -> list[str]:
    text_blocks: list[str] = []
    for block in response.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            text_blocks.append(block.get("text", ""))
    return text_blocks


def assert_no_think_leak(response: dict, phase: str) -> None:
    leaked_blocks = [
        text
        for text in extract_text_blocks(response)
        if "<think>" in text or "</think>" in text
    ]
    if leaked_blocks:
        raise RuntimeError(
            f"{phase}: found think-tag leakage in text blocks: {json.dumps(leaked_blocks, ensure_ascii=False)}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Assert that minimax-m2.5 does not leak </think> markers in Anthropic tool-loop responses."
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:4000")
    parser.add_argument("--auth-token", default="local-litellm-key")
    parser.add_argument("--model", default="minimax-m2.5")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--final-expected", default="tool-loop-ok")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tools = [
        {
            "name": "echo_status",
            "description": "Return a fixed status payload for proxy tool-loop testing.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                },
                "required": ["status"],
            },
        }
    ]
    first_user_text = (
        "Call the tool echo_status with status=ok. "
        f"After you receive the tool result, answer with exactly: {args.final_expected}"
    )
    first_payload = {
        "model": args.model,
        "max_tokens": 768,
        "tools": tools,
        "messages": [{"role": "user", "content": first_user_text}],
    }
    first_response = send_request(
        args.base_url, args.auth_token, first_payload, args.timeout
    )
    assert_no_think_leak(first_response, "first_response")

    tool_use = None
    for block in first_response.get("content", []):
        if isinstance(block, dict) and block.get("type") == "tool_use":
            tool_use = block
            break

    if tool_use is None:
        raise RuntimeError(
            f"first_response: tool_use block not found: {json.dumps(first_response, ensure_ascii=False)}"
        )

    second_payload = {
        "model": args.model,
        "max_tokens": 256,
        "tools": tools,
        "messages": [
            {"role": "user", "content": first_user_text},
            {"role": "assistant", "content": first_response.get("content", [])},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.get("id", ""),
                        "content": json.dumps({"status": "ok"}),
                    }
                ],
            },
        ],
    }
    second_response = send_request(
        args.base_url, args.auth_token, second_payload, args.timeout
    )
    assert_no_think_leak(second_response, "second_response")

    text_blocks = extract_text_blocks(second_response)
    final_text = "\n".join(text for text in text_blocks if text).strip()
    if final_text != args.final_expected:
        raise RuntimeError(
            f"second_response: unexpected final text {final_text!r}; full response={json.dumps(second_response, ensure_ascii=False)}"
        )

    print("[PASS] minimax-m2.5 think leak regression")
    return 0


if __name__ == "__main__":
    sys.exit(main())
