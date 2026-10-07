{
 "sample_rows": 1480,
 "counts": {
  "ok": 1479,
  "error": 1
 },
 "latency_ms": {
  "median": 449.6,
  "p95": 17066.8,
  "mean": 3004.7
 },
 "check_full_panel": {
  "jev": {
   "recomputed": 57.91,
   "published": 57.91
  },
  "simple-jev-qwen3.8-27b-bf16": {
   "recomputed": 55.74,
   "published": 55.74
  }
 },
 "no_hle": {
  "jev": {
   "scores": {
    "balanced_skill": 59.48,
    "balanced_raw": 69.48,
    "breadth_skill": 58.73
   },
   "areas": {
    "knowledge": 57.2,
    "language": 62.0,
    "retrieval": 55.4,
    "tools": 75.1,
    "arts": 37.7
   }
  },
  "simple-jev-qwen3.8-27b-bf16": {
   "scores": {
    "balanced_skill": 57.17,
    "balanced_raw": 67.67,
    "breadth_skill": 55.72
   },
   "areas": {
    "knowledge": 41.1,
    "language": 62.1,
    "retrieval": 63.3,
    "tools": 76.2,
    "arts": 36.5
   }
  },
  "ours": {
   "scores": {
    "balanced_skill": 55.47,
    "balanced_raw": 66.22,
    "breadth_skill": 53.85
   },
   "areas": {
    "knowledge": 40.6,
    "language": 62.0,
    "retrieval": 56.8,
    "tools": 77.2,
    "arts": 32.4
   }
  }
 }
}

| 영역 | 벤치 | 지표 | 응답 | 우리 raw | simple-jev raw | Jev raw | 우리 skill | simple-jev skill | Jev skill |
|---|---|---|---|---|---|---|---|---|---|
| knowledge | GPQA Diamond | accuracy | 40 | 0.450 | 0.485 | 0.786 | 0.267 | 0.313 | 0.714 |
| knowledge | GSM8K | accuracy | 40 | 0.700 | 0.652 | 0.799 | 0.628 | 0.577 | 0.756 |
| knowledge | ChessBench | accuracy | 40 | 0.150 | 0.174 | 0.172 | 0.084 | 0.100 | 0.098 |
| knowledge | MuSR | accuracy | 40 | 0.625 | 0.632 | 0.661 | 0.404 | 0.414 | 0.461 |
| knowledge | SATA-Bench | case exact accuracy | 40 | 0.200 | 0.321 | 0.264 | 0.189 | 0.312 | 0.254 |
| knowledge | CRUXEval | accuracy | 40 | 0.600 | 0.623 | 0.730 | 0.380 | 0.402 | 0.571 |
| knowledge | CLadder | accuracy | 40 | 0.775 | 0.710 | 0.726 | 0.550 | 0.420 | 0.453 |
| knowledge | MMLU-Pro | accuracy | 40 | 0.600 | 0.598 | 0.827 | 0.550 | 0.547 | 0.805 |
| knowledge | BBH | accuracy | 40 | 0.700 | 0.708 | 0.929 | 0.565 | 0.577 | 0.897 |
| language | ContractNLI | macro-F1 | 40 | 0.756 | 0.775 | 0.717 | 0.647 | 0.675 | 0.591 |
| language | ANLI | macro-F1 | 40 | 0.694 | 0.692 | 0.748 | 0.541 | 0.539 | 0.622 |
| language | WinoGrande | accuracy | 40 | 0.850 | 0.845 | 0.919 | 0.700 | 0.689 | 0.839 |
| language | HellaSwag | accuracy | 40 | 0.950 | 0.931 | 0.945 | 0.933 | 0.908 | 0.927 |
| language | ACOS | per-review F1 | 40 | 0.343 | 0.356 | 0.295 | 0.322 | 0.335 | 0.273 |
| language | FinEntity | macro-F1 | 40 | 0.859 | 0.885 | 0.870 | 0.793 | 0.831 | 0.808 |
| language | iSarcasmEval | Sarcasm F1 · track A, English | 40 | 0.667 | 0.604 | 0.505 | 0.571 | 0.490 | 0.363 |
| language | VAST | macro-F1 | 40 | 0.722 | 0.719 | 0.646 | 0.583 | 0.578 | 0.469 |
| language | NLI4CT | macro-F1 | 40 | 0.813 | 0.837 | 0.841 | 0.637 | 0.684 | 0.690 |
| language | RAGTruth | F1 on hallucinated class | 40 | 0.718 | 0.723 | 0.765 | 0.415 | 0.426 | 0.513 |
| retrieval | BANKING77 | macro-F1 | 40 | 0.869 | 0.795 | 0.797 | 0.867 | 0.792 | 0.795 |
| retrieval | CLINC150+OOS | macro-F1 | 40 | 0.774 | 0.881 | 0.893 | 0.773 | 0.880 | 0.892 |
| retrieval | BRIGHT | nDCG@10 | 39 | 0.338 | 0.497 | 0.475 | 0.267 | 0.431 | 0.406 |
| retrieval | Amazon ESCI | macro-F1 | 40 | 0.448 | 0.574 | 0.552 | 0.308 | 0.465 | 0.438 |
| retrieval | PhishNChips phishing decisions | accuracy | 40 | 0.800 | 0.847 | 0.625 | 0.600 | 0.693 | 0.251 |
| retrieval | HoVer | accuracy | 40 | 0.775 | 0.746 | 0.729 | 0.550 | 0.492 | 0.457 |
| tools | BFCL | case exact accuracy | 40 | 0.975 | 0.968 | 0.958 | 0.967 | 0.957 | 0.943 |
| tools | ToolRet | nDCG@10 | 40 | 0.725 | 0.680 | 0.653 | 0.679 | 0.630 | 0.599 |
| tools | API-Bank | accuracy | 40 | 0.875 | 0.854 | 0.882 | 0.873 | 0.852 | 0.880 |
| tools | Home appliance simulator | case exact accuracy | 40 | 0.650 | 0.648 | 0.523 | 0.650 | 0.648 | 0.523 |
| tools | When2Call | accuracy | 40 | 0.725 | 0.750 | 0.810 | 0.633 | 0.667 | 0.746 |
| arts | BPoMP | accuracy | 40 | 0.964 | 0.963 | 0.909 | 0.929 | 0.925 | 0.818 |
| arts | Humicroedit | accuracy | 40 | 0.625 | 0.613 | 0.619 | 0.250 | 0.226 | 0.237 |
| arts | POP909-CL | accuracy | 40 | 0.282 | 0.283 | 0.166 | 0.276 | 0.277 | 0.159 |
| arts | cfcolor | accuracy | 40 | 0.542 | 0.633 | 0.644 | 0.083 | 0.267 | 0.288 |
| arts | ForecastBench | Brier (lower is better) | 40 | 0.174 | 0.148 | 0.306 | 0.174 | 0.148 | 0.306 |
| arts | Habermas Machine | accuracy | 40 | 0.375 | 0.410 | 0.459 | 0.088 | 0.144 | 0.215 |
| arts | New Yorker | accuracy | 40 | 0.600 | 0.688 | 0.701 | 0.500 | 0.609 | 0.626 |
