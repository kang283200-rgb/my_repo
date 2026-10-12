import json
import urllib.request
from datetime import datetime

# apps.json 파일 읽기
with open('apps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

current_date = datetime.now().strftime("%Y-%m-%d")

for app in data.get('apps', []):
    download_url = app.get('downloadURL')
    app_name = app.get('name', '알 수 없는 앱')
    
    if not download_url:
        print(f"[{app_name}] 다운로드 URL이 없어 건너뜁니다.")
        continue

    try:
        # 1. 파일 용량 업데이트 (HEAD 요청)
        req = urllib.request.Request(download_url, method='HEAD')
        with urllib.request.urlopen(req) as response:
            file_size = int(response.headers.get('Content-Length', 0))
        
        if file_size > 0:
            app['size'] = file_size
            app['versionDate'] = current_date
        
        # 2. 버전명(태그) 업데이트 (GitHub API 활용)
        parts = download_url.split('/')
        # URL이 github.com 구조인지 확인
        if len(parts) >= 5 and parts[2] == 'github.com':
            owner, repo_name = parts[3], parts[4]
            api_url = f"https://api.github.com/repos/{owner}/{repo_name}/releases/latest"
            
            api_req = urllib.request.Request(api_url)
            # GitHub API는 User-Agent 헤더가 없으면 요청을 차단하므로 추가
            api_req.add_header('User-Agent', 'Python-urllib')
            
            with urllib.request.urlopen(api_req) as api_response:
                release_data = json.loads(api_response.read())
                tag_name = release_data.get('tag_name', '')
                
                # 'v1.0.0' 형태라면 앞에 'v'를 제거
                if tag_name.startswith('v'):
                    tag_name = tag_name[1:]
                    
                if tag_name:
                    app['version'] = tag_name
                    print(f"[{app_name}] 갱신 완료: 버전 {tag_name}, 용량 {file_size} Bytes")
                else:
                    print(f"[{app_name}] 태그를 찾을 수 없어 용량만 갱신했습니다.")
        else:
            print(f"[{app_name}] GitHub 다운로드 링크가 아니어 버전명은 갱신하지 않았습니다.")
            
    except urllib.error.HTTPError as e:
        # 릴리스가 아직 없거나 비공개 저장소인 경우 에러 처리
        print(f"[{app_name}] GitHub API 접근 실패 (상태 코드: {e.code}). 릴리스가 존재하는지 확인하세요.")
    except Exception as e:
        print(f"[{app_name}] 처리 중 오류 발생: {e}")

# 변경된 데이터를 apps.json에 덮어쓰기
with open('apps.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("모든 앱의 버전 및 용량 갱신이 완료되었습니다!")
