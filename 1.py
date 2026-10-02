from datetime import datetime, timedelta
import libsql_client
import streamlit as st

# استيراد البيانات الحساسة والإعدادات من الملف المنفصل
from config import BANK_INFO, BOT_WHATSAPP, SENDER_EMAIL, SENDER_PASSWORD

# بيانات الاتصال بقاعدة بيانات Turso السحابية
TURSO_DATABASE_URL = "ضع_رابط_Turso_هنا"  # ضع رابط الـ URL الخاص بك هنا
TURSO_AUTH_TOKEN = "ضع_رمز_التحقق_Token_Here"  # ضع الـ Token الخاص بك هنا

# كلمة المرور السرية الخاصة بلوحة تحكم المشرف
ADMIN_PASSWORD = "123"  # يمكنك تغييرها هنا إلى أي كلمة مرور تريدها

# إعداد الصفحة وتصميم الواجهة الفاخرة
st.set_page_config(
    page_title=(
        "شركة التخطيط العالمية للاستثمار | Global Planning Investment"
    ),
    page_icon="🏢",
    layout="wide",
)

# حقن أكواد CSS لتصميم البطاقات العصرية، مع تثبيت حقل الباسورد باتجاه يساري (LTR) لحل المشكلة جذرياً
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
    /* حل جذري: إجبار خانة الباسورد على الاتجاه اليساري الإنجليزي لمنع تداخل الحروف واختفائها */
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


# دالة مساعدة للاتصال بقاعدة بيانات Turso السحابية
def get_db_client():
  return libsql_client.create_client_sync(
      url=TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN
  )


# تهيئة الجداول في قاعدة بيانات Turso السحابية
def init_db():
  try:
    client = get_db_client()

    client.execute("""
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

    client.execute("""
            CREATE TABLE IF NOT EXISTS buyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                country TEXT,
                preferred_location TEXT,
                max_budget REAL
            )
        """)

    client.execute("""
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

    client.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                log_type TEXT,
                message TEXT
            )
        """)
    client.close()
  except Exception as e:
    pass


init_db()


def add_log(log_type, message):
  try:
    client = get_db_client()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client.execute(
        "INSERT INTO activity_logs (timestamp, log_type, message) VALUES (?, ?,"
        " ?)",
        [timestamp, log_type, message],
    )
    client.close()
  except:
    pass


# ==========================================
# القائمة الجانبية ونظام تسجيل الدخول الآمن بـ Popover Button
# ==========================================
st.sidebar.markdown("### 🔐 بوابة الإدارة")

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

if not st.session_state.authenticated:
  # استخدام زر تفاعلي (Popover) يفتح نافذة منفصلة لكي تكون حرة تماماً من مشاكل اتجاه الكتابة
  with st.sidebar.popover("🔑 تسجيل دخول المشرف"):
    st.markdown("أدخل كلمة المرور الخاصة بالإدارة:")
    with st.form("admin_login_form"):
      password_input = st.text_input(
          "الباسورد:", type="password", key="pwd_box", label_visibility="collapsed"
      )
      submit_login = st.form_submit_button("تحقق ودخول")

      if submit_login:
        if password_input == ADMIN_PASSWORD:
          st.session_state.authenticated = True
          st.rerun()
        else:
          st.error("❌ كلمة المرور غير صحيحة")

  app_mode = "🌍 عرض منصة الزوار"
  st.sidebar.info(
      "💡 الموقع معروض للعملاء. لوحة التحكم محمية ولا تفتح إلا للمسؤول."
  )
else:
  st.sidebar.success("🟢 تم تسجيل الدخول بنجاح")
  if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.authenticated = False
    st.rerun()

  app_mode = st.sidebar.radio(
      "اختر وضع العرض:",
      ["🌍 عرض منصة الزوار", "⚙️ لوحة تحكم الوسيط الذكي"],
  )

one_month_ago = (datetime.now() - timedelta(days=30)).strftime(
    "%Y-%m-%d %H:%M:%S"
)

# ==========================================
# 1. منصة الزوار والمشترين
# ==========================================
if app_mode == "🌍 عرض منصة الزوار":
  st.markdown(
      "<h1 style='text-align: center; color: #1b3b36; margin-bottom: 0;'>شركة"
      " التخطيط العالمية للاستثمار</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<h3 style='text-align: center; color: #0e6251; font-weight: 400;"
      " margin-bottom: 30px;'>منصة الفرص العقارية الاستثمارية الفاخرة في سلطنة"
      " عمان والخليج</h3>",
      unsafe_allow_html=True,
  )

  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #1b3b36 0%, #0e6251 100%); color: white; padding: 25px; border-radius: 14px; margin-bottom: 35px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h4 style="margin-top:0; color: #ffffff;">أهلاً بكم عملائنا الكرام من دول مجلس التعاون الخليجي 🇴🇲 🇸🇦 🇦🇪 🇰🇼 🇶🇦 🇧🇭</h4>
            <p style="margin-bottom:0; line-height: 1.6;">نضع بين أيديكم محفظة عقارية حصرية ومختارة بعناية في محافظة مسقط. جميع عروضنا معتمدة ومضمونة.</p>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col1, col2 = st.columns([1, 2])
  with col1:
    filter_loc = st.selectbox(
        "📍 تصفية العقارات حسب المنطقة:",
        ["الكل", "مسقط", "القرم", "الخوض", "بوشر", "العامرات"],
    )

  st.markdown("---")
  st.subheader("📋 أحدث العقارات الاستثمارية المتاحة")

  public_props = []
  try:
    client = get_db_client()
    if filter_loc == "الكل":
      rs = client.execute(
          "SELECT title, location, price, details, source_url, created_at FROM"
          " properties ORDER BY id DESC"
      )
    else:
      rs = client.execute(
          "SELECT title, location, price, details, source_url, created_at FROM"
          " properties WHERE location = ? ORDER BY id DESC",
          [filter_loc],
      )
    public_props = rs.rows
    client.close()
  except:
    pass

  if public_props:
    for i in range(0, len(public_props), 2):
      cols = st.columns(2)
      for j in range(2):
        if i + j < len(public_props):
          pp = public_props[i + j]
          with cols[j]:
            whatsapp_link = (
                f"https://wa.me/{BOT_WHATSAPP.replace('+', '')}?text="
                f"مرحباً، أهتم بالعقار ({pp[0]}) في موقع ({pp[1]}) بسعر"
                f" ({pp[2]} ر.ع). أرجو التواصل للتفاصيل."
            )

            st.markdown(
                f"""
                    <div class="property-card-modern">
                        <div class="card-title">🏢 {pp[0]}</div>
                        <div class="card-location">📍 موقع العقار: <b>{pp[1]}</b></div>
                        <div>
                            <span class="card-price-badge">💰 {pp[2]:,} ر.ع</span>
                        </div>
                        <div class="card-details">{pp[3]}</div>
                        <div class="card-footer">
                            <span class="card-date">🕒 أُضيف في: {pp[5].split(' ')[0]}</span>
                            <a href="{whatsapp_link}" target="_blank" class="whatsapp-btn">💬 تواصل واتساب</a>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
  else:
    st.info(
        "لا توجد عقارات مسجلة في المنصة حالياً. قم بإضافة عقارات جديدة عبر لوحة"
        " التحكم."
    )

  # قسم تسجيل رغبة المشتري
  st.markdown("---")
  st.markdown(
      "<h2 style='text-align: center; color: #1b3b36; margin-top: 30px;'>📝"
      " سجل رغبتك الاستثمارية</h2>",
      unsafe_allow_html=True,
  )

  with st.form("public_buyer_form"):
    c1, c2 = st.columns(2)
    with c1:
      bp_name = st.text_input("الاسم الكريم")
      bp_phone = st.text_input("رقم الهاتف مع رمز الدولة (مثال: +9665XXXXXXXX)")
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
          ["مسقط", "القرم", "الخوض", "بوشر", "العامرات", "الموالح"],
      )
      bp_budget = st.number_input(
          "الحد الأقصى للميزانية المرصودة (ريال عماني)", value=100000.0
      )

    submit_bp = st.form_submit_button("إرسال الطلب لفريق الاستثمار والوساطة")

    if submit_bp and bp_name:
      try:
        client = get_db_client()
        client.execute(
            "INSERT INTO buyers (name, phone, email, country,"
            " preferred_location, max_budget) VALUES (?, ?, ?, ?, ?, ?)",
            [bp_name, bp_phone, bp_email, bp_country, bp_loc, bp_budget],
        )
        client.close()
        add_log(
            "SYSTEM",
            f"طلب استثماري جديد من ({bp_country}): {bp_name} في ({bp_loc})",
        )
        st.success(
            "تم استلام طلبكم بنجاح! سيتواصل معكم فريق شركة التخطيط العالمية"
            " للاستثمار قريباً."
        )
      except Exception as ex:
        st.error(f"حدث خطأ أثناء حفظ الطلب: {ex}")


# ==========================================
# 2. لوحة التحكم والإدارة الذكية
# ==========================================
elif app_mode == "⚙️ لوحة تحكم الوسيط الذكي":
  st.title("⚙️ لوحة تحكم الوسيط الذكي - شركة التخطيط العالمية للاستثمار")
  st.warning(
      "⚠️ لوحة تحكم سرية خاصة بإدارة العقارات، مطابقة المشترين، وتوليد"
      " الإعلانات التسويقية."
  )

  tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
      "🔍 مطابقة المشترين (AI Matchmaker)",
      "📢 صانع الإعلانات (GCC Ads)",
      "🏠 إدارة العقارات (سرية)",
      "👥 قاعدة المستثمرين",
      "💰 الإيرادات (بنك مسقط)",
      "➕ إضافة عقار جديد",
  ])

  with tab1:
    st.subheader(
        "🎯 محرك مطابقة العقارات المسجلة بالبحث التلقائي عن المشترين"
    )
    try:
      client = get_db_client()
      rs_props = client.execute(
          "SELECT id, title, location, price, created_at FROM properties"
      )
      properties_list = rs_props.rows
      client.close()
    except:
      properties_list = []

    if properties_list:
      selected_prop_id = st.selectbox(
          "اختر عقاراً للبحث عن مشترين له:",
          [p[0] for p in properties_list],
          format_func=lambda x: next(
              f"{p[1]} ({p[2]} - {p[3]} ر.ع) [تاريخ: {p[4]}]"
              for p in properties_list
              if p[0] == x
          ),
      )

      if selected_prop_id:
        client = get_db_client()
        p_data = client.execute(
            "SELECT title, location, price FROM properties WHERE id = ?",
            [selected_prop_id],
        ).rows[0]
        matched_buyers = client.execute(
            "SELECT name, phone, email, country, max_budget FROM buyers WHERE"
            " preferred_location = ? AND max_budget >= ?",
            [p_data[1], p_data[2]],
        ).rows
        client.close()

        st.markdown(f"### النتائج للعقار: **{p_data[0]}** في ({p_data[1]})")
        if matched_buyers:
          st.success(
              f"🎉 وجدنا ({len(matched_buyers)}) مشتري/مستثمر تتطابق ميزانيتهم"
              " مع هذا العقار!"
          )
          for mb in matched_buyers:
            st.markdown(
                f"- 👤 **{mb[0]}** (دولة: {mb[3]}) | هاتف: `{mb[1]}` | إيميل:"
                f" `{mb[2]}` | الميزانية: `{mb[4]} ر.ع`"
            )
            w_msg = (
                f"مرحباً بالمستثمر الكريم {mb[0]}، نوفر لكم فرصة عقارية مميزة"
                f" مطابقة لطلبكم في {p_data[1]} بسعر {p_data[2]} ر.ع. للتنسيق:"
                f" {BOT_WHATSAPP}"
            )
            st.markdown(
                f"[💬 إرسال عرض واتساب للمشتري](https://wa.me/{mb[1].replace('+', '')}?text={w_msg})"
            )
            st.markdown("---")
        else:
          st.info("لا يوجد مشترين مسجلين بنفس المواصفات حالياً.")
    else:
      st.info("لا توجد عقارات مسجلة حالياً. قم بإضافة عقار جديد أولاً.")

  with tab2:
    st.subheader(
        "📢 صانع الإعلانات التسويقية الاحترافية (Instagram / WhatsApp / Twitter)"
    )
    try:
      client = get_db_client()
      ads_props = client.execute(
          "SELECT id, title, location, price, details, created_at FROM"
          " properties"
      ).rows
      client.close()
    except:
      ads_props = []

    if ads_props:
      ad_choice = st.selectbox(
          "اختر عقاراً لتوليد إعلان له:",
          [ap[0] for ap in ads_props],
          format_func=lambda x: next(
              f"{ap[1]} - {ap[2]} [تاريخ: {ap[5]}]"
              for ap in ads_props
              if ap[0] == x
          ),
      )

      if ad_choice:
        chosen_p = next(ap for ap in ads_props if ap[0] == ad_choice)
        generated_ad_text = (
            f"🌟 **فرصة استثمارية عقارية كبرى في مسقط (عروض 2026)** 🇴🇲\n\n"
            f"📍 **الموقع:** {chosen_p[2]}\n"
            f"🏢 **العقار:** {chosen_p[1]}\n"
            f"💰 **السعر التنافسي:** {chosen_p[3]:,} ريال عماني\n\n"
            f"📝 **التفاصيل:** {chosen_p[4]}\n\n"
            f"✨ فرصة ممتازة للمستثمرين من سلطنة عمان وسائر دول مجلس التعاون"
            f" الخليجي.\n\n"
            f"📞 **للتواصل المباشر مع فريق الوساطة وحجز العقار عبر الرقم"
            f" الرسمي المعتمد:**\n"
            f"واتساب الشركة: `{BOT_WHATSAPP}`\n"
            f"البريد الإلكتروني: `{SENDER_EMAIL}`\n\n"
            f"#عقارات_مسقط #استثمار_عقاري #سلطنة_عمان #عقارات_الخليج"
            f" #شركة_التخطيط_العالمية"
        )
        st.text_area("النص الإعلاني الجاهز:", generated_ad_text, height=250)
        st.success("💡 الإعلان جاهز للنسخ والنشر المباشر.")
    else:
      st.info("لا توجد عقارات مسجلة لتوليد الإعلانات منها.")

  with tab3:
    st.subheader("قائمة العقارات وأرقام الملاك الحقيقية (سرية للوسيط)")
    try:
      client = get_db_client()
      all_p = client.execute(
          "SELECT id, title, location, price, owner_phone, created_at FROM"
          " properties ORDER BY id DESC"
      ).rows
      client.close()
    except:
      all_p = []

    if all_p:
      for ap in all_p:
        st.markdown(
            f"- **{ap[1]}** | الموقع: {ap[2]} | السعر: {ap[3]} ر.ع | 📞 رقم المالك:"
            f" `{ap[4]}` | 🕒 أُضيف في: {ap[5]}"
        )
    else:
      st.info("لا توجد عقارات مضافة.")

  with tab4:
    st.subheader("قاعدة بيانات المستثمرين المشترين المسجلين")
    try:
      client = get_db_client()
      all_b = client.execute(
          "SELECT name, phone, email, country, preferred_location, max_budget"
          " FROM buyers"
      ).rows
      client.close()
    except:
      all_b = []

    if all_b:
      for ab in all_b:
        st.markdown(
            f"- **{ab[0]}** ({ab[3]}) | هاتف: `{ab[1]}` | الإيميل: `{ab[2]}` |"
            f" المنطقة: `{ab[4]}` | الميزانية: `{ab[5]} ر.ع`"
        )
    else:
      st.info("لا يوجد مشترين مسجلين حالياً.")

  with tab5:
    st.subheader("إيرادات المكاتب والخدمات (بنك مسقط)")
    st.markdown(
        f"**البنك:** {BANK_INFO['bank_name']} | **الآيبان:**"
        f" `{BANK_INFO['iban']}`"
    )
    try:
      client = get_db_client()
      tot_res = client.execute(
          "SELECT SUM(amount_paid) FROM subscriptions WHERE payment_status = 'تم"
          " التحويل للحساب البنكي'"
      ).rows
      tot = (tot_res and tot_res[0][0]) or 0.0
      client.close()
    except:
      tot = 0.0
    st.metric("إجمالي الإيرادات", f"{tot} ر.ع")

  with tab6:
    st.subheader("إضافة عقار جديد مع رقم المالك الرسمي الصحيح")
    with st.form("manual_prop"):
      m_title = st.text_input("عنوان العقار")
      m_loc = st.text_input("الموقع (مثال: مسقط، القرم)")
      m_price = st.number_input("السعر بالريال العماني", value=50000.0)
      m_details = st.text_area("تفاصيل العقار")
      m_phone = st.text_input(
          "رقم تواصل المالك أو الوسيط المعتمد (مثال: +9689XXXXXXXX)",
          value=BOT_WHATSAPP,
      )
      m_sub = st.form_submit_button("نشر العقار الجديد في المنصة العامة")
      if m_sub and m_title:
        try:
          client = get_db_client()
          client.execute(
              "INSERT INTO properties (title, location, price, details,"
              " source_url, owner_phone, status, created_at) VALUES (?, ?, ?, ?,"
              " ?, ?, ?, ?)",
              [
                  m_title,
                  m_loc,
                  m_price,
                  m_details,
                  "https://gpic.om",
                  m_phone,
                  "نشط",
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              ],
          )
          client.close()
          st.success(
              "تم إضافة العقار وحفظه بنجاح في قاعدة بيانات Turso السحابية!"
          )
        except Exception as e:
          st.error(f"حدث خطأ أثناء الحفظ: {e}")