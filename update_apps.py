import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# JSON 파일 경로
JSON_FILE = "repo.json"

# 현재 날짜 가져오기 (YYYY-MM-DD 형식)
current_date = datetime.now().strftime("%Y-%m-%d")


def normalize_url(url):
    """한글이나 공백이 포함된 URL을 안전하게 인코딩"""
    parts = urllib.parse.urlsplit(url)
    encoded_path = urllib.parse.quote(parts.path, safe="/%")
    encoded_query = urllib.parse.quote(parts.query, safe="=&?/%")
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, encoded_path, encoded_query, parts.fragment)
    )


def get_cloudflare_file_size(download_url):
    """Cloudflare 직링크에서 파일 크기를 바이트 단위로 조회"""
    safe_url = normalize_url(download_url)
    headers = {"User-Agent": "Mozilla/5.0"}

    # 1순위: HEAD 요청으로 Content-Length 확인
    req = urllib.request.Request(safe_url, headers=headers, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > 0:
                return int(content_length)
    except urllib.error.HTTPError as e:
        if e.code not in (403, 405):
            raise

    # 2순위: HEAD가 차단되거나 길이가 없을 경우 1바이트 Range 요청으로 전체 크기 확인
    range_headers = {**headers, "Range": "bytes=0-0"}
    range_req = urllib.request.Request(safe_url, headers=range_headers, method="GET")
    with urllib.request.urlopen(range_req, timeout=30) as response:
        content_range = response.headers.get("Content-Range")
        if content_range and "/" in content_range:
            total_size = content_range.split("/")[-1].strip()
            if total_size.isdigit() and int(total_size) > 0:
                return int(total_size)

        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > 0:
            return int(content_length)

    raise ValueError("응답 헤더에서 파일 크기(Content-Length)를 확인할 수 없습니다.")


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

        if not download_url.startswith(("http://", "https://")):
            print(
                f"[{app_name} / {version_name}] "
                "지원하지 않는 다운로드 URL 형식입니다."
            )
            continue

        try:
            file_size = get_cloudflare_file_size(download_url)

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

    # 최신 버전(versions[0])의 용량을 최상위 app["size"]에도 반영
    if versions and isinstance(versions[0].get("size"), int) and versions[0]["size"] > 0:
        app["size"] = versions[0]["size"]


# 변경된 JSON 저장
with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
    f.write("\n")

print("모든 앱의 repo.json 갱신 작업이 완료되었습니다!")
