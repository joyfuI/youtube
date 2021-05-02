# 유튜브_sjva
[SJVA](https://sjva.me/) 용 YouTube 플러그인  
SJVA에서 유튜브 플레이리스트를 주기적으로 다운로드할 수 있습니다.

## 설치
> **반드시 [youtube-dl 플러그인](https://github.com/joyfuI/youtube-dl)이 설치되어 있어야지만 작동합니다!**

SJVA에서 "시스템 → 플러그인 → 플러그인 수동 설치" 칸에 저장소 주소를 넣고 설치 버튼을 누르면 됩니다.  
`https://github.com/joyfuI/youtube`

## 유의사항
스케줄러에는 플레이리스트만 등록할 수 있습니다.  
예전엔 채널 주소를 넣어도 youtube-dl이 플레이리스트 주소로 바꿔줘서 그냥 등록할 수 있었는데 언제부터인가 youtube-dl이 플레이리스트 주소로 바꿔주지 않으므로 채널의 전체 동영상을 스케줄러로 등록하려면 직접 플레이리스트 주소를 구해야 합니다.

채널의 업로드한 동영상 플레이리스트 주소를 구하는 방법은 채널의 동영상 탭에서 업로드한 동영상 옆에 있는 `모두 재생` 링크를 누르면 구할 수 있습니다.

![Imgur](https://i.imgur.com/HwX3USf.png)

아니면 **요청 페이지에서 채널 주소를 넣고 거기서 플레이리스트를 찾아 추가하셔도 됩니다.**

## 잡담
원래 스케줄링 메뉴만 비공식적으로 다른 동영상 사이트도 지원을 하긴 했으나 다른 동영상 사이트용 플러그인도 필요하긴 했고  
그렇다고 동영상 사이트별로 따로 플러그인을 만드는 건 미친 짓(...)이라는 생각이 들어 그냥 이 플러그인에서 유튜브뿐만 아니라 트위치, 브이라이브 등을 지원하도록 업데이트했습니다.  
youtube-dl에서 지원하는 사이트라면 모두 지원합니다만 사이트별로 youtube-dl에서 반환하는 정보가 달라서 동작하지 않거나 이상한 사이트가 있을 수도 있습니다. 그런 사이트는 제보 부탁드립니다.

일단 알려진 문제점으로 V LIVE 채널 주소를 넣었을 때 목록의 영상 이름이 `undefined`로 뜨는 문제가 있습니다.  
이건 youtube-dl에서 `title` 값을 반환해주지 않아서 어쩔 수 없습니다. 그렇다고 빈칸으로 둘 수도 없는 노릇이라 그냥 그대로 `undefined`(...)를 출력합니다.

## Changelog
v2.0.0
* SJVA3 대응

v1.1.2

v1.1.1
* 자막 다운로드를 해제해도 설정으로 저장되고 자막 다운로드가 안되는 문제 수정

v1.1.0
* 자막 다운로드 기능 추가
* 역순으로 다운로드 기능 추가  
  playlist_index도 역순으로 매겨져서 순서가 역순인 플레이리스트를 관리할 때 편리합니다.
* 설정에 경로 선택 버튼 추가
* 플레이리스트 관련 반환값 변경 대응

v1.0.2
* 스케줄링 중지가 안되는 문제 수정

v1.0.1
* 특정 스케줄이 수정 안되는 문제 수정

v1.0.0
* 트위치, V LIVE 등 다른 동영상 사이트 지원  
  그동안 스케줄링 메뉴에서만 비공식적으로 지원하던 타 동영상 사이트를 요청 페이지에서도 지원합니다.

v0.3.4
* 등록한 플레이리스트가 삭제되면 스케줄러가 그 부분부터 멈추는 문제 수정

v0.3.3

v0.3.2
* Python 2.7에서 날짜 지정이 안 되는 문제 수정

v0.3.1

v0.3.0
* Python 3 지원  
  Python 2를 유지한 채로 Python 3 지원을 추가했습니다.
* 날짜 지정 기능 추가  
  지정한 날짜 이후에 업로드된 동영상만 다운로드하는 옵션입니다.

v0.2.1
* 저장 폴더 수정이 안 되는 문제 수정

v0.2.0
* 다운로드, 스케줄 별로 저장 폴더 지정 기능 추가
* 트위치 등 다른 동영상 사이트 비공식 지원  
  youtube-dl에서 플레이리스트로 인식하는 다른 동영상 사이트 주소도 스케줄 등록을 할 수 있습니다.  
  단, 비공식 지원으로 스케줄링 메뉴만 정상적으로 작동합니다. 비공식 지원이지만 혹시 다른 동영상 사이트 중 작동하지 않는 사이트를 알려주시면 스케줄링이라도 작동하도록 고쳐보겠습니다.

v0.1.0
* 최초 공개
