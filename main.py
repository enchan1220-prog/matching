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
            "새로운 만남과 가능성에 설레는 그대에게, 피카츄의 밝은 모습은 좋은 비유가 되오.",
            "상상과 열정으로 주변에 활기를 더하는 기질을 전기의 반짝임에 겹쳐 보았소.",
            "낯선 길에서도 즐거운 호기심을 함께 나눌 벗이라 하겠소.",
        ],
    },
    "ISTJ": {
        "ko": "거북왕", "en": "Blastoise", "number": "009", "slug": "blastoise",
        "types": ["물"], "epithet": "약속을 굳건히 지키는 성벽", "emoji": "🐢",
        "feature": "등껍질에 달린 두 개의 대포로 물을 발사한다. 두꺼운 등껍질과 묵직한 체구가 특징이다.",
        "reasons": [
            "기본과 약속을 지키며 맡은 일을 완수하는 그대를 거북왕의 단단한 모습에 비추어 보았소.",
            "꾸준한 준비와 책임감이 묵직한 안정감의 이미지와 상응하오.",
            "말보다 행동으로 신뢰를 쌓아 갈 벗이라 하겠소.",
        ],
    },
    "ISFJ": {
        "ko": "럭키", "en": "Chansey", "number": "113", "slug": "chansey",
        "types": ["노말"], "epithet": "작은 안부를 잊지 않는 돌봄의 벗", "emoji": "🥚",
        "feature": "배의 주머니에 알을 지니고 다닌다. 영양가 높은 알을 아프거나 다친 이에게 나누는 포켓몬이다.",
        "reasons": [
            "드러나지 않는 필요까지 살피는 그대의 배려를 럭키의 돌봄에 빗대었소.",
            "작은 정성과 꾸준한 도움으로 관계를 지키는 성정이 서로 어우러지오.",
            "오래된 인연을 다정하게 돌보기에 어울리는 벗이라 하겠소.",
        ],
    },
    "ESTJ": {
        "ko": "강철톤", "en": "Steelix", "number": "208", "slug": "steelix",
        "types": ["강철", "땅"], "epithet": "질서를 세우는 강철의 기둥", "emoji": "🛡️",
        "feature": "강철 같은 몸으로 땅속을 파고드는 포켓몬이다. 길게 이어진 금속성 몸체가 특징이다.",
        "reasons": [
            "명료한 기준으로 일을 정리하는 그대에게, 강철톤의 단단함은 좋은 비유가 되오.",
            "현실적인 판단과 책임 있는 실행이 굳건한 기둥의 이미지와 상응하오.",
            "흔들리는 상황에서도 중심을 함께 잡아 줄 벗이라 하겠소.",
        ],
    },
    "ESFJ": {
        "ko": "푸린", "en": "Jigglypuff", "number": "039", "slug": "jigglypuff",
        "types": ["노말", "페어리"], "epithet": "사람 사이의 선율을 잇는 가객", "emoji": "🎵",
        "feature": "둥근 몸과 큰 눈을 지닌 포켓몬이다. 노래로 듣는 이를 잠들게 하는 것으로 알려져 있다.",
        "reasons": [
            "사람 사이의 분위기를 살피는 그대의 친화력을 푸린의 선율에 비추어 보았소.",
            "함께하는 순간을 정성껏 가꾸는 기질이 부드러운 이미지와 어우러지오.",
            "서로 다른 마음을 한자리에 이어 줄 벗이라 하겠소.",
        ],
    },
    "ISTP": {
        "ko": "핫삼", "en": "Scizor", "number": "212", "slug": "scizor",
        "types": ["벌레", "강철"], "epithet": "필요한 순간을 꿰뚫는 장인", "emoji": "🔧",
        "feature": "강철처럼 단단한 붉은 몸과 큰 집게를 지닌 포켓몬이다. 날개를 움직여 체온을 조절한다.",
        "reasons": [
            "직접 관찰하고 손으로 해결하는 그대의 기질을 핫삼의 정밀한 모습에 빗대었소.",
            "필요한 순간에 집중하는 침착함이 간결한 행동의 이미지와 맞닿아 있소.",
            "복잡한 문제를 실용적으로 풀어 갈 벗이라 하겠소.",
        ],
    },
    "ISFP": {
        "ko": "루브도", "en": "Smeargle", "number": "235", "slug": "smeargle",
        "types": ["노말"], "epithet": "일상의 여백을 물들이는 화공", "emoji": "🎨",
        "feature": "꼬리 끝에서 나오는 액체로 표시를 남기는 포켓몬이다. 붓을 연상시키는 꼬리가 특징이다.",
        "reasons": [
            "자신만의 감각으로 세계를 표현하는 그대에게, 루브도는 개성의 좋은 비유가 되오.",
            "일상의 작은 아름다움을 발견하는 섬세함이 붓을 든 모습과 어우러지오.",
            "정해진 틀보다 각자의 색을 존중할 벗이라 하겠소.",
        ],
    },
    "ESTP": {
        "ko": "개굴닌자", "en": "Greninja", "number": "658", "slug": "greninja",
        "types": ["물", "악"], "epithet": "순간의 흐름을 타는 유랑객", "emoji": "🥷",
        "feature": "닌자를 연상시키는 민첩한 포켓몬이다. 물을 압축하여 수리검 모양으로 만들어 사용한다.",
        "reasons": [
            "기회를 읽고 곧바로 행동하는 그대의 순발력을 개굴닌자의 민첩함에 빗대었소.",
            "변화하는 상황을 즐기는 기질이 유연한 움직임의 이미지와 상응하오.",
            "생생한 경험 속에서 길을 함께 개척할 벗이라 하겠소.",
        ],
    },
    "ESFP": {
        "ko": "로파파", "en": "Ludicolo", "number": "272", "slug": "ludicolo",
        "types": ["물", "풀"], "epithet": "현재의 기쁨을 노래하는 악사", "emoji": "💃",
        "feature": "흥겨운 리듬에 맞춰 춤을 추면 활력이 솟는 포켓몬이다. 넓은 잎 모양의 머리가 특징이다.",
        "reasons": [
            "지금의 즐거움을 주변과 나누는 그대에게, 로파파의 춤은 좋은 비유가 되오.",
            "새로운 경험과 사람을 반기는 활력이 흥겨운 리듬과 어우러지오.",
            "평범한 순간도 추억으로 빚어 갈 벗이라 하겠소.",
        ],
    },
}

CSS = """
<style>
:root { color-scheme: light; }
.stApp { background: #f6efdc; color: #3c3023; }
[data-testid="stHeader"] { background: rgba(246,239,220,.92); }
[data-testid="stMainBlockContainer"] { max-width: 1040px; padding-top: 3rem; padding-bottom: 3rem; }
.stApp, .stApp p, .stApp label, .stApp button, .stApp input {
    font-family: "Batang", "바탕", "Noto Serif KR", "Georgia", serif;
}
.stApp p, .stApp label { font-size: 19px; line-height: 1.9; color: #3c3023; }
.stApp h1, .stApp h2, .stApp h3 { font-family: "Batang", "바탕", "Georgia", serif; color: #3c3023; }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-color: #c9b991 !important; border-radius: 5px; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #fcf8ed; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #fffbee; border-color: #baa576; border-radius: 3px; min-height: 58px; color: #3c3023;
}
[data-testid="stSelectbox"] [data-baseweb="select"] * { font-size: 19px; }
[data-testid="stButton"] button {
    border-radius: 3px; min-height: 54px; border: 1px solid #9a7735;
    color: #493617; background: #f1dc9b; letter-spacing: .04em;
}
[data-testid="stButton"] button:hover { border-color: #7e5d23; color: #302315; background: #e7cd80; }
[data-testid="stButton"] button[kind="primary"] { background: #705324; color: #fff8e7; }
[data-testid="stButton"] button[kind="primary"] p { color: #fff8e7; }
[data-testid="stButton"] button:focus-visible { outline: 3px solid #a9863b; outline-offset: 3px; }
[data-testid="stImage"] img { object-fit: contain; }
.masthead { border-top: 4px double #a98a4b; border-bottom: 1px solid #bca575; padding: 24px 0 26px; margin-bottom: 22px; text-align: center; }
.catalogue { font: 13px/1.5 Georgia, serif; letter-spacing: .22em; color: #7a643e; }
.masthead h1 { font-size: clamp(32px, 5vw, 49px); font-weight: 500; margin: 18px 0 14px; letter-spacing: -.035em; }
.masthead .subtitle { color: #685638; font-size: 19px; margin: 0; }
.chapter { font-size: 14px; letter-spacing: .1em; color: #846a3c; margin: 0 0 8px; }
.section-title { font-size: 25px; font-weight: 500; margin: 0 0 12px; }
.prose { color: #594930; font-size: 19px; }
.glossary { border-top: 1px solid #d2c29f; padding-top: 12px; margin-top: 12px; }
.axis { display: flex; gap: 16px; border-bottom: 1px dotted #d6c8a8; padding: 8px 0; }
.axis b { color: #725624; min-width: 50px; font-family: Georgia, serif; font-size: 18px; }
.axis span { color: #6f5e43; font-size: 17px; }
.empty-page { padding: 38px 20px; text-align: center; border: 1px dashed #c7b58d; margin: 24px 0; }
.ornament { font-size: 35px; color: #a27d35; letter-spacing: .3em; }
.empty-page h2 { font-size: 27px; font-weight: 500; margin: 12px 0; }
.empty-page p { color: #756244; font-size: 18px; }
.discovery { text-align: center; padding: 24px 12px 20px; border-top: 3px double #ac8b46; margin-top: 25px; }
.discovery p { color: #796039; margin: 5px 0; }
.discovery h2 { font-size: 32px; font-weight: 500; margin: 8px 0; }
.plate { font: 14px/1.5 Georgia, serif; letter-spacing: .13em; color: #856b3e; }
.pokemon-name { font-size: 36px; font-weight: 500; margin: 4px 0; }
.english-name { font: italic 20px Georgia, serif; color: #806a43; margin-bottom: 14px; }
.type-badge { display: inline-block; padding: 3px 14px; margin: 0 8px 12px 0; border: 1px solid #c3ac75; background: #f5e9bd; font-size: 17px; border-radius: 30px; }
.entry-label { margin-top: 20px; color: #856c3f; font-size: 15px; letter-spacing: .04em; }
.entry-text { font-size: 19px; line-height: 1.9; color: #403527; }
.epithet { font-size: 19px; color: #755b31; margin: 10px 0 16px; font-style: italic; }
.rationale { margin: 20px 0 14px; padding: 20px 24px; border-left: 3px solid #b89650; background: #f7efda; }
.rationale h3 { margin: 0 0 12px; font-size: 22px; font-weight: 500; }
.rationale p { margin: 7px 0; font-size: 19px; }
.source-link { font-size: 16px; color: #725729; text-underline-offset: 4px; }
.image-fallback { text-align: center; font-size: 100px; padding: 35px 0; }
.colophon { border-top: 1px solid #baa575; margin-top: 30px; padding: 17px 8px; text-align: center; }
.colophon p { color: #79674b; font-size: 14px; margin: 5px 0; line-height: 1.8; }
.mbti-celebration-layer { position: fixed; inset: 0; pointer-events: none; overflow: hidden; z-index: 99999; }
.mbti-gold-piece { position: absolute; top: -30px; color: #af8632; opacity: 0; animation: gold-descent 4s ease-out forwards; }
@keyframes gold-descent {
    0% { opacity: 0; transform: translate(0,-20px) rotate(0deg); }
    12% { opacity: .9; }
    85% { opacity: .65; }
    100% { opacity: 0; transform: translate(var(--drift),100vh) rotate(var(--turn)); }
}
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] { padding: 1.5rem 1rem; }
    .masthead { padding-top: 18px; }
    .masthead .subtitle { font-size: 17px; }
    .rationale { padding: 18px; }
    .pokemon-name { font-size: 31px; }
}
@media (prefers-reduced-motion: reduce) { .mbti-gold-piece { animation: none; } }
</style>
"""


@st.cache_data(ttl=86400, max_entries=32, show_spinner=False)
def fetch_image(number: str) -> bytes:
    """공식 이미지를 하루 동안 캐시합니다. 실패한 요청은 캐시하지 않습니다."""
    request = Request(IMAGE_BASE + number + ".png", headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=8) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000 or not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("공식 이미지 형식을 확인할 수 없습니다.")
    return data


def clear_result() -> None:
    st.session_state["matched_type"] = None


def reset_selection() -> None:
    st.session_state["selected_type"] = None
    clear_result()


def celebrate(serial: int) -> None:
    """금빛 종잇조각 효과. 외부 JavaScript나 추가 패키지가 필요하지 않습니다."""
    # 이 문자열에는 앱 작성자가 정의한 코드와 정수만 들어갑니다.
    markup = """
    <div id="companion-celebration-__SERIAL__" class="mbti-celebration-layer" aria-hidden="true"></div>
    <script>
    (() => {
        const layer = document.getElementById('companion-celebration-__SERIAL__');
        if (!layer) return;
        document.querySelectorAll('.mbti-celebration-layer').forEach(old => {
            if (old !== layer) old.remove();
        });
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            layer.remove();
            return;
        }
        for (let i = 0; i < 42; i++) {
            const piece = document.createElement('span');
            piece.className = 'mbti-gold-piece';
            piece.textContent = ['✦', '◆', '·'][i % 3];
            piece.style.left = (Math.random() * 100) + '%';
            piece.style.fontSize = (12 + Math.random() * 14) + 'px';
            piece.style.animationDelay = (Math.random() * .7) + 's';
            piece.style.setProperty('--drift', (Math.random() * 180 - 90) + 'px');
            piece.style.setProperty('--turn', (Math.random() * 500 - 250) + 'deg');
            layer.appendChild(piece);
        }
        window.setTimeout(() => layer.remove(), 5000);
    })();
    </script>
    """.replace("__SERIAL__", str(serial))
    st.html(markup, unsafe_allow_javascript=True)


def render_companion(mbti: str) -> None:
    pokemon = POKEMON[mbti]
    st.html(f"""
    <section class="discovery">
        <div class="chapter">第二章 · 인연의 발견</div>
        <h2>그대의 단짝을 찾았소.</h2>
        <p>{escape(mbti)}의 성정에 비추어, 한 벗을 동행록에 기록하오.</p>
    </section>
    """)

    with st.container(border=True):
        picture, description = st.columns([1, 1.5], gap="large")
        with picture:
            st.html(f'<p class="plate">NATIONAL POKÉDEX · No. {pokemon["number"]}</p>')
            try:
                with st.spinner("도감의 삽화를 펼치는 중이오…"):
                    image = fetch_image(pokemon["number"])
                st.image(image, width=280)
            except (URLError, HTTPException, OSError, ValueError):
                st.html(f'<div class="image-fallback" aria-hidden="true">{pokemon["emoji"]}</div>')
                st.caption("삽화를 불러오지 못했소. 아래 공식 도감 링크를 살펴보거나 잠시 뒤 다시 시도해 주시오.")
            st.html(f'<a class="source-link" href="{POKEDEX_BASE}{pokemon["slug"]}" target="_blank" rel="noopener noreferrer">삽화와 정보의 출처 · 공식 도감 ↗</a>')

        with description:
            badges = "".join(f'<span class="type-badge">{escape(t)}</span>' for t in pokemon["types"])
            st.html(f"""
            <h2 class="pokemon-name">{escape(pokemon['ko'])}</h2>
            <div class="english-name">({escape(pokemon['en'])})</div>
            <p class="epithet">“{escape(pokemon['epithet'])}”</p>
            <div aria-label="포켓몬 타입">{badges}</div>
            <div class="entry-label">도감의 관찰 · 특징</div>
            <p class="entry-text">{escape(pokemon['feature'])}</p>
            """)

        reasons = "".join(f"<p>{escape(reason)}</p>" for reason in pokemon["reasons"])
        st.html(f'<section class="rationale"><h3>그대와 상응하는 까닭</h3>{reasons}</section>')
        st.button("다시 고르겠소", on_click=reset_selection, use_container_width=True)


def main() -> None:
    st.set_page_config(page_title="열여섯 성정의 동행록", page_icon="📜", layout="centered")
    st.html(CSS)
    st.session_state.setdefault("matched_type", None)
    st.session_state.setdefault("celebration_serial", 0)

    st.html("""
    <header class="masthead">
        <div class="catalogue">COMPANION ARCHIVE · VOLUME XVI</div>
        <h1>열여섯 성정의 동행록</h1>
        <p class="subtitle">그대의 기질을 비추어, 포켓몬 한 벗과의 인연을 청하오.</p>
    </header>
    """)

    selection, preface = st.columns([1.15, 1], gap="large")
    with selection:
        with st.container(border=True):
            st.html('<p class="chapter">第一章 · 성정의 선택</p><h2 class="section-title">그대는 어느 성정에 속하시오?</h2>')
            choice = st.selectbox(
                "나의 MBTI 유형",
                options=list(POKEMON),
                index=None,
                placeholder="열여섯 유형 중 하나를 고르시오",
                key="selected_type",
                on_change=clear_result,
            )
            found = st.button(
                "나의 단짝을 찾아보겠소",
                type="primary",
                disabled=choice is None,
                use_container_width=True,
            )

    with preface:
        st.html("""
        <p class="chapter">序文 · 읽는 이에게</p>
        <p class="prose">성정(性情)이란 마음의 바탕과 그 드러남을 이르는 말이오.
        여기서는 MBTI를 빌려 포켓몬의 모습과 기질을 비유적으로 연결하였소.</p>
        <div class="glossary">
            <div class="axis"><b>E · I</b><span>외향과 내향</span></div>
            <div class="axis"><b>S · N</b><span>감각과 직관</span></div>
            <div class="axis"><b>T · F</b><span>사고와 감정</span></div>
            <div class="axis"><b>J · P</b><span>판단과 인식</span></div>
        </div>
        """)

    if found and choice:
        st.session_state["matched_type"] = choice
        st.session_state["celebration_serial"] += 1

    matched_type = st.session_state["matched_type"]
    if matched_type:
        render_companion(matched_type)
        if found:
            celebrate(st.session_state["celebration_serial"])
    else:
        st.html("""
        <section class="empty-page">
            <div class="ornament" aria-hidden="true">❧ ✦ ❧</div>
            <h2>동행록의 한 장이 아직 비어 있소.</h2>
            <p>유형을 고르고 ‘나의 단짝을 찾아보겠소’를 누르면,<br>
            그대와 어울리는 포켓몬의 이름과 삽화, 그리고 인연의 까닭이 드러나오.</p>
        </section>
        """)

    st.html("""
    <footer class="colophon">
        <p>프로그래밍 수행평가를 위한 비공식 수업용 실습 · 단짝 대응과 해석은 재미를 위한 창작이오.</p>
        <p>성격을 확정하는 진단이나 공식 MBTI 분류가 아니오. 도감 정보는 포켓몬의 기본 형태를 기준으로 하였소.</p>
        <p>이미지 출처: Pokémon 공식 사이트 · © Pokémon. © Nintendo / Creatures Inc. / GAME FREAK inc.</p>
    </footer>
    """)


if __name__ == "__main__":
    main()
