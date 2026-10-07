# 보험 도메인 임베딩 파인튜닝 조사 원본 자료 (2026-10-07)

[`insurance-finetuning.md`](../../topics/insurance-finetuning.md)의 근거 자료다. 문서의 수치와 이용 조건은 2026-10-07에 여기 있는 사본과 대조했다. 웹 문서와 데이터 카드는 계속 바뀌므로 인용 시점을 고정하려고 남긴다.

Claude와 코덱스가 나눠 받았다. HTML은 텍스트로 추출했고, 손해보험협회 페이지는 직접 접속이 403이라 검색 서비스(Exa)가 추출한 본문을 저장했다. 받은 원본 HTML·PDF와 수집 기록은 git에 올리지 않는 레포 보존 폴더(`.archive/2026-10-07_insurance-ft-collab/`)에 있다.

KURE-v1, Snowflake-ko, PIXIE-Rune-v1.5, Comsat, Qwen3-Embedding-0.6B 모델 카드는 [한국어 검색 조사 자료](../2026-10-07_korean-retrieval/README.md)의 사본과 같은 파일이라 그쪽을 쓴다.

| 문서 출처 | 파일 |
|-----------|------|
| S25 | `../2026-10-07_korean-retrieval/model-cards/Qwen_Qwen3-Embedding-0.6B.md` |
| S32 | `../2026-10-07_korean-retrieval/model-cards/nlpai-lab_KURE-v1.md` |
| S33 | `../2026-10-07_korean-retrieval/model-cards/dragonkue_snowflake-arctic-embed-l-v2.0-ko.md` |
| S34 | `../2026-10-07_korean-retrieval/model-cards/telepix_PIXIE-Rune-v1.5.md` |
| S35 | `../2026-10-07_korean-retrieval/model-cards/sionic-ai_comsat-embed-ko-8b-preview.md` |

## 디렉터리

| 경로 | 내용 |
|------|------|
| `papers/` | 논문 본문 (arXiv HTML 또는 ACL Anthology PDF의 텍스트 추출본) |
| `official/` | 라이브러리 공식 문서, 기업 기술 블로그, 데이터 제공 기관의 안내·이용 정책 |
| `repos/` | GitHub 저장소 README·문서 사본 |
| `datasets/` | 데이터셋 카드와 AI Hub 데이터 안내 |
| `model-cards/` | 보험·법률 파인튜닝 사례 모델 카드 |
| `community/` | 개인 실험 글 원문 |

## papers/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `h_2407.15831.txt` | S01 | NV-Retriever. Table 1은 교사 모델 비교로 BM25 채굴 네거티브가 가장 낮음. TopK-PercPos 95%는 4.3.1절 임계값 탐색(Figure 1)에서 최선 |
| `h_2403.20327.txt` | S02 | Gecko. LLM 재순위로 정답 문단이 바뀐 비율 약 15% |
| `h_2209.11755.txt` | S03 | Promptagator. 합성 데이터로 학습한 검색기로 왕복 일관성 필터 |
| `h_2202.05144.txt` | S04 | InPars. 생성 확률 상위 질의만 남기는 필터 |
| `h_2401.00368.txt` | S05 | E5-mistral. 질의 길이·명확도·난이도를 변수로 두는 2단계 생성 지시문 |
| `h_2506.05176.txt` | S06 | Qwen3 Embedding. 역할 배정 합성, 거짓 네거티브 마스크(정답+0.1), 체크포인트 slerp 병합 |
| `h_2112.07577.txt` | S07 | GPL. 제로샷 기준 모델 대비 최대 +9.3, TSDAE+GPL 평균 +7.7(nDCG@10). DistilBERT 기반 |
| `h_2311.13534.txt` | S08 | LM-Cocktail 논문 |
| `h_2402.16829.txt` | S09 | GISTEmbed. 안내 모델로 배치 내 네거티브 선별 |
| `h_2101.06983.txt` | S10 | GradCache. 큰 대조 배치를 작은 메모리로 계산 |
| `acl_2025.emnlp-main.179.txt` | S11 | FinMTEB·Fin-E5 최종본. 검색 nDCG@10 0.6749→0.7105(p=0.0489), 19,467개, 100스텝 |
| `h_2502.10990.txt` | S11 | 같은 논문 arXiv v2. 본문 일부 수치가 최종본 표와 달라 최종본을 기준으로 씀 |
| `acl_2024.emnlp-industry.26.txt` | S12 | BAM. 문서 단위 분할 시험 44.7만 쌍에서 Recall@1 34.3%→62.8%. 하드 네거티브 0·1·3개 비교 |
| `h_2401.14654.txt` | S13 | 한국어 보험 분쟁 판단 데이터(493건 중 473건 사용). 검색 과제가 아님 |
| `acl_2022.cai-1.5.txt` | S14 | 한국어 암보험 대화 QA. 수집 12,734건 → 2,295건 선별 + 수작업 892건 |

## official/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `sbert_loss-overview.txt` | S15 | 데이터 형식별 손실 표. (질의, 정답[, 네거티브])의 기본 추천은 MNRL 계열 |
| `sbert_losses-reference.txt` | S15 | CMNRL·GISTEmbedLoss·CachedGIST 인자(scale 20, 온도 0.01 등) |
| `sbert_mine-hard-negatives.txt` | S16 | `mine_hard_negatives` 인자. 기본값 `relative_margin=None`, `num_negatives=3`과 NV-Retriever 권장 예제 |
| `sbert_domain-adaptation.txt` | S17 | 적응 사전학습의 비용과 GPL 안내 |
| `sbert_peft.txt` | S18 | LoRA 0.4705 대 전체 학습 0.4728(bert-base, GooAQ) |
| `hf-blog_embeddinggemma.md` | S19 | MIRIAD 의료 파인튜닝 예제. nDCG@10 0.8340→0.8862, Qwen3-0.6B 0.8493 |
| `hf-blog_train-reranker.md` | S20 | 도메인 학습한 작은 리랭커가 큰 범용 리랭커를 이겼다는 GooAQ 실험 |
| `ai-google-dev_fine-tuning-embeddinggemma.txt` | S21 | 도메인 삼중항(같은 의도 정답, 다른 의도 네거티브) 예시. 보험 예문 포함 |
| `anthropic_contextual-retrieval.txt` | S22 | 상위 20개 검색 실패율 5.7% → 3.7%(맥락) → 2.9%(+BM25) → 1.9%(+리랭커) |
| `vllm_pooling-models.txt` | S26 | `--runner pooling`과 풀링 설정 |
| `vllm_pooling-embed.txt` | S26 | `/v1/embeddings`, 지원 구조, bge-m3의 Matryoshka 차원 지정 거부 예시 |
| `vllm_pooling-token_embed.txt` | S26 | ColBERT 계열 토큰 임베딩 경로 |
| `vllm_engine-args.txt` | S26 | `gpu_memory_utilization`이 인스턴스별 비율이라는 설명 |
| `aihub_usage-policy.txt` | S38 | AI Hub 이용 정책. 국외 소재자 이용과 국외 반출은 별도 합의 필요 |
| `aihub_faq.txt` | S38 | AI Hub FAQ. 학습으로 만든 모델·서비스 등 2차 저작물의 영리 이용 허용과 제한 사항 |
| `aihub_robots.txt` | S38 | 수집 경로 확인용 |
| `data-go-kr_post-insurance-terms-api.txt` | S39 | 우체국보험 약관 API. 무료, 이용허락범위 제한 없음, 개발계정 신청 트래픽 10,000 |
| `data-go-kr_robots.txt` | S39 | 수집 경로 확인용 |
| `law-go-kr_insurance-standard-terms.txt` | S40 | 보험업감독업무시행세칙 별표 15 표준약관 PDF 추출본(1.4MB). 준거법 조항 9개 반복, 음절 순서 뒤섞임 사례 |
| `knia_term-disclosure-pages.txt` | S41 | 손해보험협회 상품비교공시 안내와 공시 용어 페이지. 직접 접속 403이라 검색 서비스 추출본 |
| `knia_consumer-faq.txt` | S41 | 손해보험협회 소비자 FAQ 사본 |
| `fss_dispute-case-list.txt` | S42 | 금감원 분쟁조정사례 목록. 201건은 전 금융 권역 합계 |
| `fss_dispute-case-example.txt` | S42 | 분쟁조정사례 상세 예시(민원 내용·쟁점·처리 결과·유의사항) |
| `fss_robots.txt` | S42 | 수집 경로 확인용 |
| `fss_copyright-policy.txt` | S43 | "수익을 얻거나 이에 상응하는 혜택" 목적 이용은 사전 협의·허락 |
| `opendart_document-api-guide.txt` | S44 | OpenDART 공시서류 원본 API 안내 |

## repos/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `FlagOpen_FlagEmbedding_LM-Cocktail_README.md` | S08 | `mix_models`, `mix_models_with_data`, 예시 가중치 `[0.5, 0.5]` |
| `yixuantt_FinMTEB_README.md` | S11 | FinMTEB 저장소 |
| `FlagOpen_FlagEmbedding_finetune-embedder_README.md` | S23 | 데이터 형식, `hn_mine.py`, 리랭커 점수 추가, bge-m3 통합 학습 예시 |
| `modelscope_ms-swift_Embedding.md` | S24 | InfoNCE 온도 기본 0.1, `INFONCE_MASK_FAKE_NEGATIVE` |
| `QwenLM_Qwen3-Embedding_README.md` | S25 | 지시문 사용 시 1~5% 향상, 영어 지시문 권장, MRL 지원 표 |
| `huggingface_text-embeddings-inference_README.md` | S27 | TEI 지원 구조(XLM-R, Qwen3, Gemma3, ModernBERT) |
| `shuzi_insuranceQA_README.md` | S46 | InsuranceQA 원 저장소. "for research purpose only" |

## datasets/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `tomaarsen_miriad-4.4M-split.md` | S19 | MIRIAD 분할. 질문이 원 문단에서 생성돼 어휘 중복이 크다는 설명 |
| `aihub_71610_finance-law-mrc.txt` | S36 | 원천 140,226건, 라벨 401,108건, 보험학 2.90% |
| `aihub_580_legal-terms-analysis.txt` | S37 | 약관 범주별 건수. 보험 명시 8개 범주 합계 1,355건 |
| `chaannwooff_Dartdoc.md` | S44 | 256,548 청크, CC-BY-4.0 표시 |
| `choeeiden_kor-insu-qaset.md` | S45 | 보험·의료 QA 719행, MIT 표시 |
| `deccan-ai_insuranceQA-v2.md` | S46 | InsuranceQA 파생 카드 |
| `nlpai-lab_ko-triplet-v1.0.md` | S47 | 744,862건. 라이선스·원 출처 표기 없음 |
| `jacepark12_kr-insurance-bench.md` | — | 카드에 태그만 있어 규모·출처 미확인. 문서 12절에서만 언급 |
| `vessl_insurance-policies.txt` | — | 직접 접근 401이라 검색 서비스 추출본. 51행, README 비어 있음. 데이터 본체·권리 미확인. 문서 12절에서만 언급. 원래 손보협회 추출본과 한 파일이었던 것을 분리 |

## model-cards/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `neuralchainai_embeddinggemma-300m-insuranceqa.md` | S30 | Recall@10 0.6082→0.7108. 평가 정답이 학습 답변에도 있다고 명시 |
| `epequeno_legal-embeddings-bge-base.md` | S31 | 우월성 주장 철회, 보류 데이터셋에서 이득 없음. 표 일부 Recall 100% 초과 |

## community/

| 파일 | 문서 출처 | 설명 |
|------|-----------|------|
| `philschmid_fine-tune-embedding-model-for-rag.txt` | S28 | 2024-06-04. nDCG@10 0.7684→0.8254. 시험 질의로 체크포인트를 고름 |
| `shrikar_finetune-embeddinggemma-insurance-retrieval.txt` | S29 | InsuranceQA 21,325행, L40S 605초. nDCG@10 0.732→0.818, Recall@10 0.850→0.936. 후보 200개 대 3,308개 정확도@1 |

## 받지 못한 자료

- Databricks 임베딩 파인튜닝 블로그는 403으로 막혀 사본이 없다. 문서에 인용하지 않았다.
- 손해보험협회 공시 페이지는 직접 접속이 403이라 검색 서비스 추출본만 있다(S41). 소비자 FAQ는 사본이 있다.
- `vessl/insurance-policies`는 직접 접근이 401이라 검색 서비스 추출본으로 카드만 확인했다. `42MARU/korean-financial-sft`는 401 응답으로 받지 못했다. `jjinho28/korean-insurance-qa`는 404다.
- S13 분쟁 데이터와 S14 대화 데이터는 논문만 받았고 데이터 본체는 받지 않았다.
- AI Hub 데이터 본체, 우체국보험 API 응답, OpenDART 원문은 이번 조사 범위 밖이라 받지 않았다.
