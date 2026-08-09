"""
styles.py
هوية التصميم الملكي: الألوان، الخطوط، البطاقات، وخلفية الجمرات الذهبية المتحركة.
كل شي هنا نصوص (CSS/HTML) يتم حقنها بالصفحة عن طريق st.markdown.
"""

import random

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,500&family=Aref+Ruqaa:wght@400;700&family=Tajawal:wght@300;400;500;700&display=swap');

:root {
    --emerald-deep: #0b3d2e;
    --obsidian: #06110d;
    --burgundy: #5c1a2b;
    --gold: #c9a227;
    --gold-light: #e8c766;
    --ivory: #f5efe0;
}

/* ============ إعدادات عامة ============ */
html, body, [class*="css"] {
    direction: rtl;
    font-family: 'Tajawal', sans-serif;
}

.stApp {
    background: radial-gradient(ellipse at top, #0f4a37 0%, var(--emerald-deep) 45%, var(--obsidian) 100%);
    color: var(--ivory);
}

#MainMenu, footer, header { display: none !important; }

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

/* ============ خلفية الجمرات الذهبية المتحركة ============ */
.ember-container {
    position: fixed;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
    z-index: 0;
}
.ember {
    position: absolute;
    bottom: -20px;
    border-radius: 50%;
    background: radial-gradient(circle, var(--gold-light) 0%, var(--gold) 55%, transparent 75%);
    box-shadow: 0 0 8px 2px rgba(201, 162, 39, 0.55);
    opacity: 0;
    animation-name: rise;
    animation-timing-function: ease-in-out;
    animation-iteration-count: infinite;
}
@keyframes rise {
    0%   { transform: translate(0, 0); opacity: 0; }
    12%  { opacity: 0.9; }
    50%  { transform: translate(var(--drift), -55vh); }
    88%  { opacity: 0.5; }
    100% { transform: translate(calc(var(--drift) * -1), -110vh); opacity: 0; }
}

/* ============ الفواصل الملكية ============ */
.royal-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin: 2.2rem 0 1.6rem 0;
    position: relative;
    z-index: 1;
}
.royal-divider span {
    height: 1px;
    width: 90px;
    background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.royal-divider i {
    color: var(--gold);
    font-style: normal;
    font-size: 1.1rem;
    transform: rotate(45deg);
    display: inline-block;
}
.category-divider { gap: 1.2rem; }
.category-title {
    font-family: 'Aref Ruqaa', serif;
    color: var(--gold-light);
    font-size: 1.9rem;
    font-weight: 700;
    margin: 0;
    white-space: nowrap;
}

/* ============ الهيرو ============ */
.hero {
    text-align: center;
    position: relative;
    z-index: 1;
    padding-top: 1rem;
}
.hero-crown { font-size: 2.2rem; margin-bottom: 0.3rem; }
.hero-title {
    font-family: 'Aref Ruqaa', 'Cinzel', serif;
    font-size: 3.2rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(180deg, var(--gold-light) 20%, var(--gold) 80%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 2px 25px rgba(201, 162, 39, 0.25);
}
.hero-tagline {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    color: var(--ivory);
    opacity: 0.85;
    font-size: 1.25rem;
    margin-top: 0.4rem;
}

/* ============ حالة القائمة الفارغة ============ */
.empty-state {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.4rem;
    color: var(--gold-light);
    opacity: 0.85;
    padding: 3rem 1rem;
    position: relative;
    z-index: 1;
}

/* ============ شبكة الأطباق ============ */
.menu-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 1.4rem;
    position: relative;
    z-index: 1;
    margin-bottom: 1rem;
}
.menu-card {
    background: rgba(11, 61, 46, 0.45);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(201, 162, 39, 0.35);
    border-radius: 14px;
    overflow: hidden;
    position: relative;
    transition: transform 0.35s ease, box-shadow 0.35s ease, border-color 0.35s ease;
}
.menu-card:hover {
    transform: translateY(-6px) scale(1.015);
    box-shadow: 0 12px 30px rgba(0,0,0,0.4), 0 0 20px rgba(201,162,39,0.25);
    border-color: var(--gold-light);
}
.menu-card.unavailable { opacity: 0.6; filter: grayscale(0.35); }
.item-img {
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
    display: block;
}
.item-img.placeholder {
    width: 100%;
    aspect-ratio: 1 / 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    background: rgba(6, 17, 13, 0.5);
}
.price-medallion {
    position: absolute;
    top: 10px;
    left: 10px;
    background: linear-gradient(160deg, var(--gold-light), var(--gold));
    color: var(--obsidian);
    font-weight: 700;
    font-size: 0.82rem;
    border-radius: 50%;
    width: 58px;
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.4);
    line-height: 1.05;
    padding: 4px;
}
.availability-ribbon {
    position: absolute;
    top: 12px;
    right: -34px;
    background: var(--burgundy);
    color: var(--ivory);
    font-size: 0.72rem;
    padding: 4px 40px;
    transform: rotate(-45deg);
    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}
.card-body { padding: 0.9rem 1rem 1.1rem; }
.item-name {
    font-family: 'Aref Ruqaa', serif;
    color: var(--gold-light);
    font-size: 1.25rem;
    margin: 0 0 0.3rem 0;
}
.item-desc {
    font-family: 'Tajawal', sans-serif;
    font-weight: 300;
    font-size: 0.9rem;
    color: var(--ivory);
    opacity: 0.8;
    margin: 0;
    line-height: 1.5;
}

/* ============ التذييل ============ */
.royal-footer {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    color: var(--gold);
    opacity: 0.55;
    margin-top: 2.5rem;
    font-size: 1rem;
    position: relative;
    z-index: 1;
}

/* ============ بوابة الإشراف ============ */
.admin-gate {
    text-align: center;
    padding-top: 2.5rem;
    position: relative;
    z-index: 1;
}
.gate-icon { font-size: 2.4rem; margin-bottom: 0.5rem; }
.gate-title {
    font-family: 'Aref Ruqaa', serif;
    color: var(--gold-light);
    font-size: 2.2rem;
    margin: 0;
}
.gate-sub {
    font-family: 'Cormorant Garamond', serif;
    color: var(--ivory);
    opacity: 0.75;
    margin-top: 0.3rem;
}
.shake-error {
    text-align: center;
    color: #e07a7a;
    background: rgba(92, 26, 43, 0.35);
    border: 1px solid rgba(224, 122, 122, 0.4);
    border-radius: 8px;
    padding: 0.6rem;
    margin-top: 0.8rem;
    animation: shake 0.4s ease;
}
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-6px); }
    75% { transform: translateX(6px); }
}

/* ============ لوحة الإشراف ============ */
.dash-title {
    font-family: 'Aref Ruqaa', serif;
    color: var(--gold-light);
    font-size: 2rem;
    margin: 0;
}
.tab-hint {
    color: var(--ivory);
    opacity: 0.7;
    font-size: 0.9rem;
    margin-bottom: 0.8rem;
}
.no-img {
    aspect-ratio: 1/1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.2rem;
    background: rgba(6,17,13,0.5);
    border-radius: 10px;
}

/* ============ أزرار Streamlit ============ */
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(160deg, var(--gold-light), var(--gold));
    color: var(--obsidian) !important;
    font-family: 'Tajawal', sans-serif;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    letter-spacing: 0.3px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(201,162,39,0.35);
}

/* الزر المخفي (الجوهرة) */
.st-key-hidden_gem_btn button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--gold) !important;
    opacity: 0.16;
    font-size: 0.75rem;
    padding: 0 !important;
    min-height: unset !important;
    transition: opacity 0.4s ease;
}
.st-key-hidden_gem_btn button:hover {
    opacity: 0.55;
    transform: none;
    box-shadow: none !important;
}
.st-key-back_to_menu_btn button, .st-key-logout_btn button {
    background: transparent !important;
    border: 1px solid rgba(201,162,39,0.4) !important;
    color: var(--gold-light) !important;
}

/* ============ حقول الإدخال ============ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background: rgba(6, 17, 13, 0.45) !important;
    color: var(--ivory) !important;
    border: 1px solid rgba(201,162,39,0.3) !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: rgba(6, 17, 13, 0.45) !important;
    border-radius: 8px !important;
}

/* ============ ظهور تدريجي عند التحميل ============ */
.fade-in-up {
    animation: fadeInUp 0.75s ease both;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ============ الاستجابة للشاشات الصغيرة ============ */
@media (max-width: 640px) {
    .hero-title { font-size: 2.2rem; }
    .menu-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.9rem; }
    .category-title { font-size: 1.4rem; }
}

/* ============ احترام تفضيل تقليل الحركة ============ */
@media (prefers-reduced-motion: reduce) {
    .ember { animation: none !important; opacity: 0.25 !important; }
    .menu-card, .stButton > button { transition: none !important; }
    .fade-in-up { animation: none !important; }
}
</style>
"""


def get_base_css() -> str:
    """يرجّع كود الـ CSS الكامل، يُحقن بالصفحة مرة وحدة عند بدء التطبيق."""
    return _CSS


def render_embers(count: int = 45) -> str:
    """يبني خلفية من جمرات ذهبية متحركة تصعد ببطء وراء المحتوى (بدون أي جافاسكربت،
    فقط CSS خالص حتى تشتغل بثبات داخل Streamlit)."""
    pieces = []
    for _ in range(count):
        left = round(random.uniform(0, 100), 2)
        size = round(random.uniform(2, 6), 1)
        duration = round(random.uniform(9, 22), 1)
        delay = round(random.uniform(0, 18), 1)
        drift = round(random.uniform(-40, 40), 1)
        pieces.append(
            f'<div class="ember" style="left:{left}%; width:{size}px; height:{size}px; '
            f'animation-duration:{duration}s; animation-delay:{delay}s; --drift:{drift}px;"></div>'
        )
    return '<div class="ember-container">' + "".join(pieces) + "</div>"
