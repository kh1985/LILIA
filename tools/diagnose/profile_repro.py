#!/usr/bin/env python3
"""
profile_generator standalone reproducer.

session_004 の character.yaml + answers.md を読み込み、
profile_generator が組み立てる本物のプロンプトを使って
claude / codex を直接呼び出し、所要時間と結果を計測する。

usage:
    cd <LILIA repo root>
    python tools/diagnose/profile_repro.py --session session_004 --engine claude
    python tools/diagnose/profile_repro.py --session session_004 --engine codex

何が見たいか:
- claude / codex のどちらが詰まるか / 詰まらないか
- 詰まる場合、stdout が何バイト出た時点で止まるか
- subprocess の returncode、stderr 内容
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.common.engine_runner import _build_engine_command


def build_engine_command(engine: str) -> list[str]:
    return _build_engine_command(engine, ROOT)


def parse_answers(path: Path) -> dict:
    """簡易パーサ。本物の parse_newgame_answers と同じ形式で返す。"""
    text = path.read_text(encoding="utf-8")
    answers: dict[int, str] = {}
    current_q: int | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        line = line.rstrip()
        if line.startswith("## Q"):
            if current_q is not None:
                answers[current_q] = "\n".join(buffer).strip()
            try:
                current_q = int(line.split("Q", 1)[1].split(".", 1)[0])
            except (ValueError, IndexError):
                current_q = None
            buffer = []
        elif current_q is not None:
            buffer.append(line)
    if current_q is not None:
        answers[current_q] = "\n".join(buffer).strip()
    return answers


def build_profile_prompt(answers: dict, character_yaml: dict) -> str:
    """profile_generator._build_generation_prompt と同等の構造。
    実コードを import するとサブプロセス依存が増えるため最小再現で書く。
    本物の実装が変わったら追従が必要。"""
    import json

    answers_json = json.dumps(answers, ensure_ascii=False, indent=2, default=str)
    character_json = json.dumps(character_yaml, ensure_ascii=False, indent=2, sort_keys=True, default=str)

    return f"""あなたはLILIA用のPersona Profile生成補助です。
Q&A回答と生成済みcharacter YAMLから、first scene前に読む `lilia/main/profile.md` を1つ生成してください。

## Q&A 回答

```json
{answers_json}
```

## character YAML

```json
{character_json}
```

profile.md を Markdown のコードブロック ```markdown ... ``` で囲んで出力してください。
"""


def run_with_streaming(engine: str, prompt: str, timeout: float = 900.0) -> dict:
    """run_engine を最小再現。stdout/stderr を別スレッドで逐次受信。"""
    command = build_engine_command(engine)
    print(f"[start] engine={engine} command={' '.join(command)}", flush=True)
    print(f"[start] prompt size = {len(prompt)} chars / approx {len(prompt) // 3} tokens", flush=True)

    start = time.time()
    proc = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=os.environ.copy(),
        start_new_session=True,
    )

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
    last_stdout_at = [start]
    last_stderr_at = [start]

    def reader(pipe, target, last_at_ref, label):
        try:
            for line in pipe:
                target.append(line)
                last_at_ref[0] = time.time()
                # 進捗を可視化（最初の 200 文字 + 100 文字ごとにマーカー）
                total = sum(len(c) for c in target)
                if total < 200 or total % 500 < 100:
                    print(f"[{label}] +{time.time()-start:5.1f}s total={total}c last={line.rstrip()[:80]}", flush=True)
        except Exception as exc:
            print(f"[{label}] reader exception: {exc}", flush=True)
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    t_out = threading.Thread(target=reader, args=(proc.stdout, stdout_chunks, last_stdout_at, "stdout"), daemon=True)
    t_err = threading.Thread(target=reader, args=(proc.stderr, stderr_chunks, last_stderr_at, "stderr"), daemon=True)
    t_out.start()
    t_err.start()

    try:
        proc.stdin.write(prompt)
        proc.stdin.close()
        print(f"[input] sent {len(prompt)} chars to stdin, closed", flush=True)
    except (BrokenPipeError, OSError) as exc:
        print(f"[input] failed: {exc}", flush=True)

    # 5 秒ごとに「生きてるか」を出す
    poll_interval = 5
    elapsed = 0.0
    try:
        while elapsed < timeout:
            try:
                proc.wait(timeout=poll_interval)
                break
            except subprocess.TimeoutExpired:
                elapsed = time.time() - start
                stdout_total = sum(len(c) for c in stdout_chunks)
                stderr_total = sum(len(c) for c in stderr_chunks)
                since_stdout = time.time() - last_stdout_at[0]
                since_stderr = time.time() - last_stderr_at[0]
                print(
                    f"[wait] +{elapsed:5.1f}s  stdout={stdout_total}c (last {since_stdout:4.1f}s ago)  "
                    f"stderr={stderr_total}c (last {since_stderr:4.1f}s ago)  pid={proc.pid}",
                    flush=True,
                )
        else:
            print(f"[timeout] {timeout}s 超過、プロセスグループを kill", flush=True)
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            time.sleep(2)
            if proc.poll() is None:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            proc.wait()
    except KeyboardInterrupt:
        print("[KeyboardInterrupt] killing process group", flush=True)
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        raise

    elapsed = time.time() - start
    t_out.join(timeout=5)
    t_err.join(timeout=5)

    stdout_text = "".join(stdout_chunks)
    stderr_text = "".join(stderr_chunks)

    return {
        "engine": engine,
        "elapsed": elapsed,
        "returncode": proc.returncode,
        "stdout_chars": len(stdout_text),
        "stderr_chars": len(stderr_text),
        "stdout_head": stdout_text[:500],
        "stdout_tail": stdout_text[-500:] if len(stdout_text) > 500 else "",
        "stderr": stderr_text,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True, help="session name e.g. session_004")
    parser.add_argument("--engine", required=True, choices=["claude", "codex"])
    parser.add_argument("--timeout", type=float, default=900.0)
    args = parser.parse_args()

    session_path = ROOT / "saves" / args.session
    if not session_path.exists():
        print(f"session not found: {session_path}", file=sys.stderr)
        return 1

    character_yaml_path = session_path / "lilia" / "main" / "character.yaml"
    answers_path = session_path / "answers.md"

    if not character_yaml_path.exists():
        print(f"character.yaml not found: {character_yaml_path}", file=sys.stderr)
        return 1
    if not answers_path.exists():
        print(f"answers.md not found: {answers_path}", file=sys.stderr)
        return 1

    with character_yaml_path.open("r", encoding="utf-8") as f:
        character_yaml = yaml.safe_load(f)
    answers = parse_answers(answers_path)

    print(f"[load] character.yaml keys: {list(character_yaml.keys())[:8]}", flush=True)
    print(f"[load] answers Q numbers: {sorted(answers.keys())}", flush=True)

    prompt = build_profile_prompt(answers, character_yaml)
    result = run_with_streaming(args.engine, prompt, timeout=args.timeout)

    print("\n=== RESULT ===", flush=True)
    print(f"engine:       {result['engine']}", flush=True)
    print(f"elapsed:      {result['elapsed']:.1f}s", flush=True)
    print(f"returncode:   {result['returncode']}", flush=True)
    print(f"stdout chars: {result['stdout_chars']}", flush=True)
    print(f"stderr chars: {result['stderr_chars']}", flush=True)
    if result["stdout_head"]:
        print(f"\n--- stdout head ---\n{result['stdout_head']}", flush=True)
    if result["stdout_tail"]:
        print(f"\n--- stdout tail ---\n{result['stdout_tail']}", flush=True)
    if result["stderr"]:
        print(f"\n--- stderr ---\n{result['stderr']}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
