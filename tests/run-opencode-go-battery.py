import argparse
import json
import sys
import urllib.error
import urllib.request


def build_uri(base_url: str, beta: bool) -> str:
    base = base_url.rstrip("/")
    uri = f"{base}/v1/messages"
    if beta:
        uri += "?beta=true"
    return uri


def send_request(uri: str, auth_token: str, payload: dict, timeout: int) -> dict:
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    request = urllib.request.Request(uri, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw}") from exc


def check_health(base_url: str, timeout: int) -> None:
    request = urllib.request.Request(base_url.rstrip("/") + "/", method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=timeout):
            return
    except urllib.error.HTTPError as exc:
        if exc.code >= 500:
            raise RuntimeError(f"HEAD / failed with status {exc.code}") from exc
    except Exception as exc:
        raise RuntimeError(f"HEAD / failed: {exc}") from exc


def extract_text(content: list) -> str:
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(part for part in parts if part).strip()


def find_tool_use(content: list) -> dict | None:
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            return block
    return None


def is_minimax_m25_truncated_tool_call(response: dict) -> bool:
    if response.get("model") != "minimax-m2.5":
        return False
    if response.get("stop_reason") != "max_tokens":
        return False

    for block in response.get("content", []):
        if (
            isinstance(block, dict)
            and block.get("type") == "text"
            and "<minimax:tool_call>" in block.get("text", "")
        ):
            return True

    return False


def matches_expected_final_text(model: str, text: str, expected: str) -> bool:
    stripped = text.strip()
    if stripped == expected:
        return True

    # minimax-m2.5 currently leaks reasoning as plain text before the final answer.
    if model != "minimax-m2.5":
        return False
    if "</think>" not in stripped or not stripped.endswith(expected):
        return False

    last_non_empty_line = ""
    for line in reversed(stripped.splitlines()):
        if line.strip():
            last_non_empty_line = line.strip()
            break

    return last_non_empty_line == expected


def run_smoke(
    uri: str, auth_token: str, model: str, timeout: int, expected: str
) -> str:
    last_text = ""
    payload = {
        "model": model,
        "max_tokens": 64,
        "messages": [{"role": "user", "content": f"Reply with exactly: {expected}"}],
    }
    for _ in range(2):
        response = send_request(uri, auth_token, payload, timeout)
        text = extract_text(response.get("content", []))
        if text.strip() == expected:
            return text
        last_text = text
    raise RuntimeError(f"unexpected text: {last_text!r}")


def run_tool_loop(
    uri: str,
    auth_token: str,
    model: str,
    timeout: int,
    final_expected: str,
) -> str:
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
        f"After you receive the tool result, answer with exactly: {final_expected}"
    )
    first_payload = {
        "model": model,
        "max_tokens": 256,
        "tools": tools,
        "messages": [{"role": "user", "content": first_user_text}],
    }
    first_response = send_request(uri, auth_token, first_payload, timeout)
    assistant_content = first_response.get("content", [])
    tool_use = find_tool_use(assistant_content)

    # minimax-m2.5 can expose a real tool_use block only after a larger first-turn budget.
    if tool_use is None and is_minimax_m25_truncated_tool_call(first_response):
        first_payload["max_tokens"] = 768
        first_response = send_request(uri, auth_token, first_payload, timeout)
        assistant_content = first_response.get("content", [])
        tool_use = find_tool_use(assistant_content)

    if tool_use is None:
        raise RuntimeError(
            f"tool_use block not found in first response: {json.dumps(first_response)}"
        )

    second_payload = {
        "model": model,
        "max_tokens": 256,
        "tools": tools,
        "messages": [
            {"role": "user", "content": first_user_text},
            {"role": "assistant", "content": assistant_content},
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
    second_response = send_request(uri, auth_token, second_payload, timeout)
    text = extract_text(second_response.get("content", []))
    if not matches_expected_final_text(model, text, final_expected):
        raise RuntimeError(f"unexpected final text: {text!r}")
    return text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a direct test battery against a local LiteLLM proxy in front of OpenCode Go."
    )
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        help="One or more model aliases exposed by the local LiteLLM config.",
    )
    parser.add_argument(
        "--mode",
        choices=["smoke", "tool-loop", "all"],
        default="all",
        help="Which subset of tests to run.",
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:4000")
    parser.add_argument("--auth-token", default="local-litellm-key")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--smoke-expected", default="ok")
    parser.add_argument("--tool-final-expected", default="tool-loop-ok")
    parser.add_argument("--beta", action="store_true")
    parser.add_argument("--skip-health", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    uri = build_uri(args.base_url, args.beta)

    if not args.skip_health:
        check_health(args.base_url, args.timeout)
        print(f"[PASS] health {args.base_url}")

    results = []

    for model in args.models:
        if args.mode in ("smoke", "all"):
            try:
                text = run_smoke(
                    uri, args.auth_token, model, args.timeout, args.smoke_expected
                )
                results.append(("smoke", model, True, text))
                print(f"[PASS] smoke {model} -> {text}")
            except Exception as exc:
                results.append(("smoke", model, False, str(exc)))
                print(f"[FAIL] smoke {model} -> {exc}")

        if args.mode in ("tool-loop", "all"):
            try:
                text = run_tool_loop(
                    uri,
                    args.auth_token,
                    model,
                    args.timeout,
                    args.tool_final_expected,
                )
                results.append(("tool-loop", model, True, text))
                print(f"[PASS] tool-loop {model} -> {text}")
            except Exception as exc:
                results.append(("tool-loop", model, False, str(exc)))
                print(f"[FAIL] tool-loop {model} -> {exc}")

    failures = [item for item in results if not item[2]]
    print(f"Summary: {len(results) - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
