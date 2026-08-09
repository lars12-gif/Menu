import streamlit as st
import sqlite3
import os
import base64
from PIL import Image
import io
from pathlib import Path

# ======================= إعداد الصفحة =======================
st.set_page_config(page_title="منيو المطعم", page_icon="🍽️", layout="wide")

# ======================= إنشاء المجلدات =======================
if not os.path.exists("images"):
    os.makedirs("images")

# ======================= قاعدة البيانات =======================
conn = sqlite3.connect("menu.db", check_same_thread=False)
c = conn.cursor()

# إنشاء الجداول إذا لم تكن موجودة
c.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS menu_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        image_path TEXT,
        available BOOLEAN DEFAULT 1,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
''')
conn.commit()

# ======================= دوال مساعدة =======================
def get_categories():
    c.execute("SELECT * FROM categories")
    return c.fetchall()

def add_category(name):
    c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()

def delete_category(cat_id):
    # حذف الأطباق المرتبطة بالتصنيف
    c.execute("DELETE FROM menu_items WHERE category_id=?", (cat_id,))
    c.execute("DELETE FROM categories WHERE id=?", (cat_id,))
    conn.commit()

def get_items(category_id=None):
    if category_id and category_id != "الكل":
        c.execute("""
            SELECT menu_items.*, categories.name as cat_name 
            FROM menu_items 
            JOIN categories ON menu_items.category_id = categories.id 
            WHERE category_id=?
        """, (category_id,))
    else:
        c.execute("""
            SELECT menu_items.*, categories.name as cat_name 
            FROM menu_items 
            JOIN categories ON menu_items.category_id = categories.id
        """)
    return c.fetchall()

def add_item(name, price, description, image_path, available, category_id):
    c.execute("INSERT INTO menu_items (name, price, description, image_path, available, category_id) VALUES (?,?,?,?,?,?)",
              (name, price, description, image_path, available, category_id))
    conn.commit()

def update_item(item_id, name, price, description, image_path, available, category_id):
    c.execute("UPDATE menu_items SET name=?, price=?, description=?, image_path=?, available=?, category_id=? WHERE id=?",
              (name, price, description, image_path, available, category_id, item_id))
    conn.commit()

def delete_item(item_id):
    # حذف الصورة إذا كانت موجودة
    c.execute("SELECT image_path FROM menu_items WHERE id=?", (item_id,))
    row = c.fetchone()
    if row and row[0] and os.path.exists(row[0]):
        os.remove(row[0])
    c.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
    conn.commit()

def image_to_base64(image_path):
    """تحويل الصورة إلى base64 لاستخدامها في HTML"""
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_default_image_base64():
    """صورة افتراضية إذا لم توجد صورة للصنف"""
    # صورة بسيطة جدًا مدمجة بـ base64 (أيقونة طعام)
    # يمكنك استبدالها بمسار صورة افتراضية في مجلد images
    default = "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAACXBIWXMAAAsTAAALEwEAmpwYAAAB..."
    # سأضع صورة شفافة أو أيقونة بسيطة
    return ""

# ======================= الأنماط CSS =======================
def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');

    * {
        font-family: 'Tajawal', sans-serif;
    }

    body {
        direction: rtl;
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    .stApp {
        background: transparent;
    }

    /* الزر المخفي */
    .hidden-admin-btn {
        position: fixed;
        bottom: 10px;
        right: 10px;
        opacity: 0.15;
        transition: opacity 0.3s;
        background: #ffffff22;
        backdrop-filter: blur(10px);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        cursor: pointer;
        color: white;
        border: 1px solid #ffffff33;
        z-index: 999;
    }

    .hidden-admin-btn:hover {
        opacity: 1;
    }

    /* تصميم الكرت الزجاجي */
    .glass-card {
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        padding: 20px;
        transition: transform 0.3s, box-shadow 0.3s;
        color: white;
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .glass-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.4);
    }

    .glass-card img {
        width: 120px;
        height: 120px;
        object-fit: cover;
        border-radius: 50%;
        margin: 0 auto 15px;
        border: 3px solid rgba(255,255,255,0.3);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    .badge-available {
        background: #00c853;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 14px;
        display: inline-block;
        margin-top: 10px;
    }

    .badge-unavailable {
        background: #ff1744;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 14px;
        display: inline-block;
        margin-top: 10px;
    }

    .category-title {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(5px);
        padding: 8px 20px;
        border-radius: 30px;
        display: inline-block;
        margin: 20px 0 10px;
        font-weight: bold;
        font-size: 18px;
    }

    /* أزرار التصنيفات */
    .filter-btn {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        margin: 5px;
        cursor: pointer;
        transition: 0.3s;
        font-weight: bold;
    }

    .filter-btn:hover {
        background: rgba(255,255,255,0.25);
    }

    .filter-btn.active {
        background: #ff9800;
        border-color: #ff9800;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ======================= إدارة حالة التطبيق =======================
if "admin" not in st.session_state:
    st.session_state.admin = False

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "الكل"

# ======================= دوال عرض المنيو =======================
def show_menu():
    # زر مخفي (يؤدي إلى لوحة الإشراف)
    st.markdown("""
    <div class="hidden-admin-btn" title="لوحة الإشراف">
        ⚙️
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚙️", key="admin_btn_hidden", help="لوحة الإشراف"):
        st.session_state.admin = True
        st.rerun()

    st.markdown("<h1 style='text-align: center; color: white; margin-bottom: 30px;'>🍽️ منيو المطعم</h1>", unsafe_allow_html=True)

    # استدعاء التصنيفات للفلترة
    cats = get_categories()
    cat_options = ["الكل"] + [cat[1] for cat in cats]

    # عرض أزرار التصنيفات
    col_btn = st.columns(len(cat_options) + 1)
    for i, cat_name in enumerate(cat_options):
        with col_btn[i]:
            btn_class = "filter-btn active" if st.session_state.selected_category == cat_name else "filter-btn"
            if st.button(cat_name, key=f"cat_{i}", use_container_width=True):
                st.session_state.selected_category = cat_name
                st.rerun()

    # جلب الأطباق المطلوبة
    if st.session_state.selected_category == "الكل":
        items = get_items()
    else:
        # البحث عن id التصنيف
        cat_id = None
        for c in cats:
            if c[1] == st.session_state.selected_category:
                cat_id = c[0]
                break
        items = get_items(cat_id)

    if not items:
        st.info("لا توجد أطباق في هذا التصنيف حاليًا.")
        return

    # تجميع الأطباق حسب التصنيفات (للعرض مع العناوين)
    from collections import defaultdict
    grouped = defaultdict(list)
    for item in items:
        # item: (id, name, price, desc, img, available, cat_id, cat_name)
        grouped[item[7]].append(item)

    for cat_name, item_list in grouped.items():
        st.markdown(f"<div class='category-title'>{cat_name}</div>", unsafe_allow_html=True)

        # عرض في صفوف من 4 كروت
        n_cols = 4
        rows = [item_list[i:i+n_cols] for i in range(0, len(item_list), n_cols)]
        for row in rows:
            cols = st.columns(n_cols)
            for idx, item in enumerate(row):
                with cols[idx]:
                    item_id, name, price, desc, img_path, available, _, _ = item
                    img_b64 = image_to_base64(img_path) if img_path else None
                    if img_b64:
                        img_html = f'<img src="data:image/jpeg;base64,{img_b64}" alt="{name}">'
                    else:
                        # صورة افتراضية
                        img_html = f'<div style="width:120px;height:120px;border-radius:50%;background:#ffffff22;margin:0 auto 15px;display:flex;align-items:center;justify-content:center;font-size:30px;">🍲</div>'

                    badge = '<span class="badge-available">✅ متوفر</span>' if available else '<span class="badge-unavailable">❌ غير متوفر</span>'

                    card_html = f"""
                    <div class="glass-card">
                        {img_html}
                        <h3 style="margin:10px 0;">{name}</h3>
                        <p style="color:#ddd; font-size:14px;">{desc[:60] if desc else ''}</p>
                        <div style="font-size:20px; font-weight:bold; color:#FFD700;">{price} د.ع</div>
                        {badge}
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

# ======================= دوال لوحة الإشراف =======================
def admin_panel():
    st.markdown("<h1 style='color:white; text-align:center;'>🔧 لوحة الإشراف</h1>", unsafe_allow_html=True)

    # زر العودة
    if st.button("⬅️ العودة للصفحة الرئيسية"):
        st.session_state.admin = False
        st.rerun()

    tab1, tab2 = st.tabs(["📂 إدارة التصنيفات", "🍔 إدارة الأطباق"])

    # ================== تبويب التصنيفات ==================
    with tab1:
        st.subheader("إضافة تصنيف جديد")
        new_cat = st.text_input("اسم التصنيف", key="new_cat")
        if st.button("إضافة تصنيف", key="add_cat"):
            if new_cat.strip():
                # منع التكرار
                existing = [cat[1] for cat in get_categories()]
                if new_cat.strip() in existing:
                    st.warning("هذا التصنيف موجود مسبقًا.")
                else:
                    add_category(new_cat.strip())
                    st.success("تمت الإضافة.")
                    st.rerun()
            else:
                st.warning("الرجاء كتابة اسم للتصنيف.")

        st.subheader("التصنيفات الحالية")
        cats = get_categories()
        if cats:
            for cat in cats:
                col1, col2 = st.columns([4,1])
                with col1:
                    st.write(f"📌 {cat[1]}")
                with col2:
                    if st.button("حذف", key=f"del_cat_{cat[0]}"):
                        delete_category(cat[0])
                        st.success("تم حذف التصنيف مع أطباقه.")
                        st.rerun()
        else:
            st.info("لا توجد تصنيفات بعد.")

    # ================== تبويب الأطباق ==================
    with tab2:
        st.subheader("إضافة طبق جديد")
        with st.form("add_item_form", clear_on_submit=True):
            cats = get_categories()
            if not cats:
                st.warning("يرجى إضافة تصنيفات أولاً.")
                submitted = False
            else:
                cat_names = [cat[1] for cat in cats]
                selected_cat = st.selectbox("التصنيف", cat_names)
                name = st.text_input("اسم الطبق")
                price = st.number_input("السعر", min_value=0.0, step=100.0)
                desc = st.text_area("الوصف (البايو)")
                uploaded_img = st.file_uploader("صورة الطبق", type=["jpg", "jpeg", "png"])
                available = st.checkbox("متوفر", value=True)

                submitted = st.form_submit_button("إضافة الطبق")

            if submitted and cats:
                if not name.strip():
                    st.warning("الرجاء كتابة اسم الطبق.")
                else:
                    # حفظ الصورة
                    img_path = None
                    if uploaded_img:
                        img = Image.open(uploaded_img)
                        img = img.convert("RGB")
                        # حفظ في مجلد images باسم فريد
                        img_name = f"img_{len(os.listdir('images'))+1}_{uploaded_img.name}"
                        img_path = os.path.join("images", img_name)
                        img.save(img_path)

                    # الحصول على id التصنيف المختار
                    for c in cats:
                        if c[1] == selected_cat:
                            cat_id = c[0]
                            break
                    add_item(name.strip(), price, desc, img_path, int(available), cat_id)
                    st.success("تمت إضافة الطبق بنجاح!")
                    st.rerun()

        st.subheader("الأطباق الحالية")
        all_items = get_items()
        if not all_items:
            st.info("لا توجد أطباق مضافة بعد.")
        else:
            for item in all_items:
                item_id, name, price, desc, img_path, available, cat_id, cat_name = item
                with st.expander(f"{name} - {price} د.ع ({cat_name})"):
                    col1, col2 = st.columns([1,2])
                    with col1:
                        if img_path and os.path.exists(img_path):
                            st.image(img_path, width=150)
                        else:
                            st.markdown("🍲 لا توجد صورة")
                        st.markdown(f"**متوفر:** {'✅' if available else '❌'}")

                    with col2:
                        # نموذج تعديل
                        with st.form(f"edit_form_{item_id}"):
                            new_name = st.text_input("الاسم", value=name)
                            new_price = st.number_input("السعر", value=float(price))
                            new_desc = st.text_area("الوصف", value=desc if desc else "")
                            new_available = st.checkbox("متوفر", value=bool(available))
                            # اختيار تصنيف جديد
                            cats = get_categories()
                            if cats:
                                current_cat_index = 0
                                for i, c in enumerate(cats):
                                    if c[0] == cat_id:
                                        current_cat_index = i
                                        break
                                new_cat = st.selectbox("التصنيف", [c[1] for c in cats], index=current_cat_index)
                                # الحصول على id التصنيف المختار
                                new_cat_id = None
                                for c in cats:
                                    if c[1] == new_cat:
                                        new_cat_id = c[0]
                                        break
                            else:
                                new_cat_id = cat_id  # لا تغيير

                            new_img = st.file_uploader("تغيير الصورة (اترك فارغًا للإبقاء على الحالية)", type=["jpg","jpeg","png"], key=f"img_{item_id}")
                            save_edit = st.form_submit_button("حفظ التعديلات")
                            delete_btn = st.form_submit_button("🗑️ حذف الطبق")

                            if save_edit:
                                if new_img:
                                    # حذف الصورة القديمة إذا استبدلت
                                    if img_path and os.path.exists(img_path):
                                        os.remove(img_path)
                                    img = Image.open(new_img).convert("RGB")
                                    img_name = f"img_{len(os.listdir('images'))+1}_{new_img.name}"
                                    new_img_path = os.path.join("images", img_name)
                                    img.save(new_img_path)
                                else:
                                    new_img_path = img_path  # نفس المسار

                                update_item(item_id, new_name, new_price, new_desc, new_img_path, int(new_available), new_cat_id)
                                st.success("تم تحديث الطبق.")
                                st.rerun()

                            if delete_btn:
                                delete_item(item_id)
                                st.success("تم حذف الطبق.")
                                st.rerun()

# ======================= تشغيل الصفحة المناسبة =======================
if st.session_state.admin:
    admin_panel()
else:
    show_menu()
