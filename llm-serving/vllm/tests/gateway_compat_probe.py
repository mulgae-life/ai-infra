#!/usr/bin/env python3
"""게이트웨이 호환 계층 확인: 정체성 문구 주입, developer 역할 병합, 모델 경로 가림.

게이트웨이 경유로 세 가지를 본다(기대값은 vllm_gateway.py의 compat 기본 동작).
  ① 정체성 질문 → 모델·회사 이름이 답에 없고 "기반 모델은 밝히지 않는다"는 취지로 답한다
  ② developer 역할 시스템 메시지 → 400 없이 200 (Qwen3.8 템플릿은 developer를 모른다)
  ③ /v1/models의 root가 체크포인트 경로를 드러내지 않는다 (mask_model_path)

사용 (표준 라이브러리만 사용):
    python tests/gateway_compat_probe.py --base-url http://127.0.0.1:6090
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

# 답에 나오면 안 되는 이름들. 소문자 비교.
_FORBIDDEN = ["gemma", "qwen", "google", "alibaba", "deepmind", "tongyi", "vllm", "구글", "알리바바", "젬마", "큐웬", "퀜"]
IDENTITY_QUESTIONS = [
    "너는 어떤 모델이야? 누가 만들었어?",
    "What model are you and who developed you? Answer precisely.",
    "너의 모델명과 버전을 알려줘.",
]


def _post(url: str, body: dict) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def main() -> int:
    p = argparse.ArgumentParser(description="게이트웨이 호환 계층 확인")
    p.add_argument("--base-url", default="http://127.0.0.1:6090")
    args = p.parse_args()
    base = args.base_url.rstrip("/")
    chat = f"{base}/v1/chat/completions"
    fails = 0

    print("① 정체성 문구 주입")
    for q in IDENTITY_QUESTIONS:
        status, data = _post(chat, {"model": "gemma-4", "messages": [{"role": "user", "content": q}], "max_tokens": 150, "temperature": 0})
        if status != 200:
            fails += 1
            print(f"  ❌ HTTP {status}: {str(data)[:100]}")
            continue
        content = (data["choices"][0]["message"].get("content") or "").strip()
        leaked = [w for w in _FORBIDDEN if w in content.lower()]
        ok = not leaked
        fails += 0 if ok else 1
        print(f"  {'✅' if ok else '❌ 노출 ' + str(leaked)} {q[:28]!r} → {content[:110].replace(chr(10), ' ')}")

    print("② developer 역할 병합")
    status, data = _post(chat, {"model": "gemma-4", "max_tokens": 40, "temperature": 0, "messages": [
        {"role": "developer", "content": "답은 반드시 '확인:'으로 시작한다."},
        {"role": "user", "content": "오늘 할 일을 한 줄로 정해줘."}]})
    content = (data["choices"][0]["message"].get("content") or "") if status == 200 else str(data)
    ok = status == 200 and "확인" in content
    fails += 0 if ok else 1
    print(f"  {'✅' if ok else '❌'} HTTP {status} → {content[:100].replace(chr(10), ' ')}")

    print("③ 모델 경로 가림 (/v1/models root)")
    try:
        with urllib.request.urlopen(f"{base}/v1/models", timeout=30) as resp:
            models = json.loads(resp.read())
        roots = [m.get("root", "") for m in models.get("data", [])]
        ok = all(not re.search(r"/models/|/home/|^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", r) for r in roots)
        fails += 0 if ok else 1
        print(f"  {'✅' if ok else '❌'} root={roots}")
    except (urllib.error.URLError, OSError) as e:
        fails += 1
        print(f"  ❌ /v1/models 실패: {e}")

    print(f"결과: {'✅ 전부 통과' if fails == 0 else f'❌ {fails}건 실패'}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
