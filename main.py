"""열여섯 성정의 동행록 — Streamlit Cloud에 main.py 하나로 배포하는 수업용 앱.

Cloud의 Main file path에 main.py를 지정합니다.
로컬에서는 Streamlit 설치 후 `streamlit run main.py`로 실행합니다.
이미지는 공식 Pokémon 사이트에서 불러옵니다. 인터넷 연결이 필요합니다.
Python 표준 라이브러리와 Streamlit만 사용하며 CSS·JavaScript는 아래에 포함합니다.
"""

from html import escape
from http.client import HTTPException
from urllib.error import URLError
from urllib.request import Request, urlopen

import streamlit as st


IMAGE_BASE = "https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/"
POKEDEX_BASE = "https://www.pokemon.com/us/pokedex/"

# 기본 형태의 타입과 특징입니다. MBTI 대응 및 이유는 수업용 창작 해석입니다.
POKEMON = {
    "INTJ": {
        "ko": "후딘", "en": "Alakazam", "number": "065", "slug": "alakazam",
        "types": ["에스퍼"], "epithet": "사유의 깊이를 헤아리는 현자", "emoji": "🧠",
        "feature": "뛰어난 지능과 강력한 초능력을 지닌 포켓몬이다. 두 손의 숟가락이 독특한 인상을 남긴다.",
        "reasons": [
            "사태의 표면보다 그 이면의 질서를 탐구하는 그대에게, 후딘의 지적인 모습은 좋은 비유가 되오.",
            "홀로 사유를 벼리고 장기적인 구상을 세우는 성정이 서로 상응하오.",
            "멀리 내다보는 안목을 함께 나누기에 어울리는 벗이라 하겠소.",
        ],
    },
    "INTP": {
        "ko": "폴리곤", "en": "Porygon", "number": "137", "slug": "porygon",
        "types": ["노말"], "epithet": "가상의 질서를 탐구하는 학자", "emoji": "💻",
        "feature": "과학 기술로 만들어진 인공 포켓몬이다. 사이버 공간을 자유롭게 이동할 수 있다.",
        "reasons": [
            "당연한 명제에도 물음을 던지는 그대에게, 폴리곤은 원리 탐구의 흥미로운 동행이오.",
            "새로운 체계와 추상적인 가능성을 즐기는 기질이 디지털 존재의 이미지와 맞닿아 있소.",
            "해답을 서두르기보다 질문의 깊이를 함께 넓혀 갈 벗이라 하겠소.",
        ],
    },
    "ENTJ": {
        "ko": "리자몽", "en": "Charizard", "number": "006", "slug": "charizard",
        "types": ["불꽃", "비행"], "epithet": "높은 뜻을 펼치는 불꽃의 선봉", "emoji": "🔥",
        "feature": "커다란 날개로 하늘을 날며 뜨거운 불꽃을 내뿜는다. 기본 형태는 불꽃·비행 타입이다.",
        "reasons": [
            "목표를 정하면 과감히 나아가는 그대의 기상은 리자몽의 힘찬 비상과 닮았소.",
            "구상을 실행으로 옮기는 추진력에 불꽃의 이미지를 겹쳐 보았소.",
            "큰 도전 앞에서 함께 용기를 북돋울 벗이라 하겠소.",
        ],
    },
    "ENTP": {
        "ko": "팬텀", "en": "Gengar", "number": "094", "slug": "gengar",
        "types": ["고스트", "독"], "epithet": "정설의 틈을 엿보는 재치의 객", "emoji": "👻",
        "feature": "그림자 속에 숨어 주변의 열을 빼앗는 포켓몬이다. 넓은 미소와 신비로운 모습이 특징이다.",
        "reasons": [
            "익숙한 관점을 뒤집어 새 가능성을 찾는 그대에게, 팬텀의 의외성은 좋은 비유가 되오.",
            "재치 있는 질문과 자유로운 발상이 예측하기 어려운 이미지와 어우러지오.",
            "평범한 하루에도 새로운 논제를 던져 줄 듯한 벗이라 하겠소.",
        ],
    },
    "INFJ": {
        "ko": "가디안", "en": "Gardevoir", "number": "282", "slug": "gardevoir",
        "types": ["에스퍼", "페어리"], "epithet": "보이지 않는 마음의 수호자", "emoji": "🔮",
        "feature": "초능력을 다루며 트레이너를 지키려 하는 포켓몬이다. 우아한 실루엣과 보호의 이미지가 두드러진다.",
        "reasons": [
            "말 너머의 마음을 헤아리는 그대의 통찰을 가디안의 보호적인 모습에 비추어 보았소.",
            "소중한 가치와 관계를 깊이 지키려는 성정이 서로 상응하오.",
            "고요한 이해와 신뢰를 나누기에 어울리는 벗이라 하겠소.",
        ],
    },
    "INFP": {
        "ko": "이브이", "en": "Eevee", "number": "133", "slug": "eevee",
        "types": ["노말"], "epithet": "아직 쓰이지 않은 가능성의 시", "emoji": "🌱",
        "feature": "다양한 진화 가능성을 품은 포켓몬이다. 불안정한 유전적 구조가 여러 진화 형태와 연결된다.",
        "reasons": [
            "자신만의 가치와 가능성을 소중히 품는 그대에게, 이브이는 열린 미래의 비유가 되오.",
            "하나의 틀에 머물지 않는 상상력과 섬세한 감성이 그 모습과 어우러지오.",
            "서두르지 않고 각자의 길을 찾아갈 벗이라 하겠소.",
        ],
    },
    "ENFJ": {
        "ko": "망나뇽", "en": "Dragonite", "number": "149", "slug": "dragonite",
        "types": ["드래곤", "비행"], "epithet": "함께 나아갈 길을 밝히는 인도자", "emoji": "🐉",
        "feature": "날개를 지닌 드래곤 포켓몬이다. 큰 체구와 부드러운 표정이 대비되는 모습을 지녔다.",
        "reasons": [
            "사람의 장점을 발견하고 성장을 돕는 그대의 성정을 망나뇽의 든든한 모습에 빗대었소.",
            "목표와 관계를 함께 돌보는 기질이 힘과 온화함의 조화와 맞닿아 있소.",
            "동행하는 이에게 용기를 건네기에 어울리는 벗이라 하겠소.",
        ],
    },
    "ENFP": {
        "ko": "피카츄", "en": "Pikachu", "number": "025", "slug": "pikachu",
        "types": ["전기"], "epithet": "새로운 인연에 빛을 켜는 불씨", "emoji": "⚡",
        "feature": "양 볼의 전기 주머니에 전기를 모은다. 노란 몸과 번개 모양의 꼬리를 지닌 포켓몬이다.",
        "reasons": [
