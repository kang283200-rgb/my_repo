import json
import urllib.request
from datetime import datetime

# apps.json 파일 읽기
with open('apps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 현재 날짜 가져오기 (YYYY-MM-DD 형식)
current_date = datetime.now().strftime("%Y-%m-%d")

# apps 배열 안의 모든 앱을 순회하며 개별 업데이트
for app in data.get('apps', []):
    download_url = app.get('downloadURL')
    app_name = app.get('name', '알 수 없는 앱')
    
    if not download_url:
        print(f"[{app_name}] 다운로드 URL이 없어 건너뜁니다.")
        continue

    try:
        # HEAD 요청: 파일을 실제로 다운로드하지 않고 용량(헤더) 정보만 빠르게 추출
        req = urllib.request.Request(download_url, method='HEAD')
        with urllib.request.urlopen(req) as response:
            file_size = int(response.headers.get('Content-Length', 0))
        
        if file_size > 0:
            app['size'] = file_size
            app['versionDate'] = current_date
            print(f"[{app_name}] 용량 업데이트 완료: {file_size} Bytes")
        else:
            print(f"[{app_name}] 용량을 확인할 수 없습니다.")
            
    except Exception as e:
        print(f"[{app_name}] 접근 실패 (URL을 확인하세요): {e}")

# 변경된 데이터를 apps.json에 덮어쓰기
with open('apps.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("모든 앱의 apps.json 갱신이 완료되었습니다!")
