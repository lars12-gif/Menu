import streamlit as st
import sqlite3
import base64
import pandas as pd
from PIL import Image
import io

# ==========================================
# 1. إعدادات الصفحة الأساسية
# ==========================================
st.set_page_config(page_title="Royal Menu | المنيو الملكي", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# 2. حقن أكواد CSS المخصصة (التصميم الملكي)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        /* إخفاء شريط أدوات ستريم ليت الافتراضي */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* الخلفية الملكية المتحركة (Dark & Gold Particles) */
        .stApp {
            background-color: #0d0d0d;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(212, 175, 55, 0.05), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(212, 175, 55, 0.08), transparent 25%);
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* تصميم الكروت الزجاجية (Glassmorphism) */
        .meal-card {
            background: rgba(25, 25, 25, 0.6);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            text-align: right;
            direction: rtl;
        }
        .meal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(212, 175, 55, 0.2);
            border: 1px solid rgba(212, 175, 55, 0.8);
        }
        
        /* صورة الوجبة */
        .meal-img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* نصوص الكارت */
        .meal-title { color: #D4AF37; font-size: 22px; font-weight: bold; margin: 5px 0; }
        .meal-bio { color: #cccccc; font-size: 14px; margin-bottom: 10px; min-height: 40px;}
        .meal-price { color: #ffffff; font-size: 20px; font-weight: bold; background: linear-gradient(135deg, #bf953f, #b38728); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
        
        /* شارات التوفر */
        .badge-available { background: rgba(46, 204, 113, 0.2); color: #2ecc71; padding: 4px 8px; border-radius: 5px; font-size: 12px; border: 1px solid #2ecc71;}
        .badge-unavailable { background: rgba(231, 76, 60, 0.2); color: #e74c3c; padding: 4px 8px; border-radius: 5px; font-size: 12px; border: 1px solid #e74c3c;}
        .card-unavailable { opacity: 0.6; filter: grayscale(50%); }

        /* تخصيص أزرار Streamlit (الذهبية للتابلت) */
        div[data-testid="stButton"] > button {
            background: linear-gradient(135deg, #2a2a2a, #1a1a1a);
            color: #D4AF37;
            border: 1px solid #D4AF37;
            border-radius: 8px;
            width: 100%;
            padding: 10px;
            font-size: 18px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        div[data-testid="stButton"] > button:hover {
            background: linear-gradient(135deg, #D4AF37, #b38728);
            color: #111;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
            border-color: #fff;
        }
        
        /* عربة الطلبات (السلة) */
        .cart-container {
            background: rgba(15, 15, 15, 0.9);
            border: 1px solid #D4AF37;
            border-radius: 15px;
            padding: 20px;
            position: sticky;
            top: 20px;
        }
        .cart-item { border-bottom: 1px solid rgba(212, 175, 55, 0.2); padding: 10px 0; }
        .cart-total { font-size: 24px; color: #D4AF37; font-weight: bold; text-align: center; margin-top: 20px; }
        
        /* تأثيرات الإدخال */
        div[data-baseweb="input"] > div {
            background-color: #1a1a1a;
            border: 1px solid #444;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 3. إعدادات قاعدة البيانات SQLite
# ==========================================
def init_db():
    conn = sqlite3.connect('menu_database.db', check_same_thread=False)
    c = conn.cursor()
    # جدول الأصناف
    c.execute('''CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE)''')
    # جدول الوجبات
    c.execute('''CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    name TEXT,
                    bio TEXT,
                    price REAL,
                    image TEXT,
                    is_available BOOLEAN,
                    FOREIGN KEY(category_id) REFERENCES categories(id))''')
    conn.commit()
    return conn, c

conn, c = init_db()

# دوال التعامل مع قاعدة البيانات
def add_category(name):
    try:
        c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except: return False

def get_categories():
    c.execute("SELECT id, name FROM categories")
    return c.fetchall()

def add_meal(cat_id, name, bio, price, image_b64, is_available):
    c.execute("INSERT INTO meals (category_id, name, bio, price, image, is_available) VALUES (?, ?, ?, ?, ?, ?)",
              (cat_id, name, bio, price, image_b64, is_available))
    conn.commit()

def get_meals(category_id=None):
    if category_id:
        c.execute("SELECT * FROM meals WHERE category_id=?", (category_id,))
    else:
        c.execute("SELECT * FROM meals")
    return c.fetchall()

def update_availability(meal_id, status):
    c.execute("UPDATE meals SET is_available=? WHERE id=?", (status, meal_id))
    conn.commit()

def delete_meal(meal_id):
    c.execute("DELETE FROM meals WHERE id=?", (meal_id,))
    conn.commit()

# ==========================================
# 4. إدارة الجلسات (Session State) للسلة والأدمن
# ==========================================
if 'cart' not in st.session_state:
    st.session_state.cart = {}  # {meal_id: {"name": str, "price": float, "qty": int}}
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# دوال السلة
def add_to_cart(m_id, m_name, m_price):
    if m_id in st.session_state.cart:
        st.session_state.cart[m_id]['qty'] += 1
    else:
        st.session_state.cart[m_id] = {'name': m_name, 'price': m_price, 'qty': 1}

def remove_from_cart(m_id):
    if m_id in st.session_state.cart:
        st.session_state.cart[m_id]['qty'] -= 1
        if st.session_state.cart[m_id]['qty'] <= 0:
            del st.session_state.cart[m_id]

def clear_cart():
    st.session_state.cart = {}

# ==========================================
# 5. واجهة الإدارة المخفية (Admin Panel)
# ==========================================
with st.sidebar:
    st.markdown("<h3 style='color:#D4AF37; text-align:center;'>القائمة الجانبية</h3>", unsafe_allow_html=True)
    st.write("---")
    if not st.session_state.admin_auth:
        admin_pass = st.text_input("كلمة مرور الإشراف", type="password")
        if st.button("تسجيل الدخول"):
            if admin_pass == "1234":  # يمكنك تغيير الباسورد هنا
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("كلمة المرور خاطئة!")
    else:
        st.success("أنت في وضع الإشراف")
        if st.button("تسجيل الخروج"):
            st.session_state.admin_auth = False
            st.rerun()

# ==========================================
# 6. الواجهة الرئيسية (التطبيق)
# ==========================================
if st.session_state.admin_auth:
    # ---------------- لوحة تحكم الأدمن ----------------
    st.markdown("<h1 style='text-align: center; color: #D4AF37;'>👑 لوحة التحكم الملكية (الإدارة)</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 إضافة صنف", "🍔 إضافة وجبة", "⚙️ إدارة الوجبات"])
    
    with tab1:
        st.subheader("إضافة صنف جديد (مثال: مقبلات، مشويات)")
        new_cat = st.text_input("اسم الصنف")
        if st.button("إضافة الصنف", key="add_cat"):
            if new_cat and add_category(new_cat):
                st.success(f"تمت إضافة صنف '{new_cat}' بنجاح!")
            else:
                st.error("الاسم موجود مسبقاً أو الحقل فارغ.")
                
    with tab2:
        st.subheader("إضافة وجبة أو أكلة جديدة")
        categories = get_categories()
        if not categories:
            st.warning("يرجى إضافة صنف واحد على الأقل أولاً.")
        else:
            cat_dict = {cat[1]: cat[0] for cat in categories}
            selected_cat = st.selectbox("اختر الصنف", list(cat_dict.keys()))
            
            m_name = st.text_input("اسم الوجبة")
            m_bio = st.text_area("تفاصيل ومكونات الوجبة (البايو)")
            m_price = st.number_input("السعر (مثال: 5000)", min_value=0.0, step=500.0)
            m_image = st.file_uploader("ارفع صورة الوجبة", type=['png', 'jpg', 'jpeg'])
            m_avail = st.checkbox("متوفرة للطلب الآن؟", value=True)
            
            if st.button("حفظ الوجبة", key="save_meal"):
                if m_name and m_price > 0 and m_image:
                    # تشفير الصورة
                    bytes_data = m_image.getvalue()
                    base64_img = base64.b64encode(bytes_data).decode()
                    
                    add_meal(cat_dict[selected_cat], m_name, m_bio, m_price, base64_img, m_avail)
                    st.success("تمت إضافة الوجبة بنجاح!")
                else:
                    st.error("يرجى تعبئة الاسم، السعر، وإرفاق صورة.")
                    
    with tab3:
        st.subheader("إدارة وتعديل الوجبات الحالية")
        all_meals = get_meals()
        for meal in all_meals:
            m_id, c_id, name, bio, price, img, avail = meal
            with st.expander(f"⚙️ {name} - {price} د.ع"):
                col1, col2 = st.columns(2)
                with col1:
                    new_avail = st.checkbox("متوفر؟", value=bool(avail), key=f"avail_{m_id}")
                    if new_avail != bool(avail):
                        update_availability(m_id, new_avail)
                        st.success("تم تحديث حالة التوفر")
                        st.rerun()
                with col2:
                    if st.button("❌ حذف الوجبة", key=f"del_{m_id}"):
                        delete_meal(m_id)
                        st.rerun()

else:
    # ---------------- واجهة الزبون والتابلت (المنيو) ----------------
    
    # تقسيم الشاشة: 70% للمنيو و 30% للسلة
    menu_col, cart_col = st.columns([7, 3])
    
    with menu_col:
        st.markdown("<h1 style='text-align: center; color: #D4AF37; margin-bottom:30px;'>✨ المنيو الملكي ✨</h1>", unsafe_allow_html=True)
        
        categories = get_categories()
        if not categories:
            st.info("المنيو فارغ حالياً، يرجى إضافة أكلات من لوحة الإدارة.")
        else:
            # إنشاء تبويبات للأصناف
            cat_names = [c[1] for c in categories]
            cat_tabs = st.tabs(cat_names)
            
            for idx, tab in enumerate(cat_tabs):
                with tab:
                    cat_id = categories[idx][0]
                    meals = get_meals(cat_id)
                    
                    if not meals:
                        st.write("لا توجد وجبات في هذا الصنف حالياً.")
                        continue
                    
                    # عرض الوجبات في شبكة (2 كروت في كل صف للتابلت)
                    cols = st.columns(2)
                    for i, meal in enumerate(meals):
                        m_id, c_id, name, bio, price, img_b64, avail = meal
                        
                        # تحديد التصميم بناء على التوفر
                        avail_class = "badge-available" if avail else "badge-unavailable"
                        avail_text = "متوفر الآن" if avail else "نفدت الكمية"
                        card_class = "meal-card" if avail else "meal-card card-unavailable"
                        
                        with cols[i % 2]:
                            # كود الـ HTML للكارت
                            st.markdown(f"""
                            <div class="{card_class}">
                                <img src="data:image/jpeg;base64,{img_b64}" class="meal-img">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div class="meal-title">{name}</div>
                                    <div class="{avail_class}">{avail_text}</div>
                                </div>
                                <div class="meal-bio">{bio}</div>
                                <div class="meal-price">{price:,.0f} د.ع</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # أزرار الإضافة والحذف (تظهر فقط إذا الوجبة متوفرة)
                            if avail:
                                btn_col1, btn_col2 = st.columns(2)
                                with btn_col1:
                                    st.button("➕ إضافة", key=f"add_{m_id}", on_click=add_to_cart, args=(m_id, name, price))
                                with btn_col2:
                                    st.button("➖ إزالة", key=f"sub_{m_id}", on_click=remove_from_cart, args=(m_id,))
                            else:
                                st.markdown("<div style='height:45px;'></div>", unsafe_allow_html=True) # فراغ للمحاذاة
                                
    # ---------------- سلة الطلبات المؤقتة ----------------
    with cart_col:
        st.markdown("""
        <div class="cart-container">
            <h2 style='text-align: center; color: #D4AF37;'>🛒 سلة الطلبات</h2>
            <hr style="border-color: rgba(212, 175, 55, 0.3);">
        """, unsafe_allow_html=True)
        
        total_price = 0
        if not st.session_state.cart:
            st.markdown("<p style='text-align:center; color:#888;'>السلة فارغة</p>", unsafe_allow_html=True)
        else:
            for item_id, item_info in st.session_state.cart.items():
                item_total = item_info['qty'] * item_info['price']
                total_price += item_total
                st.markdown(f"""
                <div class="cart-item" style="direction:rtl; display:flex; justify-content:space-between;">
                    <span style="color:#fff; font-size:16px;"><b>{item_info['name']}</b> (x{item_info['qty']})</span>
                    <span style="color:#D4AF37;">{item_total:,.0f} د.ع</span>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class="cart-total">
                المجموع الكلي: {total_price:,.0f} د.ع
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # مسافة
        if st.session_state.cart:
            if st.button("✅ تأكيد وإرسال الطلب", use_container_width=True):
                # هنا يمكنك إضافة كود للطباعة أو الإرسال إذا أردت مستقبلاً
                clear_cart()
                st.toast('🎉 تم تأكيد الطلب بنجاح! جاري تحضيره...', icon='🔥')
                # تحديث الصفحة لتفريغ السلة
                st.rerun()
            
            if st.button("🗑️ إلغاء وتصفير السلة", use_container_width=True):
                clear_cart()
                st.rerun()
