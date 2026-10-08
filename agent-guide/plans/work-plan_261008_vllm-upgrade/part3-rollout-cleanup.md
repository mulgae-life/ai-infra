# Part 3: 운영 반영과 정리 — P4-P5

> master: [master.md](master.md)
> 선행 Part: [part2](part2-image-ab.md) | 후속 Part: -
> 담당 Phase: P4-P5 | 변경 파일: 레포 수정 9 + 휠 이동 1 | 상태: 초안 v3.2

## 목표
- 시험장에서 검증한 `aws/`를 운영에 올릴 반영 묶음을 대표님께 넘기고, 운영 빌드 결과가 시험 이미지와 같은 조합인지 대조하게 한다.
- 운영 반영을 확인한 뒤 설정 키와 문서의 버전 표기를 정리한다.

## 전제 조건
- [ ] part2 완료: 판정표 통과, 대표님의 운영 반영 승인
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
  1. 되돌리기 태그: 운영 컨테이너의 실제 이미지 ID에 보존 태그를 붙인다(아래 변경 예시)
  2. env 준비: `.env`의 `VLLM_IMAGE`를 태그+다이제스트로 바꾸고 `EXTRA_REQUIREMENTS`를 비운다. 이 값은 재생성 때 `.env`에서 읽히고 컨테이너 시작마다 설치되므로(`user.sh:49,371`, `entrypoint-llm.sh:37-40`) 재생성 전에 맞춰야 한다
  3. `docker compose build`. 이때 공통 이름 `llm-prd:latest`가 새 이미지로 옮겨 간다. 이미 떠 있는 컨테이너는 그대로지만, 이후 `user.sh`로 만드는 모든 컨테이너는 새 이미지를 쓴다. 대조를 마칠 때까지 다른 재생성을 하지 않는다
  4. 조합 대조 (GPU 불필요, 임시 컨테이너): `docker run --rm --entrypoint python3 llm-prd:latest /opt/gen-core-constraints.py --final`과 이미지 안 `/opt/image-freeze.txt`를 꺼내 `aws/image-freeze-0.31.0.txt`와 비교한다
     - `--final` 항목(핵심·FlashInfer 부속·음성 경로)이 하나라도 다르면 멈춘다. `llm-prd:latest`를 보존 태그로 되돌리고 차이를 알려 준다
     - 그 밖의 패키지 차이는 영향 범위를 판정한다. 게이트웨이·클라이언트·음성 처리에 닿는 패키지(HTTP 클라이언트·서버, 직렬화, 오디오 처리)가 바뀌었으면 시험장에서 관련 시험을 다시 하고 통과한 뒤 진행한다. 닿지 않는 것만 기록으로 넘긴다
     - 하나라도 다르면 "시험 이미지와 같은 이미지"라고 부르지 않는다
  5. 재생성: `./user.sh rebuild <name>`. **이름을 반드시 준다.** 이름이 없으면 `managed-by=user.sh` 컨테이너 전부를 다시 만든다(`user.sh:440-447`)
  6. 재생성 뒤 확인 (아래 체크리스트)
- [ ] 운영 확인 체크리스트 (재생성 뒤, 대표님용)
  - 이미지 확인: `python`·`vllm` 실경로와 버전, `pip check`, 사용자 site와 겹치는 패키지
  - 기동 로그 핵심 줄: Model Runner V2, 양자화 방식, MTP 방식
  - 대상 지정 기능 시험 결과, 처음 하루 동안의 엔진 오류 여부
  - 운영 GPU(RTX PRO 6000 TP1, 온프레미스 H200)의 첫 추론과 FlashInfer JIT 동작. L40S 결과로 대신하지 않는다
- [ ] Qwen3.6(`prd-pii-qwen.yaml`, 결정 ⑥): 운영에서 쓰지 않으면 체크리스트에서 뺀다. 쓰고 있으면 둘 중 하나로 정해 이 인스턴스의 완료 조건으로 둔다
  - 전환 보류: 보류 단위는 **Qwen3.6이 뜬 컨테이너**다. `user.sh rebuild`는 컨테이너를 통째로 바꾸고 런처는 그 컨테이너의 `vllm`을 쓰므로(`aws/user.sh:498-499, 516`, `vllm_server_launcher.py:674`) 한 컨테이너 안에서 모델 하나만 옛 이미지에 남길 수 없다
    - 다른 전환 대상과 분리된 컨테이너면 그 컨테이너를 옛 이미지로 유지한다
    - 같은 컨테이너면 그 컨테이너의 전환을 결정 ⑥ 확정과 필요한 검증까지 미룬다. 독립된 다른 운영 컨테이너의 전환까지 막지는 않는다
    - 별도 컨테이너로 나누는 작업은 이번 범위에 자동으로 넣지 않는다. 운영 컨테이너 구성은 확인하지 않았으므로 P4 전에 대표님께 확인한다
  - 운영자 개별 검증: 새 이미지에서 기동·기능 시험을 하고, 실패하면 되돌리기 묶음으로 복구한다
  - 어느 쪽이든 "6종 시험 완료"를 운영 전체 모델 검증으로 일반화하지 않는다

### P5 설정·문서 정리 (운영 반영 확인 뒤)
- [ ] 운영 Gemma 인스턴스 2개(`prd-gemma.yaml`, `prd-pii-gemma.yaml`)의 `quantization: fp8`을 `fp8_per_tensor`로 바꾼다. 근거는 P3의 `fp8` ↔ `fp8_per_tensor` 확인이다
- [ ] 연구계 Gemma 인스턴스(`gemma.yaml`, `gemma-26b.yaml`)는 `fp8`을 유지한다. 옛 nightly에서 `fp8`(`quantization/fp8.py`)과 `fp8_per_tensor`(`quantization/online/fp8.py`)는 다른 구현이라 이름이 등록돼 있다는 것만으로 실행 호환이 입증되지 않는다. 연구계 전환 때 같이 바꾼다
- [ ] 런처의 `async_scheduling` 우회 블록은 **유지**하고 주석만 고친다. 0.31도 밑줄 키의 `false`를 버린다(`utils/argparse_utils.py:615`). 제거 조건은 "실제 `serve` 진입점에서 최종값이 False로 해석될 때"로 적는다
- [ ] 운영 문서
  - `VLLM_OPS_GUIDE.md`: 버전 표기, Gemma 4 파서 파일 경로(`parser/gemma4.py`, `reasoning/gemma4_engine_reasoning_parser.py`), 직접 호출의 effort 의미 변화(0.31은 최상위 effort가 thinking을 켬, 게이트웨이 경유는 그대로), 알려진 이슈 표 재확인
  - `STT_OPS_GUIDE.md`, `stt/tests/test_stt_server.py` 주석: 버전 표기와 리샘플러 변경
  - `vllm/instances/_SCHEMA.txt`: MTP 첫 릴리스(0.21.0) 정정, 소스 줄 번호 인용 갱신
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
- [ ] Qwen3.6 처리 결과가 결정 ⑥대로 기록됨
- [ ] P5 정리 커밋, 문서 정합 확인
- [ ] master Phase 맵에서 part3 상태 갱신, 계획서를 `agent-guide/.archive/`로 이동
