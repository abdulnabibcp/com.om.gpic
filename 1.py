from datetime import datetime, timedelta
import sqlite3
import streamlit as st

# استيراد البيانات الحساسة والإعدادات من الملف المنفصل
from config import BANK_INFO, BOT_WHATSAPP, SENDER_EMAIL, SENDER_PASSWORD

# كلمة المرور السرية الخاصة بلوحة تحكم المشرف (الخاصة بالشركة)
ADMIN_PASSWORD = "GPI*2025"

# إعداد الصفحة وتصميم الواجهة الفاخرة
st.set_page_config(
    page_title=(
        "شركة التخطيط العالمية للاستثمار | Global Planning Investment"
    ),
    page_icon="🏢",
    layout="wide",
)

# حقن أكواد CSS لتصميم البطاقات العصرية وتنسيق الواجهة
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Cairo', sans-serif, Tahoma;
        background-color: #f4f6f8;
    }
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        background-color: #1b3b36;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    input[type="password"] {
        direction: ltr !important;
        text-align: left !important;
    }
    .property-card-modern {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .property-card-modern:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
        border-color: #0e6251;
    }
    .property-card-modern::before {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        left: 0;
        height: 5px;
        background: linear-gradient(90deg, #1b3b36, #0e6251);
    }
    .card-title {
        color: #1b3b36;
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    .card-location {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .card-price-badge {
        background-color: #e6f4f1;
        color: #0e6251;
        padding: 8px 16px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 18px;
        display: inline-block;
        margin-bottom: 14px;
    }
    .card-details {
        color: #334155;
        font-size: 14px;
        line-height: 1.6;
        margin-bottom: 20px;
        min-height: 48px;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #f1f5f9;
        padding-top: 14px;
    }
    .card-date {
        color: #94a3b8;
        font-size: 12px;
    }
    .whatsapp-btn {
        background-color: #25d366;
        color: white !important;
        padding: 8px 18px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 13px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: background 0.2s;
    }
    .whatsapp-btn:hover {
        background-color: #1ebe5d;
    }
    h1, h2, h3 {
        color: #1b3b36;
        font-weight: 800;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def get_db_connection():
  return sqlite3.connect("gpic_buildings.db")


def init_db():
  try:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                type TEXT,
                location TEXT,
                units_count INTEGER,
                monthly_income REAL,
                annual_income REAL,
                price REAL,
                roi REAL,
                owner_phone TEXT,
                google_maps TEXT,
                created_at TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                location TEXT,
                price REAL,
                details TEXT,
                source_url TEXT,
                owner_phone TEXT,
                status TEXT,
                created_at TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS buyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                country TEXT,
                preferred_location TEXT,
                max_budget REAL,
                deal_status TEXT DEFAULT 'مهتم جديد'
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                office_name TEXT,
                owner_name TEXT,
                phone TEXT,
                plan_type TEXT,
                amount_paid REAL,
                payment_status TEXT,
                created_at TEXT
            )
        """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                log_type TEXT,
                message TEXT
            )
        """)
    conn.commit()
    conn.close()
  except Exception as e:
    pass


init_db()


def add_log(log_type, message):
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO activity_logs (timestamp, log_type, message) VALUES (?, ?,"
        " ?)",
        (timestamp, log_type, message),
    )
    conn.commit()
    conn.close()
  except:
    pass


# ==========================================
# القائمة الجانبية ونظام تسجيل الدخول الآمن
# ==========================================
st.sidebar.markdown("### 🔐 بوابة الإدارة والتحكم")

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

with st.sidebar.form("login_sidebar_form"):
  st.markdown("أدخل كلمة المرور لدخول لوحة التحكم:")
  pwd_input = st.text_input(
      "الباسورد:", type="password", label_visibility="collapsed"
  )
  login_btn = st.form_submit_button("🔓 تسجيل الدخول")

  if login_btn:
    if pwd_input == ADMIN_PASSWORD:
      st.session_state.authenticated = True
      st.success("تم تسجيل الدخول بنجاح!")
      st.rerun()
    else:
      st.error("❌ كلمة المرور غير صحيحة")

if st.session_state.authenticated:
  st.sidebar.success("🟢 المشرف مسجل الدخول حالياً")
  if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()

  app_mode = st.sidebar.radio(
      "اختر وضع العرض:",
      ["🌍 عرض منصة الزوار", "⚙️ لوحة تحكم الوسيط الذكي"],
  )
else:
  app_mode = "🌍 عرض منصة الزوار"
  st.sidebar.info(
      "💡 الموقع معروض للزوار. أدخل كلمة المرور (GPI*2025) بالأعلى لفتح لوحة"
      " التحكم."
  )


# ==========================================
# 1. منصة الزوار (عرض البنايات الاستثمارية)
# ==========================================
if app_mode == "🌍 عرض منصة الزوار":
  st.markdown(
      "<h1 style='text-align: center; color: #1b3b36; margin-bottom: 0;'>شركة"
      " التخطيط العالمية للاستثمار</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<h3 style='text-align: center; color: #0e6251; font-weight: 400;"
      " margin-bottom: 30px;'>منصة صفقات البنايات والعقارات الاستثمارية الكبرى في"
      " سلطنة عمان والخليج</h3>",
      unsafe_allow_html=True,
  )

  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #1b3b36 0%, #0e6251 100%); color: white; padding: 25px; border-radius: 14px; margin-bottom: 35px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h4 style="margin-top:0; color: #ffffff;">أهلاً بكم عملائنا الكرام والمستثمرين من دول مجلس التعاون الخليجي 🇴🇲 🇸🇦 🇦🇪 🇰🇼 🇶🇦 🇧🇭</h4>
            <p style="margin-bottom:0; line-height: 1.6;">نختص بالصفقات الكبرى (البنايات السكنية، التجارية، والصناعية) في مسقط وسلطنة عمان بعوائد استثمارية مضمونة.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  b_filter_type = st.selectbox(
      "🏢 تصفية صفقات البنايات حسب القطاع:",
      ["الكل", "سكنية", "تجارية", "صناعية"],
  )

  st.markdown("---")
  st.subheader("📋 محفظة البنايات الاستثمارية المتاحة للبيع")

  public_buildings = []
  try:
    conn = get_db_connection()
    cursor = conn.cursor()
    if b_filter_type == "الكل":
      cursor.execute(
          "SELECT id, title, type, location, units_count, monthly_income,"
          " annual_income, price, roi, owner_phone, google_maps, created_at FROM"
          " buildings ORDER BY id DESC"
      )
    else:
      cursor.execute(
          "SELECT id, title, type, location, units_count, monthly_income,"
          " annual_income, price, roi, owner_phone, google_maps, created_at FROM"
          " buildings WHERE type = ? ORDER BY id DESC",
          (b_filter_type,),
      )
    public_buildings = cursor.fetchall()
    conn.close()
  except:
    pass

  if public_buildings:
    for i in range(0, len(public_buildings), 2):
      cols = st.columns(2)
      for j in range(2):
        if i + j < len(public_buildings):
          b_item = public_buildings[i + j]
          (
              b_id,
              b_title,
              b_type,
              b_loc,
              b_units,
              b_mincome,
              b_aincome,
              b_price,
              b_roi,
              b_ophone,
              b_maps,
              b_date,
          ) = b_item
          with cols[j]:
            contact_number = b_ophone if b_ophone else BOT_WHATSAPP
            whatsapp_msg = (
                f"مرحباً، أهتم بصفقة البناية ({b_title}) - نوع ({b_type}) في"
                f" ({b_loc}) بسعر ({b_price:,.2f} ر.ع) وعائد ({b_roi}%). أرجو"
                f" التنسيق للتفاصيل."
            )
            import urllib.parse

            wa_link = f"https://wa.me/{contact_number.replace('+', '').replace(' ', '')}?text={urllib.parse.quote(whatsapp_msg)}"

            st.markdown(
                f"""
                    <div class="property-card-modern">
                        <div class="card-title">🏢 {b_title}</div>
                        <div class="card-location">📍 الموقع: <b>{b_loc}</b> | النوع: <b>{b_type}</b></div>
                        <div>
                            <span class="card-price-badge">💰 {b_price:,.2f} ر.ع</span>
                        </div>
                        <div class="card-details">
                            🚪 عدد الوحدات: <b>{b_units}</b><br>
                            💵 الدخل الشهري: <b>{b_mincome:,.2f} ر.ع</b> | السنوي: <b>{b_aincome:,.2f} ر.ع</b><br>
                            📈 العائد السنوي (ROI): <b>~{b_roi}%</b>
                        </div>
                        <div style="margin-bottom: 14px;">
                            <a href="{b_maps}" target="_blank" style="color: #0e6251; font-weight: bold; text-decoration: underline;">📍 رابط موقع البناية على الخريطة</a>
                        </div>
                        <div class="card-footer">
                            <span class="card-date">🕒 أُضيف في: {b_date.split(' ')[0]}</span>
                            <a href="{wa_link}" target="_blank" class="whatsapp-btn">💬 تواصل واتساب الصفقة</a>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
  else:
    st.info("لا توجد بنايات استثمارية معروضة حالياً.")

  st.markdown("---")
  st.markdown(
      "<h2 style='text-align: center; color: #1b3b36; margin-top: 30px;'>📝"
      " سجل رغبتك الاستثمارية في البنايات</h2>",
      unsafe_allow_html=True,
  )

  with st.form("public_buyer_form"):
    c1, c2 = st.columns(2)
    with c1:
      bp_name = st.text_input("الاسم الكريم / اسم الشركة الاستثمارية")
      bp_phone = st.text_input("رقم الهاتف مع رمز الدولة (مثال: +9689XXXXXXXX)")
      bp_email = st.text_input("البريد الإلكتروني")
    with c2:
      bp_country = st.selectbox(
          "الدولة القادم منها",
          [
              "سلطنة عمان",
              "المملكة العربية السعودية",
              "الإمارات العربية المتحدة",
              "الكويت",
              "قطر",
              "البحرين",
          ],
      )
      bp_loc = st.selectbox(
          "المنطقة المطلوبة في مسقط",
          ["مسقط", "القرم", "الخوض", "بوشر", "العامرات", "الموالح", "البريمي"],
      )
      bp_budget = st.number_input(
          "الحد الأقصى للميزانية المرصودة للبنايات (ريال عماني)",
          value=500000.0,
          step=50000.0,
      )

    submit_bp = st.form_submit_button(
        "إرسال الطلب لفريق الصفقات الكبرى والوساطة"
    )

    if submit_bp and bp_name:
      try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO buyers (name, phone, email, country,"
            " preferred_location, max_budget, deal_status) VALUES (?, ?, ?, ?,"
            " ?, ?, ?)",
            (
                bp_name,
                bp_phone,
                bp_email,
                bp_country,
                bp_loc,
                bp_budget,
                "مهتم بـ بنايات",
            ),
        )
        conn.commit()
        conn.close()
        st.success("تم استلام طلبكم بنجاح وسيتواصل معكم فريق الشركة قريباً.")
      except Exception as ex:
        st.error(f"حدث خطأ أثناء حفظ الطلب: {ex}")


# ==========================================
# 2. لوحة التحكم للمشرف (Admin Dashboard)
# ==========================================
elif app_mode == "⚙️️ لوحة تحكم الوسيط الذكي":
  st.title("⚙️ لوحة تحكم صفقات البنايات - شركة التخطيط العالمية للاستثمار")
  st.warning(
      "⚠️ لوحة تحكم سرية خاصة بإدارة البنايات، توليد رسائل الواتساب، وتعديل أو"
      " حذف السجلات."
  )

  tab1, tab2, tab3, tab4, tab5 = st.tabs([
      "🏢 1. إضافة وتوليد واتساب للبنايات",
      "✏️ 2. تعديل وحذف البنايات",
      "👥 3. إدارة وحذف المستثمرين",
      "📥 4. تصدير التقارير (CSV)",
      "💰 5. الإيرادات والعمولات",
  ])

  # --- تبويب 1: إضافة بناية وتوليد رسائل (مع الدخل الشهري ورقم الاتصال) ---
  with tab1:
    st.subheader(
        "➕ إضافة بناية استثمارية جديدة مع احتساب الدخل السنوي وعائد (ROI)"
        " إلكترونياً"
    )

    with st.form("building_form"):
      b_title_in = st.text_input(
          "عنوان البناية (مثال: بناية تجارية استثمارية بالقرم)"
      )
      col_b1, col_b2 = st.columns(2)
      with col_b1:
        b_type_in = st.selectbox(
            "قطاع البناية:", ["سكنية", "تجارية", "صناعية"]
        )
        b_loc_in = st.text_input("الموقع / الولاية (مثال: مسقط، بوشر)")
        b_units_in = st.number_input(
            "عدد الشقق / المحلات / الورش:", value=12, step=1
        )
        b_ophone_in = st.text_input(
            "رقم تواصل المالك أو الوسيط المعتمد (مثال: +9689XXXXXXXX)",
            value=BOT_WHATSAPP,
        )
      with col_b2:
        b_monthly_income_in = st.number_input(
            "الدخل الشهري الإجمالي (ريال عماني):", value=3000.0, step=100.0
        )
        b_price_in = st.number_input(
            "السعر المطلوب للصفقة (ريال عماني):",
            value=400000.0,
            step=10000.0,
        )
        b_maps_in = st.text_input(
            "رابط خرائط جوجل للموقع (Google Maps URL):",
            value="https://maps.google.com",
        )

      submit_building = st.form_submit_button(
          "حفظ البناية وتوليد رسالة الواتساب التسويقية"
      )

      if submit_building and b_title_in:
        # حساب الدخل السنوي والعائد الاستثماري (ROI) إلكترونياً
        calculated_annual_income = b_monthly_income_in * 12
        calculated_roi = (
            round((calculated_annual_income / b_price_in) * 100, 2)
            if b_price_in > 0
            else 0.0
        )
        try:
          conn = get_db_connection()
          cursor = conn.cursor()
          cursor.execute(
              """INSERT INTO buildings (title, type, location, units_count, monthly_income, 
                                     annual_income, price, roi, owner_phone, google_maps, created_at) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (
                  b_title_in,
                  b_type_in,
                  b_loc_in,
                  b_units_in,
                  b_monthly_income_in,
                  calculated_annual_income,
                  b_price_in,
                  calculated_roi,
                  b_ophone_in,
                  b_maps_in,
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"✅ تم حفظ البناية بنجاح! الدخل السنوي المحسوب:"
              f" {calculated_annual_income:,.2f} ر.ع | العائد (ROI):"
              f" {calculated_roi}%"
          )
        except Exception as e:
          st.error(f"خطأ أثناء الحفظ: {e}")

    st.markdown("---")
    st.subheader("📲 توليد رسالة واتساب جاهزة للبنايات المسجلة")
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, title, type, location, units_count, monthly_income,"
          " annual_income, price, roi, owner_phone, google_maps FROM buildings"
          " ORDER BY id DESC"
      )
      b_list_res = cursor.fetchall()
      conn.close()
    except:
      b_list_res = []

    if b_list_res:
      selected_b_id = st.selectbox(
          "اختر البناية لتوليد رسالة واتساب:",
          [item[0] for item in b_list_res],
          format_func=lambda x: next(
              f"{item[1]} ({item[2]} - {item[7]:,.2f} ر.ع)"
              for item in b_list_res
              if item[0] == x
          ),
      )

      if selected_b_id:
        chosen_b = next(item for item in b_list_res if item[0] == selected_b_id)
        bt, bty, bloc, buni, bminc, bainc, bpr, broi, bophone, bmap = (
            chosen_b[1],
            chosen_b[2],
            chosen_b[3],
            chosen_b[4],
            chosen_b[5],
            chosen_b[6],
            chosen_b[7],
            chosen_b[8],
            chosen_b[9],
            chosen_b[10],
        )

        contact_num = bophone if bophone else BOT_WHATSAPP
        ready_wa_text = (
            f"🔥 *فرصة استثمارية عقارية كبرى (بناية للبيع)* 🔥\n\n"
            f"🏢 *{bt}*\n\n"
            f"📍 الموقع: {bloc}\n"
            f"🏷 القطاع: {bty}\n"
            f"🚪 عدد الوحدات: {buni} وحدة\n"
            f"💵 الدخل الشهري: {bminc:,.2f} ر.ع (السنوي: {bainc:,.2f} ر.ع)\n"
            f"💵 السعر المطلوب: {bpr:,.2f} ر.ع\n"
            f"📈 العائد السنوي (ROI): ~{broi}%\n\n"
            f"📍 *رابط الموقع على الخريطة مباشرة:*\n"
            f"{bmap}\n\n"
            f"📞 *للتواصل وحجز الصفقة مع مسؤول البناية مباشرة:*\n"
            f"هاتف التواصل / واتساب: `{contact_num}`\n"
            f"البريد الإلكتروني: `{SENDER_EMAIL}`\n\n"
            f"#عقارات_مسقط #بنايات_للبيع #استثمار_عقاري #سلطنة_عمان"
            f" #شركة_التخطيط_العالمية"
        )

        st.text_area("نسخ النص التسويقي للواتساب:", ready_wa_text, height=220)
        import urllib.parse

        direct_link = f"https://wa.me/{contact_num.replace('+', '').replace(' ', '')}?text={urllib.parse.quote(ready_wa_text)}"
        st.markdown(
            f"[💬 اضغط هنا لفتح واتساب ومشاركة الرسالة مباشرة]"
            f"({direct_link})"
        )
    else:
      st.info("لا توجد بنايات مسجلة حالياً.")

  # --- تبويب 2: تعديل وحذف البنايات ---
  with tab2:
    st.subheader(
        "✏️ إدارة، تعديل، أو حذف البنايات الاستثمارية المسجلة في النظام"
    )
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, title, type, location, units_count, monthly_income,"
          " price, owner_phone, google_maps FROM buildings ORDER BY id DESC"
      )
      edit_buildings = cursor.fetchall()
      conn.close()
    except:
      edit_buildings = []

    if edit_buildings:
      selected_edit_id = st.selectbox(
          "اختر البناية المراد تعديلها أو حذفها:",
          [eb[0] for eb in edit_buildings],
          format_func=lambda x: next(
              f"ID: {eb[0]} | {eb[1]} ({eb[2]} - {eb[3]})"
              for eb in edit_buildings
              if eb[0] == x
          ),
      )

      if selected_edit_id:
        current_b = next(
            eb for eb in edit_buildings if eb[0] == selected_edit_id
        )
        (
            eb_id,
            eb_title,
            eb_type,
            eb_loc,
            eb_units,
            eb_mincome,
            eb_price,
            eb_ophone,
            eb_maps,
        ) = current_b

        with st.form(f"edit_building_form_{eb_id}"):
          st.markdown(f"### تعديل بيانات البناية (ID: {eb_id})")
          new_title = st.text_input("عنوان البناية:", value=eb_title)
          col_e1, col_e2 = st.columns(2)
          with col_e1:
            new_type = st.selectbox(
                "القطاع:",
                ["سكنية", "تجارية", "صناعية"],
                index=["سكنية", "تجارية", "صناعية"].index(eb_type)
                if eb_type in ["سكنية", "تجارية", "صناعية"]
                else 0,
            )
            new_loc = st.text_input("الموقع:", value=eb_loc)
            new_units = st.number_input(
                "عدد الوحدات:", value=int(eb_units), step=1
            )
            new_ophone = st.text_input(
                "رقم تواصل المالك:",
                value=eb_ophone if eb_ophone else BOT_WHATSAPP,
            )
          with col_e2:
            new_mincome = st.number_input(
                "الدخل الشهري (ر.ع):", value=float(eb_mincome), step=50.0
            )
            new_price = st.number_input(
                "السعر المطلوب (ر.ع):", value=float(eb_price), step=10000.0
            )
            new_maps = st.text_input("رابط الخريطة:", value=eb_maps)

          col_btn1, col_btn2 = st.columns(2)
          with col_btn1:
            submit_update = st.form_submit_button("💾 حفظ التعديلات")
          with col_btn2:
            submit_delete = st.form_submit_button("🗑️ حذف هذه البناية نهائياً")

          if submit_update:
            new_aincome = new_mincome * 12
            calc_roi = (
                round((new_aincome / new_price) * 100, 2)
                if new_price > 0
                else 0.0
            )
            try:
              conn = get_db_connection()
              cursor = conn.cursor()
              cursor.execute(
                  """UPDATE buildings SET title=?, type=?, location=?, units_count=?, 
                                     monthly_income=?, annual_income=?, price=?, roi=?, 
                                     owner_phone=?, google_maps=? WHERE id=?""",
                  (
                      new_title,
                      new_type,
                      new_loc,
                      new_units,
                      new_mincome,
                      new_aincome,
                      new_price,
                      calc_roi,
                      new_ophone,
                      new_maps,
                      eb_id,
                  ),
              )
              conn.commit()
              conn.close()
              st.success("✨ تم تحديث بيانات البناية بنجاح!")
              st.rerun()
            except Exception as err_up:
              st.error(f"خطأ أثناء التحديث: {err_up}")

          if submit_delete:
            try:
              conn = get_db_connection()
              cursor = conn.cursor()
              cursor.execute("DELETE FROM buildings WHERE id=?", (eb_id,))
              conn.commit()
              conn.close()
              st.success("🗑️ تم حذف البناية بنجاح من النظام!")
              st.rerun()
            except Exception as err_del:
              st.error(f"خطأ أثناء الحذف: {err_del}")
    else:
      st.info("لا توجد بنايات مسجلة للتعديل أو الحذف.")

  # --- تبويب 3: إدارة وحذف المستثمرين ---
  with tab3:
    st.subheader(
        "👥 إدارة وعرض وحذف قاعدة بيانات المستثمرين والمهتمين بالصفقات"
    )
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, name, phone, country, preferred_location, max_budget,"
          " deal_status FROM buyers ORDER BY id DESC"
      )
      all_buyers = cursor.fetchall()
      conn.close()
    except:
      all_buyers = []

    if all_buyers:
      for ab in all_buyers:
        ab_id, ab_name, ab_phone, ab_country, ab_loc, ab_budget, ab_status = ab
        with st.expander(
            f"👤 المستثمر: {ab_name} | الدولة: {ab_country} | الحالة: [{ab_status}]"
        ):
          st.markdown(
              f"📞 **الهاتف:** `{ab_phone}` | 📍 **المنطقة:** {ab_loc} |"
              f" **الميزانية:** `{ab_budget:,.2f} ر.ع`"
          )
          if st.button(
              f"🗑 حذف السجل رقم ({ab_id}) للمستثمر {ab_name}",
              key=f"del_buyer_{ab_id}",
          ):
            try:
              conn = get_db_connection()
              cursor = conn.cursor()
              cursor.execute("DELETE FROM buyers WHERE id=?", (ab_id,))
              conn.commit()
              conn.close()
              st.success("🗑️ تم حذف بيانات المستثمر بنجاح!")
              st.rerun()
            except Exception as e_b:
              st.error(f"خطأ أثناء الحذف: {e_b}")
    else:
      st.info("لا يوجد مستثمرون مسجلون حالياً.")

  # --- تبويب 4: تصدير التقارير ---
  with tab4:
    st.subheader("📥 نظام تصدير بيانات البنايات والعملاء (Export Reports)")
    exp_choice = st.radio(
        "اختر الملف المطلوب تصديره:",
        ["قائمة البنايات الاستثمارية", "قاعدة بيانات المستثمرين"],
    )

    if st.button("تجهيز وتحميل ملف CSV"):
      import pandas as pd

      try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if exp_choice == "قائمة البنايات الاستثمارية":
          cursor.execute(
              "SELECT id, title, type, location, units_count, monthly_income,"
              " annual_income, price, roi, owner_phone, google_maps, created_at"
              " FROM buildings"
          )
          rows = cursor.fetchall()
          df_exp = pd.DataFrame(
              rows,
              columns=[
                  "ID",
                  "العنوان",
                  "النوع",
                  "الموقع",
                  "الوحدات",
                  "الدخل الشهري",
                  "الدخل السنوي",
                  "السعر",
                  "العائد %",
                  "رقم المالك",
                  "خرائط جوجل",
                  "تاريخ الإضافة",
              ],
          )
          fname = "buildings_report.csv"
        else:
          cursor.execute(
              "SELECT id, name, phone, email, country, preferred_location,"
              " max_budget, deal_status FROM buyers"
          )
          rows = cursor.fetchall()
          df_exp = pd.DataFrame(
              rows,
              columns=[
                  "ID",
                  "الاسم",
                  "الهاتف",
                  "الإيميل",
                  "الدولة",
                  "الموقع",
                  "الميزانية",
                  "الحالة",
              ],
          )
          fname = "investors_report.csv"
        conn.close()

        csv_bytes = df_exp.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label=f"💾 اضغط هنا لتحميل ملف ({fname})",
            data=csv_bytes,
            file_name=fname,
            mime="text/csv",
        )
        st.success("الملف جاهز للتحميل بنجاح!")
      except Exception as ex_c:
        st.error(f"خطأ في التصدير: {ex_c}")

  # --- تبويب 5: الإيرادات والعمولات ---
  with tab5:
    st.subheader("💰 إيرادات وعمولات صفقات البنايات (بنك مسقط)")
    st.markdown(
        f"**البنك:** {BANK_INFO['bank_name']} | **الآيبان:**"
        f" `{BANK_INFO['iban']}`"
    )
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT SUM(amount_paid) FROM subscriptions WHERE payment_status = 'تم"
          " التحويل للحساب البنكي'"
      )
      tot_res = cursor.fetchone()
      tot = (tot_res and tot_res[0]) or 0.0
      conn.close()
    except:
      tot = 0.0
    st.metric("إجمالي التحويلات والإيرادات", f"{tot:,.2f} ر.ع")