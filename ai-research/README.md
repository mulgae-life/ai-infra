# AI 연구·실험

모델 학습과 실험을 실제로 돌리는 작업 공간이다. 조사·설계 문서는 `agent-guide/docs/`의 `*_research/`에 두고, 여기에는 그 설계를 실행하는 코드·설정·데이터·실행 결과를 둔다.

S3 배포 스크립트(`aws/start.sh`, `llm-serving/start.sh`)는 자기 디렉토리만 올리므로 이 디렉토리는 운영계 S3 배포에 들어가지 않는다. 다만 git에 올린 파일은 GitHub와 온프레미스 서버(`on-prem/start.sh pull`이 `git pull`)까지 간다.

## 프로젝트

| 경로 | 내용 | 설계 문서 |
|------|------|-----------|
| [insurance-embedding/](insurance-embedding/README.md) | 보험 약관·용어 검색용 임베딩 파인튜닝 | [insurance-finetuning.md](../agent-guide/docs/embedding_research/topics/insurance-finetuning.md) |

## git에 올리는 것과 올리지 않는 것

모든 프로젝트가 같은 구조를 따른다. 제외 규칙은 이 디렉토리의 `.gitignore`가 프로젝트 바로 아래 세 디렉토리에만 건다.

| 구분 | 프로젝트 안 위치 | 담는 것 | 이유 |
|------|------------------|----------|------|
| 올림 | `README.md`, `start.sh`, `configs/`, `pipeline/`, `tests/`, `results/` | 코드, 설정, 테스트, 집계 수치 | 변경 이력을 남기고 리뷰한다 |
| 제외 | `data/` | 원본, 파생 데이터, 사람 판정 | 권리 제한 자료와 사내 문서가 섞인다 |
| 제외 | `runs/` | 실행별 체크포인트·로그·지표 | 용량이 크고 실행마다 쌓인다 |
| 제외 | `models/` | 기반 모델 사본, 승격한 결과 모델 | 용량이 크다 |

- git에 올리는 파일에는 원본 문서·질의의 본문을 넣지 않는다. 테스트 예제와 지시문 예시는 직접 쓴 문장만 쓰고, `results/`에는 숫자만 남긴다.
- 루트 `.gitignore`가 `logs/`, `samples/`, `.env`를 레포 전체에서 제외하므로, git에 올릴 디렉토리에는 이 이름을 쓰지 않는다.
- 사람 판정처럼 다시 만들 수 없는 데이터도 `data/` 안이라 git 밖이다. 프로젝트마다 백업 위치를 따로 정한다.

## 새 프로젝트를 넣을 때

- `ai-research/<프로젝트>/`를 만들고 위 구분을 따른다. 프로젝트 README에 단계별 디렉토리와 읽고 쓰는 위치를 적는다.
- 이 표에 한 줄을 추가한다.
