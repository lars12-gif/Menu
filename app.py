"""
app.py
الموقع الملكي للمنيو — صفحة عرض للزبائن + لوحة إشراف مخفية محمية بكلمة سر.
"""

import base64
import os
import uuid
from pathlib import Path

import streamlit as st
from PIL import Image

import db
import styles

# =====================================================================
# إعدادات عامة — غيّرها حسب مطعمك
# =====================================================================
RESTAURANT_NAME = "قائمتنا الملكية"
RESTAURANT_TAGLINE = "نكهات فاخرة، بلمسة ملكية"
CURRENCY = "د.ع"
IMAGES_DIR = "images"
# =====================================================================


# ---------------------------------------------------------------------------
# إعداد الصفحة (يجب أن يكون أول أمر Streamlit في الملف)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=RESTAURANT_NAME,
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

os.makedirs(IMAGES_DIR, exist_ok=True)
db.init_db()

# حقن التصميم + خلفية الجمرات الذهبية (تُبنى مرة وحدة لكل جلسة حتى ما "تقفز")
st.markdown(styles.get_base_css(), unsafe_allow_html=True)
if "embers_html" not in st.session_state:
    st.session_state.embers_html = styles.render_embers()
st.markdown(st.session_state.embers_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# حالة الجلسة
# ---------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "menu"
if "admin_authed" not in st.session_state:
    st.session_state.admin_authed = False


# ---------------------------------------------------------------------------
# أدوات مساعدة
# ---------------------------------------------------------------------------
def save_uploaded_image(uploaded_file) -> str:
    """يحفظ صورة مرفوعة كمربع موحّد الحجم (600×600) ويرجّع مسارها."""
    if uploaded_file is None:
        return ""
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        ext = ".png"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(IMAGES_DIR, filename)

    image = Image.open(uploaded_file).convert("RGB")
    w, h = image.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    image = image.crop((left, top, left + side, top + side)).resize((600, 600))
    image.save(path, quality=88)
    return path


def image_to_data_uri(path: str):
    """يحوّل صورة محفوظة محلياً إلى data-uri حتى نقدر نعرضها داخل HTML مخصص."""
    if not path or not os.path.exists(path):
        return None
    ext = Path(path).suffix.lstrip(".").lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{b64}"


def format_price(price: float) -> str:
    return f"{price:,.0f}".replace(",", "٬")


# ---------------------------------------------------------------------------
# صفحة المنيو (الزبائن)
# ---------------------------------------------------------------------------
def render_menu():
    st.markdown(
        f"""
        <div class="hero fade-in-up">
            <div class="hero-crown">👑</div>
            <h1 class="hero-title">{RESTAURANT_NAME}</h1>
            <p class="hero-tagline">{RESTAURANT_TAGLINE}</p>
            <div class="royal-divider"><span></span><i>♦</i><span></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    categories = db.get_categories()
    any_items = False

    for cat in categories:
        items = db.get_items(category_id=cat["id"])
        if not items:
            continue
        any_items = True

        st.markdown(
            f"""
            <div class="royal-divider category-divider fade-in-up">
                <span></span><h2 class="category-title">{cat['name']}</h2><span></span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        cards = ['<div class="menu-grid">']
        for item in items:
            uri = image_to_data_uri(item["image_path"])
            if uri:
                img_html = f'<img class="item-img" src="{uri}" alt="{item["name"]}">'
            else:
                img_html = '<div class="item-img placeholder">🍽️</div>'

            ribbon = "" if item["available"] else '<div class="availability-ribbon">غير متوفرة</div>'
            card_class = "menu-card fade-in-up" + ("" if item["available"] else " unavailable")
            description = item["description"] or ""

            cards.append(
                f"""
                <div class="{card_class}">
                    {img_html}
                    <div class="price-medallion">{format_price(item['price'])}<br>{CURRENCY}</div>
                    {ribbon}
                    <div class="card-body">
                        <h3 class="item-name">{item['name']}</h3>
                        <p class="item-desc">{description}</p>
                    </div>
                </div>
                """
            )
        cards.append("</div>")
        st.markdown("".join(cards), unsafe_allow_html=True)

    if not any_items:
        st.markdown(
            '<div class="empty-state fade-in-up">نُجهّز لكم أشهى الأطباق… عودوا قريباً ✨</div>',
            unsafe_allow_html=True,
        )

    render_footer()


def render_footer():
    st.markdown('<div class="royal-footer">— نتشرف بزيارتكم —</div>', unsafe_allow_html=True)
    _, mid, _ = st.columns([10, 1, 10])
    with mid:
        if st.button("♦", key="hidden_gem_btn"):
            st.session_state.page = "admin_login"
            st.rerun()


# ---------------------------------------------------------------------------
# بوابة دخول الإشراف
# ---------------------------------------------------------------------------
def render_admin_login():
    st.markdown(
        """
        <div class="admin-gate fade-in-up">
            <div class="gate-icon">🔐</div>
            <h1 class="gate-title">الغرفة الملكية</h1>
            <p class="gate-sub">أدخل كلمة السر للمتابعة</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, mid, _ = st.columns([1, 1.3, 1])
    with mid:
        with st.form("login_form"):
            pwd = st.text_input(
                "كلمة السر", type="password", label_visibility="collapsed", placeholder="كلمة السر"
            )
            submitted = st.form_submit_button("دخول 👑", use_container_width=True)

        if submitted:
            try:
                correct_password = st.secrets["admin_password"]
            except Exception:
                st.error(
                    "لم يتم ضبط كلمة سر الإشراف بعد. أضِف admin_password داخل ملف "
                    ".streamlit/secrets.toml (راجع README)."
                )
                correct_password = None

            if correct_password is not None:
                if pwd == correct_password:
                    st.session_state.admin_authed = True
                    st.session_state.page = "admin_dashboard"
                    st.rerun()
                else:
                    st.markdown(
                        '<div class="shake-error">كلمة السر غير صحيحة ✗</div>',
                        unsafe_allow_html=True,
                    )

        if st.button("⟵ الرجوع إلى القائمة", key="back_to_menu_btn", use_container_width=True):
            st.session_state.page = "menu"
            st.rerun()


# ---------------------------------------------------------------------------
# لوحة الإشراف
# ---------------------------------------------------------------------------
def render_admin_dashboard():
    if not st.session_state.get("admin_authed"):
        st.session_state.page = "admin_login"
        st.rerun()
        return

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown('<h1 class="dash-title">👑 لوحة الإشراف</h1>', unsafe_allow_html=True)
    with top_r:
        if st.button("🚪 خروج", key="logout_btn", use_container_width=True):
            st.session_state.admin_authed = False
            st.session_state.page = "menu"
            st.rerun()

    tab_add_cat, tab_add_item, tab_manage_items, tab_manage_cats = st.tabs(
        ["➕ إضافة صنف", "🍽️ إضافة أكلة", "📋 إدارة الأطعمة", "🗂️ إدارة الأصناف"]
    )

    with tab_add_cat:
        render_add_category_tab()
    with tab_add_item:
        render_add_item_tab()
    with tab_manage_items:
        render_manage_items_tab()
    with tab_manage_cats:
        render_manage_categories_tab()


def render_add_category_tab():
    st.markdown(
        '<p class="tab-hint">أضف صنفاً جديداً (مثال: مقبلات، أطباق رئيسية، حلويات، مشروبات)</p>',
        unsafe_allow_html=True,
    )
    with st.form("add_cat_form", clear_on_submit=True):
        name = st.text_input("اسم الصنف")
        submitted = st.form_submit_button("إضافة الصنف")

    if submitted:
        ok, msg = db.add_category(name)
        st.success(msg) if ok else st.error(msg)
        if ok:
            st.rerun()

    cats = db.get_categories()
    if cats:
        st.markdown("**الأصناف الحالية:** " + "، ".join(c["name"] for c in cats))


def render_add_item_tab():
    cats = db.get_categories()
    if not cats:
        st.warning("أضف صنفاً واحداً على الأقل من تبويب «إضافة صنف» قبل ما تضيف أطعمة.")
        return

    cat_names = [c["name"] for c in cats]
    with st.form("add_item_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("اسم الأكلة")
            price = st.number_input(f"السعر ({CURRENCY})", min_value=0.0, step=250.0, format="%.0f")
        with col2:
            category_name = st.selectbox("الصنف", cat_names)
            available = st.toggle("متوفرة حالياً", value=True)
        description = st.text_area("الوصف / البايو", placeholder="وصف مختصر وشهي عن الطبق...")
        image = st.file_uploader("صورة الطبق", type=["png", "jpg", "jpeg", "webp"])
        submitted = st.form_submit_button("إضافة الأكلة 🍽️")

    if submitted:
        if not name.strip():
            st.error("لازم تدخل اسم الأكلة")
            return
        category_id = next(c["id"] for c in cats if c["name"] == category_name)
        image_path = save_uploaded_image(image) if image else ""
        db.add_item(name, price, description, image_path, available, category_id)
        st.success(f"تمت إضافة «{name}» بنجاح")
        st.balloons()


def render_manage_items_tab():
    cats = db.get_categories()
    if not cats:
        st.info("ما أكو أصناف بعد.")
        return

    filter_options = ["الكل"] + [c["name"] for c in cats]
    filter_choice = st.selectbox("فلترة حسب الصنف", filter_options, key="manage_filter")

    if filter_choice == "الكل":
        items = db.get_items()
    else:
        cat_id = next(c["id"] for c in cats if c["name"] == filter_choice)
        items = db.get_items(category_id=cat_id)

    if not items:
        st.info("لا توجد أطعمة بهذا الصنف.")
        return

    cat_names = [c["name"] for c in cats]

    for item in items:
        status = "🟢 متوفرة" if item["available"] else "🔴 غير متوفرة"
        with st.expander(f"{item['name']} — {status}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                if item["image_path"] and os.path.exists(item["image_path"]):
                    st.image(item["image_path"], use_container_width=True)
                else:
                    st.markdown('<div class="no-img">🍽️</div>', unsafe_allow_html=True)
                new_image = st.file_uploader(
                    "تغيير الصورة (اختياري)",
                    type=["png", "jpg", "jpeg", "webp"],
                    key=f"img_{item['id']}",
                )
            with col2:
                new_name = st.text_input("الاسم", value=item["name"], key=f"name_{item['id']}")
                new_price = st.number_input(
                    f"السعر ({CURRENCY})",
                    value=float(item["price"]),
                    min_value=0.0,
                    step=250.0,
                    format="%.0f",
                    key=f"price_{item['id']}",
                )
                current_cat = next(
                    (c["name"] for c in cats if c["id"] == item["category_id"]), cat_names[0]
                )
                new_cat = st.selectbox(
                    "الصنف", cat_names, index=cat_names.index(current_cat), key=f"cat_{item['id']}"
                )
                new_available = st.toggle(
                    "متوفرة حالياً", value=bool(item["available"]), key=f"avail_{item['id']}"
                )
                new_desc = st.text_area("الوصف", value=item["description"], key=f"desc_{item['id']}")

            b1, b2 = st.columns(2)
            with b1:
                if st.button("💾 حفظ التعديلات", key=f"save_{item['id']}", use_container_width=True):
                    new_cat_id = next(c["id"] for c in cats if c["name"] == new_cat)
                    image_path = save_uploaded_image(new_image) if new_image else item["image_path"]
                    db.update_item(
                        item["id"], new_name, new_price, new_desc, image_path, new_available, new_cat_id
                    )
                    st.success("تم الحفظ")
                    st.rerun()
            with b2:
                confirm_key = f"confirm_del_{item['id']}"
                if st.session_state.get(confirm_key):
                    if st.button(
                        "⚠️ تأكيد الحذف نهائياً", key=f"del_confirm_{item['id']}", use_container_width=True
                    ):
                        db.delete_item(item["id"])
                        st.session_state.pop(confirm_key, None)
                        st.success("تم الحذف")
                        st.rerun()
                else:
                    if st.button("🗑️ حذف", key=f"del_{item['id']}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()


def render_manage_categories_tab():
    cats = db.get_categories()
    if not cats:
        st.info("ما أكو أصناف بعد.")
        return

    for cat in cats:
        item_count = len(db.get_items(category_id=cat["id"]))
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{cat['name']}** — {item_count} صنف طعام")
        with col2:
            if st.button("🗑️ حذف", key=f"del_cat_{cat['id']}", use_container_width=True):
                ok, msg = db.delete_category(cat["id"])
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.rerun()


# ---------------------------------------------------------------------------
# الموجّه الرئيسي
# ---------------------------------------------------------------------------
def main():
    if st.session_state.page == "admin_dashboard":
        render_admin_dashboard()
    elif st.session_state.page == "admin_login":
        render_admin_login()
    else:
        render_menu()


main()
