# Requests Automation Tool

Python requests 라이브러리를 활용한 HTTP 요청 자동화 도구입니다.

## 프로젝트 구조

```
.
├── main.py                 # 메인 실행 파일
└── module/
    ├── imports.py          # 라이브러리 import 모음
    ├── headers_module.py   # HTTP 헤더 및 데이터 관리
    ├── function.py         # CSV/JSON 파일 다운로드 함수
    └── console_module.py   # 콘솔 출력 유틸리티 (배너, overwrite 등)
```

## 모듈 설명

| 모듈 | 설명 |
|------|------|
| `main.py` | 도구 실행 진입점 |
| `imports.py` | 프로젝트에서 사용하는 라이브러리 통합 import |
| `headers_module.py` | requests 헤더 및 요청 데이터 저장/관리 |
| `function.py` | 결과를 CSV, JSON 형식으로 저장하는 함수 |
| `console_module.py` | 배너 출력, 실시간 콘솔 출력(overwrite) 기능 |

## 설치

```bash
git clone https://github.com/piroim/Python-script/request-script
cd requests-automation-tool
pip install -r requirements.txt
```

## 사용법

```bash
python main.py
```

## 요구사항

- Python 3.x
- requests