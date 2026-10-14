import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Google Drive API 키
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# JSON 파일 경로
JSON_FILE = "repo.json"

# 현재 날짜 가져오기 (YYYY-MM-DD 형식)
current_date = datetime.now().strftime("%Y-%m-%d")


def extract_drive_file_id(download_url):
    """Google Drive 다운로드 URL에서 파일 ID 추출"""

    patterns = [
        r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/uc\?.*?[?&]id=([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, download_url)

        if match:
            return match.group(1)

    return None


def get_google_drive_file_size(file_id):
    """Google Drive API를 이용해 파일 크기를 바이트 단위로 조회"""

    api_url = (
        f"https://www.googleapis.com/drive/v3/files/{file_id}"
        f"?fields=id,name,size&key={urllib.parse.quote(GOOGLE_API_KEY)}"
    )

    req = urllib.request.Request(
        api_url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        file_data = json.loads(response.read().decode("utf-8"))

    if "size" not in file_data:
        raise ValueError(
            "API 응답에 파일 크기가 없습니다. 파일 접근 권한을 확인하세요."
        )

    return int(file_data["size"])


# API 키 확인
if not GOOGLE_API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY 환경 변수가 설정되지 않았습니다."
    )


# repo.json 파일 읽기
with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


# 모든 앱과 버전 순회
for app in data.get("apps", []):
    app_name = app.get("name", "알 수 없는 앱")
    versions = app.get("versions", [])

    if not versions:
        print(f"[{app_name}] 버전 정보가 없어 건너뜁니다.")
        continue

    for version_info in versions:
        version_name = version_info.get("version", "알 수 없는 버전")
        download_url = version_info.get("downloadURL")

        if not download_url:
            print(
                f"[{app_name} / {version_name}] "
                "다운로드 URL이 없어 건너뜁니다."
            )
            continue

        file_id = extract_drive_file_id(download_url)

        if not file_id:
            print(
                f"[{app_name} / {version_name}] "
                "Google Drive 파일 ID를 추출할 수 없습니다."
            )
            continue

        try:
            file_size = get_google_drive_file_size(file_id)

            if file_size > 0:
                version_info["size"] = file_size
                
                print(
                    f"[{app_name} / {version_name}] "
                    f"용량 업데이트 완료: {file_size:,} Bytes"
                )
            else:
                print(
                    f"[{app_name} / {version_name}] "
                    "파일 크기가 0이어서 기존 값을 유지합니다."
                )

        except Exception as e:
            print(
                f"[{app_name} / {version_name}] "
                f"조회 실패: {e}"
            )


# 변경된 JSON 저장
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("모든 앱의 repo.json 갱신 작업이 완료되었습니다!")
