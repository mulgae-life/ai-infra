---
language:
- ko
license: cc-by-4.0
task_categories:
- text-generation
- fill-mask
pretty_name: Dartdoc - Korean Financial Disclosure Dataset
size_categories:
- 100K<n<1M
tags:
- korean
- finance
- dart
- financial-disclosure
- llm
- pretraining
---

# Dartdoc - 한국 금융공시 텍스트 데이터셋

한국 금융감독원 전자공시시스템(DART) OpenAPI를 통해 수집한 한국어 LLM 학습용 데이터셋입니다.
사업보고서, 증권신고서 등 공시 문서에서 고품질 한국어 텍스트를 추출하였습니다.

## 데이터셋 개요

| 항목 | 내용 |
|------|------|
| 언어 | 한국어 (ko) |
| 수집 기간 | 2020년 ~ 2025년 |
| 총 레코드 수 | 256,548건 |
| 총 텍스트 | 약 4.6억 자 |
| 평균 청크 길이 | 약 1,794자 |
| 출처 | 금융감독원 DART OpenAPI |

## 수집 대상

| 공시 유형 | 코드 | 대상 문서 | 필터 조건 |
|-----------|------|-----------|-----------|
| 정기공시 | `A` | 사업보고서 | 반기/분기보고서 제외 |
| 발행공시 | `C` | 증권신고서 | 정정신고서·집합투자 제외 |

## 추출 섹션

문서 전체가 아닌 품질이 높은 본문 섹션만 추출합니다.

| 섹션 | 내용 |
|------|------|
| II | 사업의 내용 |
| IV | 이사의 경영진단 및 분석의견 |

## 데이터 구조

```json
{
  "rcept_no": "20240331001234",
  "corp_name": "삼성전자",
  "report_type": "사업보고서",
  "file": "0001.xml",
  "section": "II",
  "chunk": 0,
  "text": "당사는 반도체, 스마트폰 등 다양한 전자제품을 생산·판매하고 있으며..."
}
```

### 필드 설명

| 필드 | 설명 |
|------|------|
| `rcept_no` | DART 접수번호 |
| `corp_name` | 회사명 |
| `report_type` | 공시 유형 (사업보고서 / 증권신고서) |
| `file` | 원본 XML 파일명 |
| `section` | 추출 섹션 (II / IV) |
| `chunk` | 청크 인덱스 (문서 내 순서) |
| `text` | 본문 텍스트 (200자 이상, 최대 2,000자) |

## 텍스트 필터링 기준

- 한글 비율 20% 미만인 줄 제거
- 숫자/특수문자로만 구성된 줄 제거
- 200자 미만 청크 제거
- 청크 단위: 최대 2,000자 (단어 경계 기준)

## 데이터 출처

- 금융감독원 전자공시시스템(DART): https://dart.fss.or.kr
- DART OpenAPI: https://opendart.fss.or.kr

본 데이터셋은 공공데이터를 활용하여 구축되었습니다.
