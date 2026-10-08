# 보험 임베딩 파인튜닝

보험 질의에 맞는 근거 조항을 찾도록 임베딩 모델을 파인튜닝하는 실행 공간이다. 설계와 근거는 [insurance-finetuning.md](../../agent-guide/docs/embedding_research/topics/insurance-finetuning.md)에 있고, 작업은 그 문서 7.1절의 착수 순서를 따른다. 2026-10-08 현재 디렉토리 골격만 있고 코드는 없다.

## 구조

첫 단은 역할(코드·설정·데이터·실행 결과·가중치)로, 그 아래는 파이프라인 단계로 나눈다. `[git]`은 올리는 것, `[제외]`는 `../.gitignore`가 제외하는 것이다.

```
insurance-embedding/
├── README.md                   [git]
├── start.sh                    [git]  (예정) 단일 진입점: ./start.sh <단계> [옵션]
├── configs/                    [git]  값만 둔다. 코드 없음
│   ├── sources.yaml                   원천 목록. 권리 등급, 허용 행위(학습·검수·평가), 근거, 확인일
│   ├── parse/ chunk/ synth/ mine/     단계별 설정. 합성 지시문은 synth/prompts/
│   └── experiments/                   E0_baseline.yaml, E1_cmnrl_lr1e-5.yaml …
├── pipeline/                   [git]  단계 하나에 디렉토리 하나 (아래 "단계" 표)
├── tests/                      [git]  지표·파싱 단위 테스트
├── results/                    [git]  실행별 집계 수치 누적
├── data/                       [제외]
│   ├── raw/<source_id>/               받은 그대로 + manifest.jsonl(파일별 권리·메타데이터). 수정 금지
│   ├── derived/<종류>/vNNN/           parsed·chunks·synth·trainsets. 코드가 만든 것. 덮어쓰기 금지
│   ├── labels/                        사람이 만든 것: eval-dev, eval-test(봉인), qc-parse, qc-synth, false-neg
│   └── cache/                         말뭉치 임베딩처럼 언제든 다시 만들 수 있는 것
├── runs/<실험ID>/<실행시각>/   [제외] 설정 사본, 코드 커밋, 로그, 지표, 체크포인트
└── models/<조직>/<모델>/       [제외] 기반 모델 사본과 승격한 결과 모델
```

## 단계

표의 `raw/`·`derived/`·`labels/`·`cache/`는 모두 `data/` 아래다.

| `pipeline/` | 하는 일 | 읽는 곳 | 쓰는 곳 |
|-------------|---------|---------|---------|
| `common/` | 경로, 버전 기록, 행 스키마(pydantic), 권리 게이트 | — | — |
| `collect/` | 원본 수집과 파일별 메타데이터(설계 문서 3.2절 필드) | 외부, `configs/sources.yaml` | `raw/` |
| `parse/` | PDF를 조·항·호·표로 복원하고 페이지와 연결한다. 사내 문서는 여기서 개인정보를 가린다 | `raw/` | `derived/parsed/` |
| `chunk/` | 서빙과 같은 단위로 자르고 맥락 헤더를 붙인다 | `derived/parsed/` | `derived/chunks/` |
| `evalset/` | 분할, 판정 풀, 판정지 내보내기·받기 | `derived/chunks/` | `labels/eval-dev/`, `labels/eval-test/`, `labels/qc-parse/` |
| `synth/` | 합성 질의 생성(:5015), 검수 표본 추출 | `derived/chunks/` | `derived/synth/`, `labels/qc-synth/` |
| `mine/` | 하드 네거티브 채굴, 거짓 네거티브 판정지, 학습셋 조립 | `derived/synth/`, `derived/chunks/`, `models/` | `derived/trainsets/`, `labels/false-neg/` |
| `train/` | 학습 | `derived/trainsets/`, `models/` | `runs/` |
| `merge/` | LM-Cocktail 병합, 체크포인트 병합 | `runs/`, `models/` | `runs/` |
| `evaluate/` | 등급 nDCG, 근거 묶음 완전 회수율, 답 없음 지표, 군집 부트스트랩 | `derived/chunks/`, `labels/eval-*`, 모델 | `runs/`, `results/`, `cache/` |
| `serve_check/` | 학습 프레임워크 출력과 vLLM 출력 비교 | 모델 | `runs/` |

설계 문서 7.1절과는 이렇게 맞물린다. 1단계(자료 확정)는 `configs/sources.yaml`과 `collect/`, 2단계(파싱·주석 규칙)는 `parse/`·`chunk/`·`evalset/`, 3단계(E0 기준선)는 `evaluate/`, 4단계(1만 쌍 준비)는 `synth/`·`mine/`, 5단계(E1 학습)는 `train/`과 `evaluate/`가 맡는다. 단계 번호를 디렉토리 이름에 넣지 않은 것은 파이썬 패키지 이름이 숫자로 시작할 수 없어서다.

## 어디에 둘지

| 질문 | 위치 |
|------|------|
| 외부에서 받은 원본인가 | `data/raw/` |
| 사람이 만들었나 (판정·검수·정답표) | `data/labels/` |
| 코드와 설정으로 다시 만들 수 있나 | 다시 만들기 비싸면 `data/derived/`, 언제든 다시 만들 수 있으면 `data/cache/` |
| 학습·평가 실행이 만들었나 | `runs/`. 남길 숫자만 `results/`로 옮긴다 |
| 하이퍼파라미터·지시문·원천 목록 같은 값인가 | `configs/` |
| 서빙 설정인가 | 이 디렉토리 밖, `llm-serving/` |
| 결과 해석이나 결정 문서인가 | `agent-guide/docs/embedding_research/` |

## 규칙

- **버전:** `data/derived/<종류>/vNNN/`마다 `manifest.json`을 둔다. 입력 버전, 설정 경로와 해시, 코드 커밋, 행 수, 적용한 권리 필터를 적는다. 이 기록으로 학습셋의 한 행에서 원본 파일과 권리 근거까지 거슬러 올라간다. 기존 버전을 덮어쓰지 않고 새 번호를 쓰며, 정답표를 고칠 때도 버전을 올린다.
- **권리:** 등급은 파일 위치가 아니라 `configs/sources.yaml`과 `data/raw/<source_id>/manifest.jsonl`로 관리한다. 등급이 바뀔 때 파일을 옮기면 경로·해시 연결이 끊기고, 한 파일에 학습·검수·평가 허용이 따로 붙어 폴더 하나로 표현할 수 없기 때문이다. 각 단계는 `pipeline/common/`의 권리 게이트를 거쳐 그 용도로 허용된 파일만 읽는다.
- **시험셋:** `data/labels/eval-test/`는 최종 평가 명령만 읽는다. `--final` 없이 열면 실패하고, 열 때마다 기록을 남긴다.
- **git에 올리는 파일:** 원본 문서·질의의 본문을 넣지 않는다. 테스트 예제와 지시문 예시는 직접 쓴 문장만 쓰고, `results/`에는 숫자만 남긴다.
- **체크포인트:** `/workspace`와 `/models`는 같은 디스크다. 568M 모델은 옵티마이저 상태까지 저장하면 체크포인트 하나가 산술로 약 7GB라서 `save_total_limit`로 실행당 개수를 제한한다.
- **백업:** `data/labels/`는 다시 만들 수 없는데 git 밖이다. 사람 판정을 시작하기 전에 백업 위치를 정한다.
