# LOWKEY 검색 페이지 설치

기존 매거진/게임 화면은 유지하고 검색 가능한 기사형 페이지를 함께 제공합니다.
이 파일 묶음은 아직 GitHub에 배포되지 않았습니다.

## 한 번만 설치

1. 기존 web 저장소의 index.html을 백업합니다.
2. ZIP 안의 index.html과 tools 폴더를 web 저장소 최상위(index.html, posts.json이 있는 곳)에 올립니다. 기존 posts.json과 이미지·게임 파일은 지우거나 덮어쓰지 않습니다. 이 묶음에는 posts.json이 없습니다.
3. GitHub의 Add file → Create new file에서 파일 이름을 `.github/workflows/lowkey-pages.yml`로 입력합니다. ZIP의 같은 파일 내용을 복사해 저장합니다. 윈도우에서 .github 폴더가 안 보이더라도 이 방법으로 생성할 수 있습니다.
4. 저장소 Settings → Pages → Build and deployment → Source를 **GitHub Actions**로 선택합니다.
5. Actions → LOWKEY Pages + Search → Run workflow를 실행합니다. 기존 Pages 배포용 YAML이 있다면 두 배포 작업이 동시에 돌지 않도록 기존 Pages 배포 워크플로만 비활성화합니다. 다른 용도의 워크플로는 유지합니다.
6. 초록색 성공 표시 후 아래 주소를 확인합니다.
   - 사이트: https://lowkeyrecordz.github.io/web/
   - 기사 목록: https://lowkeyrecordz.github.io/web/search/
   - 영문 목록: https://lowkeyrecordz.github.io/web/search/en/
   - 사이트맵: https://lowkeyrecordz.github.io/web/sitemap.xml

대상은 `lowkeyrecordz/web` 저장소, `main` 브랜치, 루트의 index.html/posts.json입니다. 다른 브랜치나 docs 폴더를 사용한다면 설치 전 workflow의 branches/source 값을 맞춰야 합니다.

## 이후 글 발행

기존 관리자에서 저장 → 전체 게시를 누르면 posts.json 커밋에 맞춰 검색 페이지와 사이트맵을 자동 생성하고 배포합니다. 로컬 저장만 한 초안은 공개하지 않습니다. 글을 지우면 다음 빌드에서 검색 페이지도 제거됩니다. 사진은 공개 posts.json의 이미지에서 추출합니다.
영문 입력이 있는 글만 영어 페이지를 만듭니다. 첫 매거진은 index.html에 포함된 번역본도 사용합니다. 새 글을 자동 번역하는 기능은 아닙니다.

## 구글 서치 콘솔 (사이트 소유자가 진행)

1. https://search.google.com/search-console 에서 URL 접두어 속성 `https://lowkeyrecordz.github.io/web/`을 추가합니다.
2. HTML 파일 인증을 선택하고 구글이 제공한 인증 HTML을 저장소 루트에 올립니다. 배포 완료 후 확인을 누릅니다. 코드를 임의로 생성하지 마세요.
3. Sitemaps에 `https://lowkeyrecordz.github.io/web/sitemap.xml`을 제출합니다.
4. 기사 목록에서 매거진의 실제 주소를 복사해 URL 검사 → 실제 URL 테스트를 실행하고, 본문이 보이는지 확인한 뒤 색인 생성을 요청합니다.
5. 구조화 데이터는 https://search.google.com/test/rich-results 에서 기사 주소로 검사합니다. 소유권 인증·구글 검사·색인 요청은 이 묶음에서 대신 실행하지 않았습니다. 색인 및 노출은 구글이 결정합니다.

`/web/robots.txt`는 도메인 전체의 robots 설정이 아니므로 만들지 않습니다. `https://lowkeyrecordz.github.io/robots.txt`에 기존 차단 규칙이 있다면 해당 루트 저장소에서 점검해야 합니다.

## 구성 / 검증 범위

- index.html: 한/영 본문판 유지, 기사 목록/기사형 읽기 링크, 레이블 Organization 정보.
- tools/build_search.py: Python 표준 라이브러리만 사용. 저널·뉴스·공지의 한국어/영어 본문, 사진, 서식, 링크, 게시일, canonical, 언어별 hreflang, Article JSON-LD, 사이트맵 생성.
- .github/workflows/lowkey-pages.yml: 저장소에 글 변경이 올라오면 생성 후 GitHub Pages 배포.
- 비밀의 방: 소개 페이지와 입장 링크만 검색 대상으로 제공. 숨겨진 파편·대화는 검색용 본문에 넣지 않습니다.
- 원래 매거진 주소와 게임 주소는 그대로 동작합니다. 기사형 페이지에서 '잡지로 펼쳐 읽기'로 이동할 수 있습니다.
- 검증: HTML 내 JS 문법, 첫 매거진 한/영 본문을 이용한 빌드, 안전한 텍스트 출력, 사진 추출, 언어 연결, XML 사이트맵, 삭제 후 재생성. 실제 저장소의 Actions 실행과 구글 색인은 설치 후 확인해야 합니다.

## 되돌리기

기존 index.html을 복원하고 Pages Source를 원래 설정으로 되돌립니다. 새 LOWKEY Pages + Search 워크플로를 비활성화합니다. 이 작업은 posts.json의 글을 변경하지 않습니다.
