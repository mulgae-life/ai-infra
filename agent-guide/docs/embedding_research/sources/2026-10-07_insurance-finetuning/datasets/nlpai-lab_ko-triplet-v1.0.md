---

language:
- ko
dataset_info:
  features:
  - name: query
    dtype: string
  - name: document
    dtype: string
  - name: hard_negative
    dtype: string
  splits:
  - name: train
    num_bytes: 628315763
    num_examples: 744862
  download_size: 270060556
  dataset_size: 628315763
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*

---

# Dataset Card for nlpai-lab/ko-triplet-v1.0

## Dataset Statistics

| Split | # Examples | Size (bytes) |
|-------|------------|--------------|
| Train | 744,862 | 628,315,763 |

## Dataset Structure

### Train Sample
| query | document | hard_negative |
| --- | --- | --- |
| 데이터 사전 캐시 방법을 적용하면 어떻게 11초에서 요청한 데이터를 핸드오버 구간이 지나고 난 다음인 14초에 타겟 드론을 통해 받을 수 있어? | 제안된 방법을 적용한 경우에는 11초에서 요청한 데이터를 진행 방향에 있는 타겟 드론의 CS에 사전에 캐시 해둠으로써 핸드오버 구간이 지나고 난 다음인 14초에서 타겟 드론을 통해 데이터를 받는다. | 데이터 요청자가 타겟 드론으로 핸드오버 하기 전에, 요청한 데이터를 타겟 드론의 CS로 사전에 캐시한다. |
| 대통령, 경제, 회복, 고용, 안정, 대책, 발표하다 | 대통령이 신년 방송에서 경제 회복과 고용 안정 대책을 발표했다. | 경제 성장이 높을 때 생산, 고용, 판매, 소득이 더욱 증가한다. |
| 고지방 식이와 간장 무게의 상관관계를 다룬 연구를 한 사람은 누구인가? | 고지방 섭취 시 간장 무게가 증가한다는 Sung, Wursch 및 Park의 보고와 일치되는 결과였으며, 고지방 섭취로 인해 간장이 비대해지고, 동맥 내에 지질이 축적되어 관상 순환의 이상으로 야기된 것으로 생각된다. | Shin 등은 고지방 식이에 연잎 건분을 첨가한 식이로서 6 주간 사육했을 때 유의적인 체중감소효과를 나타내었으며, 이때 간장, 신장, 비장, 폐 등의 장기 무게도 감소한 결과는 체중감소로 인한 장기무게의 감소로 보고한 바 있다. |
| 올해, 엄마, 만나다, 고향, 오다 | 나는 올해 엄마를 만나러 고향에 자주 왔다. | 수박, 참외, 조롱박, 수세미, 오이, 가지를 정성껏 심어 무럭무럭 키웠다. |
| 뛰어오르다, 위, 하다, 수탉, 지붕 | 고양이가 슬금슬금 다가오자 수탉은 푸드득 하고 지붕 위로 뛰어올랐다. | 재주는 예절, 음악, 활쏘기, 글쓰기, 말타기, 계산하기 등등 이다. |

