import re
import requests

# 발급받으신 구글 API 키를 여기에 넣습니다.
GOOGLE_API_KEY = "AIzaSyBrvetD_WeBtyQckY7bw56chk4iU8tP1aI"

def get_file_size(url):
    # 1. 구글 드라이브 링크인지 확인하고 파일 ID를 추출합니다.
    gdrive_match = re.search(r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)', url)
    if not gdrive_match:
        gdrive_match = re.search(r'drive\.google\.com/uc\?.*id=([a-zA-Z0-9_-]+)', url)

    if gdrive_match:
        file_id = gdrive_match.group(1)
        # 구글 드라이브 API를 통해 'size' 메타데이터만 정확히 요청합니다.
        api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=size&key={GOOGLE_API_KEY}"
        
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                return int(data.get('size', 0)) # 정확한 바이트 용량 반환
            else:
                print(f"용량 가져오기 실패: {response.text}")
                return 0
        except Exception as e:
            print(f"오류 발생: {e}")
            return 0

    # 2. 구글 드라이브가 아닌 기존 링크(드롭박스 등)일 경우 기존 방식 그대로 사용
    try:
        response = requests.head(url, allow_redirects=True)
        if 'Content-Length' in response.headers:
            return int(response.headers['Content-Length'])
    except Exception as e:
        print(f"오류 발생: {e}")
    
    return 0

# --- 테스트 ---
# print(get_file_size("https://drive.google.com/file/d/1aB2c3D4e5F6g7H8i9J0/view"))
