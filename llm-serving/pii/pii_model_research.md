# 한국어 PII NER 모델 — 선택 근거·실측 평가·라이선스 규명

> 조사일: 2026-06-05
> 대상: PII 가드 프록시의 비정형 PII(이름/주소/조직 등) 탐지 모델 선택
> 현재 운영 구성: `vmaca123/korean-pii-ner-v3` + `townboy/kpfbert-kdpii` (GPU3, 각 서버 격리)
> 검증 방식: HuggingFace 모델카드·논문 **1차 본문** + 자체 **실측 평가**(`/models/PII` 직접 로드)

---

## 📌 TL;DR (3줄 요약)

1. **"최근 SLM이 NER보다 PII를 잘한다"는 사실이 아니다.** 인코더 NER이 PII 추출에서 우위(F1 96 vs 79)이고, 생성형은 recall 붕괴·offset 부재·환각으로 **마스킹 파이프라인에 구조적으로 부적합**하다.
2. **자체 실측 결과 현재 `townboy`가 최고 성능**(precision 90.5% / recall 95.0%). 1순위 대안이던 `FrameByFrame`은 P75/R75 + **org 0%·person 71%**(이름 유출 위험)로 교체 시 **보안 후퇴**.
3. **`townboy` 라이선스 리스크는 해소됨.** base KPF-BERT(MIT) + 데이터 KDPII(CC-BY-4.0)로 상업 사용 가능. **현 구성 유지가 정답**이며, 출처표기 의무는 [`NOTICE.md`](NOTICE.md)로 이행.

---

## 1. PII 검출 아키텍처 — regex + NER 하이브리드

PII 가드는 두 축으로 PII를 잡는다. 이건 의도적 설계이며 2026 best practice와 일치한다.

| 방식 | 담당 | 잡는 것 | 원리 |
|------|------|---------|------|
| **구조화(structured)** | `detectors/structured.py` | 주민·카드·전화·계좌·사업자·이메일 | 정규식 + 체크섬 (결정적) |
| **비정형(NER)** | `ner_server.py` (GPU3) | 이름·주소·조직 등 | AI 모델 (문맥 판단) |

> **왜 정형 식별번호는 regex인가** — ① 주민/카드는 형식+체크섬이 100% 결정적이라 AI보다 정밀, ② NER(GPU) 장애 시에도 항상 동작하는 최후 방어선, ③ 차단(422)은 결정적 근거가 필요, ④ `4111.1111...` 점 구분자 우회를 regex가 차단. 상세는 `structured.py` docstring.

본 리포트는 **비정형(NER) 모델 선택**만 다룬다.

---

## 2. SLM vs 전용 NER — "SLM이 더 낫다"는 근거 없음

생성형 SLM이 한국어 PII에서 NER을 능가하는지 2025~2026 근거를 1차 본문으로 검증했다.

### 2.1 정량 근거

| 출처 | 핵심 수치 | 함의 |
|------|----------|------|
| HF blog, *Tiny Encoder Models Beat LLMs at PII* | 인코더 **F1 96.3%** vs GPT-4o-mini **78.7%** (recall **67%**) | 생성형은 PII를 1/3 누락 → **유출 위험** |
| RECAP (arXiv 2510.07551) | 우승은 단독 LLM이 아니라 **regex+LLM 하이브리드** (wF1 0.657) | 우리 하이브리드 구조와 동일 철학 |
| CAPID (EACL 2026) | SLM이 이긴 상대는 *zero-shot LLM*이지 **인코더 NER이 아님** | "SLM 우위"는 비교 대상 착시 |
| GLiNER Guard (arXiv 2605.05277) | 인코더 **193 req/s, P99<1s** | 생성형은 디코딩 지연·비용 큼 |

> ⚠️ "LLM이 PII에서 NER을 이긴다"는 다수 주장은 **벤더 마케팅**(Protecto 등)으로, 본문 확인 결과 정량 근거 없음.

### 2.2 결정적 이유 — offset

PII 가드는 **정확한 문자 offset(start/end)으로 마스킹**한다(`ner_server.py`의 span, `hooks.py`의 치환). 생성형 SLM은 텍스트를 "다시 써서" 반환하므로 offset을 얻으려면 원문 재정렬이 필요하고, 그 과정에서 **환각·누락·오정렬**이 발생한다. CAPID조차 span 매칭을 character-level alignment로 별도 처리해야 했다.

### 2.3 한국어 생성형 PII 현황

한국어 **전용 생성형** PII 모델은 `flowos/teeem-pii-ko-1.2b`(EXAONE) **하나뿐, 다운로드 7회 = 미검증**. 그마저도 구조형은 regex로 처리하는 **하이브리드**다. Qwen 기반 모델조차 생성형이 아니라 **token-classification 헤드**로 쓴다.

**→ 판정: SLM 전환 비권장. NER 유지가 2026 best practice.**

---

## 3. NER 모델 후보 비교 (모델카드 1차 확인)

| 모델 | base | 다운로드/월 | likes | 라이선스 | 라벨 | 비고 |
|------|------|:----------:|:-----:|----------|:----:|------|
| **vmaca123/korean-pii-ner-v3** (현재) | klue/roberta-large | 255 | 0 | CC-BY-SA-4.0 | 7 | NAME/ADDRESS/ORG 정밀 |
| **townboy/kpfbert-kdpii** (현재) | KPF-BERT-ner | 1,537 | 0 | 미선언→해소(§5) | 33 | 대화체 광범위 안전망 |
| FrameByFrame/privacy-filter-korean | OpenAI Privacy Filter MoE 1.5B | **127,021** | 1 | Apache-2.0 | 9 | 최고 인기. **ORG 없음** |
| ehd0309/ko-pii-public-v1 | 동 MoE 1.5B | 437 | 4 | CC-BY-SA-4.0 | 23 | 공공/금융/의료 광범위 |
| vitus9988/klue-roberta-small-ner-identified | klue/roberta-small | 12,541 | 3 | 미확인 | 10 | 순수 인코더 경량 |
| OpenMed-PII-Korean-*-395M | ModernBERT-large | 22 | 0 | Apache-2.0 | 54 | 의료 도메인 전용 |

> 인기 1위 FrameByFrame이 base가 인코더가 아닌 **MoE 1.5B**라, "최근 SLM 계열이 낫나"를 실측으로 검증할 가치가 생겼다 → §4.

---

## 4. 실측 평가 — vmaca / townboy / frameby

3개 모델을 각자 **올바른 디코딩**(vmaca·townboy=BIO, frameby=BIOES)으로 직접 로드해 동일 케이스셋(`tests/eval_pii.py` CASES)에 돌렸다. 구조화 타입(rrn/card 등)은 regex 담당이라 제외.

### 4.1 타입별 recall (잡아야 할 걸 얼마나 잡나)

| 타입 | vmaca123 | **townboy** | frameby |
|------|:--------:|:-----------:|:-------:|
| person(이름) | 85.7% | **85.7%** | ⚠️ **71.4%** |
| address(주소) | 100% | 100% | 100% |
| **org(조직)** | 100% | **100%** | ❌ **0%** |
| phone | 미커버 | 100% | 100% |
| email | 미커버 | 100% | 100% |
| account | 미커버 | 100% | 100% |
| birth | 미커버 | 100% | 100% |

### 4.2 종합 (micro precision / recall)

| 모델 | precision | recall | 과탐 |
|------|:---------:|:------:|:----:|
| vmaca123 | 85.7% | 60.0%* | 1 |
| **townboy (현재)** | **90.5%** | **95.0%** | 2 |
| frameby | 75.0% | 75.0% | 3 |

> *vmaca recall이 낮은 건 person/address/org만 커버하는 설계 때문(phone 등은 townboy 담당). 정상.
> 위는 hooks 후처리(지명/일반어 필터) 전 **raw 모델 출력** 비교라 실제 운영 과탐은 더 낮다. 순위 비교엔 영향 없음.

### 4.3 핵심 발견

- **순수 성능은 townboy가 명확히 우위** (P90.5/R95 vs frameby P75/R75)
- **frameby의 실증된 약점** — 둘 다 PII 유출 직결:
  - ❌ **org 0%**: 조직명을 못 잡음(라벨 없음). 교체 시 vmaca에 100% 의존
  - ⚠️ **person 71.4%**: 이름 누락(모델카드 F1 0.69와 정확히 일치)
  - 과탐 3건("대한민국"을 person 오탐 등)

---

## 5. 호환성 — FrameByFrame은 표준 서빙 불가 (BIOES)

`ner_server.py`는 `pipeline("ner", aggregation_strategy="simple")`(BIO 가정)을 쓴다. FrameByFrame은 **BIOES 태깅**(B-/I-/E-/S-)이라 표준 pipeline이 PII **끝글자를 떼어내 별도 엔티티로 분절**한다 — 마스킹 시 끝글자 누출 버그.

| 입력 | pipeline simple (현재 방식) | BIOES 커스텀 디코더 |
|------|------------------------------|---------------------|
| 홍길동 | `홍길` + `동` ❌ | `홍길동` ✅ |
| 010-1234-5678 | `...567` + `8` ❌ | 통짜 ✅ |
| hong@example.com | `...@example` + `.com` ❌ | 통짜 ✅ |

> 채택 시 `ner_server.py`에 BIOES 디코딩 경로 추가가 전제. (transformers 5.8.0은 `openai_privacy_filter` 아키텍처를 네이티브 지원하므로 로드 자체는 가능.)

---

## 6. 라이선스 규명 — `townboy` 3단계 체인

모델 자체에 라이선스 표기가 없어, base·데이터까지 1차 출처로 추적.

| 단계 | 대상 | 라이선스 | 상업 사용 | 출처 |
|------|------|----------|:---------:|------|
| base | KPF-BERT / KPF-BERT-NER | **MIT** (© 2021 KPFBERT, "sell" 허용) | ✅ | [LICENSE 원문](https://github.com/KPFBERT/kpfbert) |
| 데이터 | KDPII (연세대 김한샘 연구실+TSCIENTIFIC, IEEE Access 2024) | **CC-BY-4.0** | ✅ | [Zenodo](https://zenodo.org/records/10968609) |
| 모델 | townboy/kpfbert-kdpii | 미선언(금지 아님) | ⚠️ 형식적 불확실 | [모델카드](https://huggingface.co/townboy/kpfbert-kdpii) |

**종합: 사내 상업 서비스 사용 가능, 차단 단계 없음.** 핵심 리스크였던 학습 데이터가 CC-BY-4.0으로 확정("연대1"=연세대 자체 데이터, AI Hub 약관 무관). 출처표기 의무는 [`NOTICE.md`](NOTICE.md)로 이행.

> 보수적 확정이 필요하면: 업로더에게 라이선스 확인 요청, 또는 동일 데이터(CC-BY-4.0)·동일 base(MIT)로 **사내 재학습**하여 권리관계 자체 확정.

---

## 7. 최종 결론·권고

| 질문 | 결론 |
|------|------|
| SLM으로 전환? | ❌ **비권장** — NER이 PII 추출 우위, 생성형은 offset/recall/환각 부적합 |
| 더 나은 NER 대안? | ❌ **현 구성이 최고** — frameby 교체는 org·person 약점으로 보안 후퇴 |
| townboy 라이선스? | ✅ **사용 가능** — MIT base + CC-BY-4.0 데이터, 출처표기로 해소 |
| **최종** | **현 구성(vmaca + townboy) 유지. 변경 불필요.** |

### 후속 과제 (선택)

- **org 커버 + 라이선스 명확한 대안**이 필요해지면 `ehd0309/ko-pii-public-v1`(23라벨, CC-BY-SA, org 포함 여부 확인 필요) 추가 평가.
- **person recall 향상**이 목표면 동일 KDPII(CC-BY-4.0)·KPF-BERT(MIT)로 **사내 재학습** → 라이선스 자체 확정 + 도메인 튜닝 동시 달성.
- 평가 자산: `tests/eval_pii.py`(케이스셋), `/models/PII/framebyframe/`(frameby 가중치 보존).

---

## 부록 — 출처

- HF blog: https://huggingface.co/blog/kalyan-ks/tiny-pii-entity-detection-models
- RECAP: https://arxiv.org/pdf/2510.07551 · CAPID: https://aclanthology.org/2026.eacl-srw.23.pdf · GLiNER Guard: https://arxiv.org/abs/2605.05277
- 모델: [vmaca123](https://huggingface.co/vmaca123/korean-pii-ner-v3) · [townboy](https://huggingface.co/townboy/kpfbert-kdpii) · [FrameByFrame](https://huggingface.co/FrameByFrame/privacy-filter-korean) · [ehd0309](https://huggingface.co/ehd0309/ko-pii-public-v1)
- KDPII 데이터: https://zenodo.org/records/10968609 · KPF-BERT: https://github.com/KPFBERT/kpfbert
