# Part 3: 운영 반영과 정리 — P4-P5

> master: [master.md](master.md)
> 선행 Part: [part2](part2-image-ab.md) | 후속 Part: -
> 담당 Phase: P4-P5 | 변경 파일: 레포 수정 9 + 휠 이동 1 | 상태: 초안 v3.2

## 목표
- 시험장에서 검증한 `aws/`를 운영에 올릴 반영 묶음을 대표님께 넘기고, 운영 빌드 결과가 시험 이미지와 같은 조합인지 대조하게 한다.
- 운영 반영을 확인한 뒤 설정 키와 문서의 버전 표기를 정리한다.

## 전제 조건
- [ ] part2 완료: 판정표 통과, 대표님의 운영 반영 승인. 관문은 안정성(기동·기능·품질 회귀·장시간 안정성·게이트웨이 호환)이다. 성능 칸의 보류·실패는 참고 기록이고 반영을 막지 않는다(master ⑧, 10-09 대표님 결정). 품질 항목의 보류는 관문에 남는다
- [ ] 결정 ③ 운영 반영 순서와 일정, 결정 ⑥ Qwen3.6 사용 여부
- [ ] P0에서 정의한 되돌리기 묶음

## 작업 목록

### P4 운영 반영 (실행은 대표님)
- [ ] 반영 묶음 전달
  - 커밋 해시 (`aws/`, `llm-serving/`)
  - 운영 env 값: `VLLM_IMAGE`(태그+다이제스트, `aws/.env.prd`·`aws/.env`·`on-prem/.env.prd`), `EXTRA_REQUIREMENTS`가 비어 있어야 함
  - 시험 이미지 기록 `aws/image-freeze-0.31.0.txt`
  - 되돌리기 묶음과 절차 (아래 변경 예시)
- [ ] 전달 경로: 대표님 요청 시 `aws/start.sh push` → 대표님이 운영계에서 pull(`aws/start.sh:6-7,81`). `llm-serving/`은 기존 `llm-serving/start.sh push` 경로. 온프레미스는 env와 git pull로 전달한다(휠 scp 단계가 없어짐)
- [ ] 운영 반영 순서 (대표님용). **조합 대조는 서비스 컨테이너를 바꾸기 전의 관문**이다. `user.sh rebuild`는 기존 컨테이너를 먼저 멈추고 지운 뒤 새로 만들기 때문이다(`aws/user.sh:498-499, 516`)
  0. 게이트웨이 먼저: `llm-serving/` 반영으로 새 게이트웨이를 옛 vLLM 위에서 먼저 재기동하고, 옛 vLLM과의 동작(effort × thinking 대상 지정 시험)을 확인한 뒤 다음으로 간다. P3 실측(10-08)에서 옛 게이트웨이 + 0.31 Qwen은 18건 중 4건이 기대와 달리 사고를 켰고(14건 통과, 생략+최상위 effort·생략+템플릿 effort의 스트리밍·비스트리밍), 새 게이트웨이는 옛 vLLM과도 18/18·Gemma 10/10으로 통과했다. 이 순서가 막아 주는 범위는 **게이트웨이를 거치는 요청의 사고 설정 호환**까지다
    - 10-10 대표님 결정으로 게이트웨이 규칙이 바뀌었다: effort를 주면 추론을 켠다(`enable_thinking` 직접 지정이 우선, `none`은 끔). 그래서 운영 반영 때 effort만 보내던 클라이언트는 추론이 켜진다. 이 변화는 의도된 것이며, 위 "옛 vLLM과 같은 동작" 확인은 새 규칙의 기대값(`tests/effort_thinking_matrix.py`)으로 한다
  0-1. 직접 호출 관문(이미지 교체 전): vLLM 포트(:7070 등)에 게이트웨이를 거치지 않고 붙는 클라이언트가 있는지 확인한다. `prd-gemma.yaml`은 `host: 0.0.0.0`이라 :7070이 외부에 열려 있을 수 있다(SESSION P2 항목). 있으면 그 클라이언트가 쓰는 요청 조합을 0.31 의미로 확인하고 대표님과 처리를 정한 뒤 진행한다. 0.31의 직접 호출 변화(P3 실측·소스 `chat_completion/protocol.py:584-585`): 최상위 `reasoning_effort`가 명시되고 null이 아니며, 요청의 `chat_template_kwargs`에 `enable_thinking`이 없을 때 `enable_thinking = (effort != "none")`이 된다(모델 공통). effort를 생략하면 이 처리가 없다. 그래서 Gemma는 `thinking 생략 + effort high`가 꺼짐에서 켜짐으로, Qwen3.8은 같은 조합이 200(꺼짐)에서 400(템플릿이 `high`를 거부)으로 바뀐다
  1. 되돌리기 태그: 운영 컨테이너의 실제 이미지 ID에 보존 태그를 붙인다(아래 변경 예시)
  2. env 준비: `.env`의 `VLLM_IMAGE`를 태그+다이제스트로 바꾸고 `EXTRA_REQUIREMENTS`를 비운다(10-09 원본 `.env.prd`·`.env.dev`에 반영 완료 — `aws/start.sh push` 뒤 서버에서 `cp .env.prd .env`). 이 값은 재생성 때 `.env`에서 읽히고 컨테이너 시작마다 설치되므로(`user.sh:49,371`, `entrypoint-llm.sh:41-47`) 재생성 전에 맞춰야 한다
  3. `docker compose build`. 이때 공통 이름 `llm-prd:latest`가 새 이미지로 옮겨 간다. 이미 떠 있는 컨테이너는 그대로지만, 이후 `user.sh`로 만드는 모든 컨테이너는 새 이미지를 쓴다. 대조를 마칠 때까지 다른 재생성을 하지 않는다
  4. 조합 대조 (GPU 불필요, 임시 컨테이너): `docker run --rm --entrypoint python3 llm-prd:latest /opt/gen-core-constraints.py --final`과 이미지 안 `/opt/image-freeze.txt`를 꺼내 `aws/image-freeze-0.31.0.txt`와 비교한다
     - 10-09: 대표님이 이미지 확인(part2 ④~⑦) 대신 개발 서버 빌드를 먼저 하므로, 그 서버의 `/opt/image-core-final.txt` 출력이 기준이다(`aws/SETUP_GUIDE.md` §4-3)
     - `--final` 항목(핵심·FlashInfer 부속·음성 경로)이 하나라도 다르면 멈춘다. `llm-prd:latest`를 보존 태그로 되돌리고 차이를 알려 준다
     - 그 밖의 패키지 차이는 영향 범위를 판정한다. 게이트웨이·클라이언트·음성 처리에 닿는 패키지(HTTP 클라이언트·서버, 직렬화, 오디오 처리)가 바뀌었으면 시험장에서 관련 시험을 다시 하고 통과한 뒤 진행한다. 닿지 않는 것만 기록으로 넘긴다
     - 하나라도 다르면 "시험 이미지와 같은 이미지"라고 부르지 않는다
  5. 재생성: `./user.sh rebuild <name>`. **이름을 반드시 준다.** 이름이 없으면 `managed-by=user.sh` 컨테이너 전부를 다시 만든다(`user.sh:440-447`)
  6. 재생성 뒤 확인 (아래 체크리스트)
- [ ] 운영 확인 체크리스트 (재생성 뒤, 대표님용)
  - 이미지 확인: `python`·`vllm` 실경로와 버전, `pip check`, 사용자 site와 겹치는 패키지
  - 기동 로그 핵심 줄: Model Runner V2, 양자화 방식, MTP 방식(운영 Gemma는 결정 ⑨로 `speculative_config=None`이어야 한다)
    - 블록 FP8 체크포인트(Qwen 계열 FP8)를 쓰는 인스턴스는 `Selected … for Fp8LinearMethod` 줄로 선형층 커널을 확인한다. L40S(8.9)에서는 0.31이 옛 Triton W8A8 대신 Marlin(가중치만 FP8)을 골랐다. 운영 GPU(RTX PRO 6000 12.0, H200 9.0)의 선택은 확인하지 않았다. 10-09 대표님 결정(master 결정 ⑦)에 따라 어떤 커널이 선택되든 설정으로 바꾸지 않고 기록만 한다. 소스 조건상 두 GPU에서는 CUTLASS 블록(H200은 DeepGEMM 패키지가 있으면 DeepGEMM)이 Marlin보다 앞 순위다
    - Gemma(온라인 `fp8_per_tensor`, 10-09 변경)는 `Fp8PerTensorOnlineLinearMethod`가 나오고 `fp8 deprecated` 경고가 없어야 한다. 경고가 나오면 옛 서빙 코드다
  - 직접 호출 클라이언트 확인은 0-1에서 마쳤어야 한다(재생성 뒤에 처음 확인하지 않는다)
  - 대상 지정 기능 시험 결과, 처음 하루 동안의 엔진 오류 여부
  - 운영 GPU(RTX PRO 6000 TP1, 온프레미스 H200)의 첫 추론과 FlashInfer JIT 동작. L40S 결과로 대신하지 않는다
  - 운영 GPU에서만 볼 수 있는 항목(L40S 시험에서 넘겨받음): Gemma 31B 6만 토큰 근처 입력(L40S는 max_model_len 8192만 기동), 운영 KV dtype `auto` 경로(시험은 fp8), TP 설정(연구계 :5015 TP2). 인스턴스마다 짧은 기동·기능 시험을 하고, 성능은 운영 기준선이 있을 때만 비교한다
- [x] Qwen3.6(`prd-pii-qwen.yaml`, 결정 ⑥): 10-09 대표님 확인 "3.6 안 쓴다, 3.8이다". `prd-pii-qwen.yaml`을 Qwen3.8로 바꿨다(`qwen.yaml`과 같은 설정에 PII용 포트·바인딩·GPU0 TP1). 아래 두 갈래는 이제 해당 없다. 쓰고 있으면 둘 중 하나로 정해 이 인스턴스의 완료 조건으로 둔다
  - 전환 보류: 보류 단위는 **Qwen3.6이 뜬 컨테이너**다. `user.sh rebuild`는 컨테이너를 통째로 바꾸고 런처는 그 컨테이너의 `vllm`을 쓰므로(`aws/user.sh:498-499, 516`, `vllm_server_launcher.py:674`) 한 컨테이너 안에서 모델 하나만 옛 이미지에 남길 수 없다
    - 다른 전환 대상과 분리된 컨테이너면 그 컨테이너를 옛 이미지로 유지한다
    - 같은 컨테이너면 그 컨테이너의 전환을 결정 ⑥ 확정과 필요한 검증까지 미룬다. 독립된 다른 운영 컨테이너의 전환까지 막지는 않는다
    - 별도 컨테이너로 나누는 작업은 이번 범위에 자동으로 넣지 않는다. 운영 컨테이너 구성은 확인하지 않았으므로 P4 전에 대표님께 확인한다
  - 운영자 개별 검증: 새 이미지에서 기동·기능 시험을 하고, 실패하면 되돌리기 묶음으로 복구한다
  - 어느 쪽이든 "6종 시험 완료"를 운영 전체 모델 검증으로 일반화하지 않는다

### P5 설정·문서 정리 (운영 반영 확인 뒤)
- [x] 운영 Gemma 인스턴스 2개의 `speculative_config` 주석 처리 (결정 ⑨, 10-09 커밋). 이 변경은 반영 묶음에 함께 들어간다. 옛 nightly의 추론 켬·축소 조건 시험에서 MTP 끔은 문법·도구 호출 증상이 관측되지 않았다(KV fp8 0/160, 운영과 같은 KV auto 0/320. 같은 KV auto의 MTP 켬은 108/320). 그래서 MTP 끄기를 버전업과 별개로 먼저 반영하는 선택을 지지한다. 이것은 운영 검증 완료를 뜻하지 않는다(옛 KV auto 끔에서도 길이 초과 2건·공백 폭주 후보 1건은 남았다). 순서는 결정 ③에서 대표님이 정하고, 반영 뒤 실제 기동 로그의 `speculative_config=None`과 기능 확인을 거친다(코덱스 R5-08). 31B `-assistant` 드래프트 모델 반입은 더 필요 없다
- [x] 운영 Gemma 인스턴스 2개(`prd-gemma.yaml`, `prd-pii-gemma.yaml`)의 `quantization: fp8`을 `fp8_per_tensor`로 바꾼다. 근거는 P3의 `fp8` ↔ `fp8_per_tensor` 확인이다
  - 10-09 밤 대표님 지시("최신버전에 맞게 다 맞춰줘")로 운영 반영 전에 앞당겼다. 시험장 31B(MTP 끔, `bundle/p5-gemma31b-pt`, 이 한 줄만 다름): 선형 커널·양자화 층 줄(md5 같음)·KV 17,385토큰이 `fp8` 기동과 같고 사용 중단 경고 0줄, 회귀 탐침 24 통과·1 건너뜀(긴 입력, 이전과 같음). 6개 인스턴스 모두 0.31 설정 해석(`check_config_parse.py --engine`) 통과
- [x] ~~연구계 Gemma 인스턴스(`gemma.yaml`, `gemma-26b.yaml`)는 `fp8`을 유지한다.~~ 10-09 밤 뒤집음: 같은 지시로 `fp8_per_tensor`와 MTP 끔을 연구계 Gemma 2개에도 적용했다. 이 파일들은 서버의 `gemma`(:5015) 컨테이너가 0.31 이미지로 띄우므로 0.31 기준이 맞다. 남는 제약: 옛 nightly에서 `fp8`(`quantization/fp8.py`)과 `fp8_per_tensor`(`quantization/online/fp8.py`)는 다른 구현이라, 연구계 컨테이너(옛 nightly)에서 이 두 파일로 Gemma를 띄우는 것은 시험하지 않았다(지금 연구계 :5015는 `qwen.yaml`)
- [ ] 런처의 `async_scheduling` 우회 블록은 **유지**하고 주석만 고친다. 0.31도 밑줄 키의 `false`를 버린다(`utils/argparse_utils.py:615`). 제거 조건은 "실제 `serve` 진입점에서 최종값이 False로 해석될 때"로 적는다
- [ ] 운영 문서
  - `VLLM_OPS_GUIDE.md`: 버전 표기, Gemma 4 파서 파일 경로(`parser/gemma4.py`, `reasoning/gemma4_engine_reasoning_parser.py`), 직접 호출의 effort 의미 변화(0.31은 최상위 effort가 thinking을 켬, 게이트웨이 경유는 그대로), 알려진 이슈 표 재확인
  - `STT_OPS_GUIDE.md`, `stt/tests/test_stt_server.py` 주석: 버전 표기와 리샘플러 변경. STT는 이번 A/B에서 시험하지 않았으므로(10-08 지시) "0.31에서 시험 안 함"으로 적고 시험 완료처럼 쓰지 않는다
  - `vllm/instances/_SCHEMA.txt`: MTP 첫 릴리스(0.21.0) 정정, 소스 줄 번호 인용 갱신 — 10-09 완료(`fp8_per_tensor` 설명, Gemma method 명시 설명, 0.31.0 줄 번호). `VLLM_OPS_GUIDE.md`는 서비스 구성·모델 비교표·MTP·Gemma 파서 설명만 고쳤고, 직접 호출 effort 의미와 알려진 이슈 표는 남았다
- [ ] `aws/wheels/`의 nightly 휠을 `.archive/<날짜>_vllm-nightly-wheel/`로 옮긴다. 되돌리기 묶음은 휠이 아니라 태그해 둔 옛 이미지로 복구하므로 휠은 필요 없다. 문서가 정본으로 적은 `/models/wheels/`는 실제로 없으므로 표기도 정리한다
- [ ] 연구계 옛 환경(`~/.local`의 nightly)은 그대로 둔다. 연구계 전환은 이 계획 범위 밖이며 대표님이 요청할 때 따로 계획한다
- [ ] `agent-guide/SESSION.md` 갱신, `PROJECT.md` 코드 지도에 시험장, 이미지 이름, 이미지 기록 파일 반영

## 변경 예시

**되돌리기 묶음 (대표님용 절차, 운영 경로 = `user.sh`)**
```bash
# 재빌드 전: 운영 컨테이너가 실제로 쓰는 이미지 ID에 보존 태그를 붙이고, ID를 P0 기록 파일에 남긴다
IMG_ID=$(docker inspect -f '{{.Image}}' <운영 컨테이너 이름>)
docker tag "$IMG_ID" llm-prd:pre-0.31-20261008
echo "$IMG_ID" > <P0 기록 폴더>/rollback-image-id.txt

# 되돌릴 때 ① 재생성 전에 이미지 밖 상태부터 복구한다
#   - .env: VLLM_IMAGE, EXTRA_REQUIREMENTS를 P0 기록값으로 (재생성 때 .env에서 읽히고 시작마다 설치됨)
#   - 볼륨: 게이트웨이 수정·P5 설정 커밋 되돌림, 사용자 site 패키지를 P0 기록과 맞춤
# ② 보존 ID는 셸 변수가 아니라 기록 파일에서 읽는다(다른 셸·다른 날 실행될 수 있음).
#    기록 없음·inspect 실패·ID 불일치 중 하나라도 있으면 멈추고, 맞을 때만 이름표 이동과 재생성을 한다
REC_ID=$(cat <P0 기록 폴더>/rollback-image-id.txt) || { echo "보존 ID 기록 없음, 중단"; exit 1; }
CUR_ID=$(docker image inspect -f '{{.Id}}' llm-prd:pre-0.31-20261008) || { echo "보존 태그 없음, 중단"; exit 1; }
if [ -n "$REC_ID" ] && [ "$CUR_ID" = "$REC_ID" ]; then
    docker tag llm-prd:pre-0.31-20261008 llm-prd:latest
    # ③ 대상 이름을 반드시 준다 (이름 없으면 user.sh 컨테이너 전부가 대상)
    #    user.sh는 이미지가 로컬에 있으면 빌드·pull 없이 docker run 한다(aws/user.sh:451, 349-375)
    ./user.sh rebuild <name>
else
    echo "보존 태그 ID($CUR_ID)가 기록($REC_ID)과 다름, 중단"; exit 1
fi
```
- 공통 이름표를 옮기면 이미 떠 있는 다른 컨테이너는 바뀌지 않지만, 이후 `user.sh`로 만드는 모든 컨테이너가 옛 이미지를 쓴다. 되돌리는 동안의 이름표 상태를 기록하고 다른 재생성과 겹치지 않게 한다
- `user.sh rebuild`가 옛 컨테이너에서 이어받는 것은 비밀번호·GPU·UID/GID·모드·포트뿐이다(`user.sh:462-494`). 메모리·공유 메모리·볼륨 경로·`EXTRA_REQUIREMENTS`는 그때의 `.env`를 따른다. 그래서 되돌리기 묶음에 이 값들의 P0 기록을 넣고, 컨테이너 설정이 자동으로 보존된다고 쓰지 않는다
- compose로 만든 컨테이너(시험장 등)는 `user.sh rebuild` 대상이 아니다(`managed-by` 라벨 확인, `user.sh:435`). 그 컨테이너의 env 파일과 프로젝트를 지정하고 이미지를 보존 태그로 직접 고른다
  ```bash
  LLM_IMAGE_NAME=<그 컨테이너의 보존 태그> docker compose --env-file <그 컨테이너의 env> -p <프로젝트> \
      up -d --no-build --pull never --force-recreate llm
  ```
- 재생성 뒤 대상 지정 기능 시험으로 확인한다

**운영 Gemma 인스턴스 2개 (P5)**
```yaml
quantization: fp8_per_tensor     # 온더플라이 FP8 (0.31부터 fp8은 사용 중단 경고 후 이 방식으로 처리)
```

**런처 우회 블록 주석 (P5)**
```python
    # vLLM YAML 파서는 bool false를 --no-<키>로 바꾸지만, 키 이름을 하이픈으로 바꾸기 전에
    # 등록된 옵션을 조회한다(0.31.0 utils/argparse_utils.py:615). 밑줄 키 async_scheduling은
    # --no-async_scheduling으로 조회돼 버려진다. 실제 serve 진입점에서 최종값이 False로
    # 해석되는 버전이 확인되면 이 블록을 제거한다.
```

## 검증
- `grep -n wheels aws/Dockerfile.llm` 결과 없음
- P5 뒤 옛 버전 표기(`0.20.2`, `dev251`) 검색: 조사 문서·버그 기록과 함께, 되돌리기 절차·호환 설명·기준선 기록에 남는 것은 정상이다. 그 밖의 "현재 버전" 설명에서만 사라졌는지 본다
- P5 설정 변경 뒤 시험장 Gemma(운영 설정 사본) 재기동, 대상 지정 기능 시험 통과, 기동 로그에 fp8 사용 중단 경고가 없음
- 운영 확인 체크리스트의 조합 대조 결과가 기록됨

## 완료 기준
- [ ] 반영 묶음 전달, 대표님의 운영 반영 확인 (EC2, 온프레미스는 결정 ③ 일정대로)
- [x] Qwen3.6 처리 결과가 결정 ⑥대로 기록됨
- [ ] P5 정리 커밋, 문서 정합 확인
- [ ] master Phase 맵에서 part3 상태 갱신, 계획서를 `agent-guide/.archive/`로 이동
