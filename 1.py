from datetime import datetime
import sqlite3
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# استيراد البيانات الحساسة والإعدادات من الملف المنفصل
from config import BANK_INFO, BOT_WHATSAPP, SENDER_EMAIL, SENDER_PASSWORD

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(
    page_title="شركة التخطيط العالمية للاستثمار | العقارات في مسقط والخليج",
    page_icon="🏢",
    layout="wide",
)

DB_NAME = "real_estate_agent.db"


# تهيئة قاعدة البيانات تلقائياً
def init_db():
  try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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

    cursor.execute("PRAGMA table_info(properties)")
    columns = [col[1] for col in cursor.fetchall()]
    if "owner_phone" not in columns:
      cursor.execute("ALTER TABLE properties ADD COLUMN owner_phone TEXT")

    cursor.execute("""
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
    init_db()
    conn = sqlite3.connect(DB_NAME)
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


# المحرك الذكي لجلب العقارات
def fetch_smart_gcc_properties():
  try:
    init_db()
    sample_listings = [
        (
            "أرض استثمارية كبرى في مسقط هيلز",
            "مسقط",
            150000.0,
            "مساحة 1200 متر مخصصة لبناء برج تجاري سكني.",
            "https://muscat-realestate.om/prop/201",
            "+96899112233",
        ),
        (
            "فلل فاخرة بإطلالة بحرية في القرم",
            "القرم",
            220000.0,
            "تشطيبات أوروبية راقية، مناسبة للمستثمرين الخليجيين.",
            "https://muscat-realestate.om/prop/202",
            "+96895554433",
        ),
        (
            "عمارة تجارية استثمارية في الخوض",
            "الخوض",
            310000.0,
            "دخل شهري مضمون بنسبة 10%، مؤجرة بالكامل.",
            "https://muscat-realestate.om/prop/203",
            "+96898887766",
        ),
    ]
    import random

    selected = random.choice(sample_listings)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM properties WHERE source_url = ?", (selected[4],)
    )
    existing = cursor.fetchone()

    if not existing:
      cursor.execute(
          "INSERT INTO properties (title, location, price, details, source_url,"
          " owner_phone, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
          (
              selected[0],
              selected[1],
              selected[2],
              selected[3],
              selected[4],
              selected[5],
              "نشط",
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ),
      )
      conn.commit()
      add_log("SUCCESS", f"تم رصد عقار جديد: {selected[0]} في {selected[1]}")
    conn.close()
  except:
    pass


# القائمة الجانبية لإدارة الدخول
st.sidebar.header("🔐 بوابة الإدارة والتحكم")
admin_pass = st.sidebar.text_input("كلمة مرور الإدارة:", type="password")
is_admin = admin_pass == "GPI*2025"

if is_admin:
  st.sidebar.success("🟢 تم تفعيل وضع المشرف (Admin Mode)")
  app_mode = st.sidebar.radio(
      "اختر وضع العرض:",
      ["🌍 عرض موقع الزوار (الرئيسي)", "⚙️ لوحة التحكم والإدارة الذكية"],
  )
else:
  app_mode = "🌍 عرض موقع الزوار (الرئيسي)"
  st.sidebar.info("💡 الموقع معروض الآن كما يراه الزبائن والمشترون.")
  fetch_smart_gcc_properties()

# ==========================================
# 1. وضع الزوار والمشترين (الموقع العقاري العام)
# ==========================================
if app_mode == "🌍 عرض موقع الزوار (الرئيسي)":
  st.title(
      "🏢 شركة التخطيط العالمية للاستثمار (Global Planning Investment"
      " Company)"
  )
  st.markdown(
      "### 🌟 منصة العروض العقارية الاستثمارية في مسقط وسائر دول مجلس التعاون"
      " الخليجي"
  )
  st.markdown(
      "نرحب بكم عملائنا الكرام من **المملكة العربية السعودية، الإمارات، الكويت،"
      " قطر، البحرين، وعمان**. استعرضوا أفضل الفرص الاستثمارية وتواصلوا مع"
      " فريق المبيعات لحفظ حقوق الوساطة."
  )
  st.markdown("---")

  col1, col2 = st.columns(2)
  with col1:
    filter_loc = st.selectbox(
        "📍 تصفية حسب المنطقة في مسقط:",
        ["الكل", "مسقط", "القرم", "الخوض", "بوشر", "العامرات"],
    )

  st.markdown("---")
  st.subheader("📋 قائمة العقارات المتاحة حالياً للبيع والاستثمار")

  init_db()
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  try:
    if filter_loc == "الكل":
      cursor.execute(
          "SELECT title, location, price, details, source_url FROM properties"
          " ORDER BY id DESC"
      )
    else:
      cursor.execute(
          "SELECT title, location, price, details, source_url FROM properties"
          " WHERE location = ? ORDER BY id DESC",
          (filter_loc,),
      )
    public_props = cursor.fetchall()
  except:
    public_props = []
  conn.close()

  if public_props:
    for pp in public_props:
      with st.container():
        st.markdown(f"### 🏢 {pp[0]}")
        st.write(
            f"📍 **الموقع:** {pp[1]} | 💰 **السعر:** {pp[2]:,} ر.ع (ريال عماني)"
        )
        st.write(f"📝 **التفاصيل:** {pp[3]}")

        whatsapp_link = (
            f"https://wa.me/{BOT_WHATSAPP.replace('+', '')}?text="
            f"مرحباً، أهتم بالعقار ({pp[0]}) في موقع ({pp[1]}) بسعر"
            f" ({pp[2]} ر.ع). أرجو التواصل للتفاصيل."
        )
        st.markdown(
            f"[💬 تواصل مع فريق المبيعات (واتساب)]({whatsapp_link}) | 📱 رقم"
            f" الشركة: `{BOT_WHATSAPP}`"
        )
        st.markdown("---")
  else:
    st.info("لا توجد عقارات مطابقة حالياً.")

  # قسم تسجيل رغبة المشتري
  st.markdown("### 📝 سجل رغبتك الاستثمارية (لبحث العقارات المخصصة)")
  with st.form("public_buyer_form"):
    bp_name = st.text_input("الاسم الكريم")
    bp_phone = st.text_input("رقم الهاتف مع رمز الدولة (مثال: +9665XXXXXXXX)")
    bp_email = st.text_input("البريد الإلكتروني")
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
    submit_bp = st.form_submit_button("إرسال الطلب لفريق الاستثمار")

    if submit_bp and bp_name:
      try:
        init_db()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO buyers (name, phone, email, country,"
            " preferred_location, max_budget) VALUES (?, ?, ?, ?, ?, ?)",
            (bp_name, bp_phone, bp_email, bp_country, bp_loc, bp_budget),
        )
        conn.commit()
        conn.close()
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

  st.markdown("---")
  st.markdown(
      f"📍 **عنوان الشركة:** مسقط، سلطنة عمان | 📧 **البريد الرسمي:**"
      f" {SENDER_EMAIL} | 📱 **خدمة العملاء:** {BOT_WHATSAPP}"
  )


# ==========================================
# 2. وضع لوحة التحكم والإدارة (دور الوسيط الشامل + صانع الإعلانات)
# ==========================================
elif app_mode == "⚙️ لوحة التحكم والإدارة الذكية":
  st.title(
      "⚙️ لوحة تحكم الوسيط الذكي - شركة التخطيط العالمية للاستثمار (دور الوسيط"
      " الكامل)"
  )
  st.warning(
      "⚠️ هذه لوحة الإدارة الخاصة بك للبحث عن المشترين وتوليد الإعلانات"
      " التسويقية."
  )

  tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
      "🔍 محرك مطابقة المشترين (AI Matchmaker)",
      "📢 صانع الإعلانات التسويقية (GCC Ads)",
      "🏠 إدارة العقارات وأرقام الملاك (سرية)",
      "👥 المشترين المسجلين",
      "💰 الإيرادات والاشتراكات",
      "➕ إضافة عقار يدوياً",
  ])

  with tab1:
    st.subheader(
        "🎯 مطابقة العقارات بالبحث التلقائي عن المشترين والمستثمرين المهتمين"
    )
    st.markdown(
        "يقوم هذا المحرك بفحص العقارات المتاحة ومقارنتها فوراً بميزانيات"
        " ومواقع المستثمرين المسجلين لديك لتبادر بالاتصال بهم كـوسيط محترف."
    )

    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, location, price FROM properties")
    properties_list = cursor.fetchall()

    if properties_list:
      selected_prop_id = st.selectbox(
          "اختر عقاراً للبحث عن مشترين له:",
          [p[0] for p in properties_list],
          format_func=lambda x: next(
              f"{p[1]} ({p[2]} - {p[3]} ر.ع)"
              for p in properties_list
              if p[0] == x
          ),
      )

      if selected_prop_id:
        cursor.execute(
            "SELECT title, location, price FROM properties WHERE id = ?",
            (selected_prop_id,),
        )
        p_data = cursor.fetchone()

        cursor.execute(
            "SELECT name, phone, email, country, max_budget FROM buyers WHERE"
            " preferred_location = ? AND max_budget >= ?",
            (p_data[1], p_data[2]),
        )
        matched_buyers = cursor.fetchall()

        st.markdown(f"### النتائج للعقار: **{p_data[0]}** في ({p_data[1]})")
        if matched_buyers:
          st.success(
              f"🎉 وجدنا ({len(matched_buyers)}) مشتري/مستثمر تتطابق ميزانيتهم"
              " وطلباتهم مع هذا العقار!"
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
          st.info(
              "لا يوجد مشترين مسجلين حالياً بنفس المواصفات. استخدم قسم (صانع"
              " الإعلانات) لنشر العقار وجذب عملاء جدد بسرعة."
          )
    else:
      st.info("لا توجد عقارات مسجلة بعد.")
    conn.close()

  with tab2:
    st.subheader(
        "📢 صانع الإعلانات التسويقية الجاهزة (Instagram / WhatsApp / Twitter)"
    )
    st.markdown(
        "أنشئ إعلانات احترافية مصممة خصيصاً لجذب المستثمرين الخليجيين"
        " والمحليين بنقرة زر واحدة."
    )

    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, location, price, details FROM properties"
    )
    ads_props = cursor.fetchall()
    conn.close()

    if ads_props:
      ad_choice = st.selectbox(
          "اختر عقاراً لتوليد إعلان له:",
          [ap[0] for ap in ads_props],
          format_func=lambda x: next(
              f"{ap[1]} - {ap[2]}" for ap in ads_props if ap[0] == x
          ),
      )

      if ad_choice:
        chosen_p = next(ap for ap in ads_props if ap[0] == ad_choice)

        generated_ad_text = (
            f"🌟 **فرصة استثمارية عقارية كبرى في مسقط** 🇴🇲\n\n"
            f"📍 **الموقع:** {chosen_p[2]}\n"
            f"🏢 **العقار:** {chosen_p[1]}\n"
            f"💰 **السعر التنافسي:** {chosen_p[3]:,} ريال عماني\n\n"
            f"📝 **التفاصيل:** {chosen_p[4]}\n\n"
            f"✨ فرصة ممتازة للمستثمرين من سلطنة عمان وسائر دول مجلس التعاون"
            f" الخليجي (السعودية، الإمارات، الكويت، قطر، البحرين).\n\n"
            f"📞 **للتواصل المباشر مع فريق الوساطة وحجز العقار:**\n"
            f"واتساب: `{BOT_WHATSAPP}`\n"
            f"البريد الإلكتروني: `{SENDER_EMAIL}`\n\n"
            f"#عقارات_مسقط #استثمار_عقاري #سلطنة_عمان #عقارات_الخليج"
            f" #مستثمر_خليجي #شركة_التخطيط_العالمية"
        )

        st.text_area(
            "النص الإعلاني الجاهز (انسخه وانشره مباشرة في وسائل التواصل):",
            generated_ad_text,
            height=250,
        )
        st.success(
            "💡 نصيحة تسويقية: انسخ هذا النص وضعه مع صورة جذابة للعقار على"
            " حساب إنستغرام الخاص بالشركة أو حالات الواتساب لجذب المستثمرين"
            " فورا!"
        )
    else:
      st.info("لا توجد عقارات كافية لتوليد الإعلانات.")

  with tab3:
    st.subheader("قائمة العقارات وأرقام الملاك الحقيقية (سرية للوسيط فقط)")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, location, price, owner_phone FROM properties"
        " ORDER BY id DESC"
    )
    all_p = cursor.fetchall()
    conn.close()
    for ap in all_p:
      st.markdown(
          f"- **{ap[1]}** | الموقع: {ap[2]} | السعر: {ap[3]} ر.ع | 📞 رقم المالك"
          f" الحقيقي: `{ap[4]}`"
      )

  with tab4:
    st.subheader("قاعدة بيانات المستثمرين المشترين")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, phone, email, country, preferred_location, max_budget"
        " FROM buyers"
    )
    all_b = cursor.fetchall()
    conn.close()
    for ab in all_b:
      st.markdown(
          f"- **{ab[0]}** ({ab[3]}) | هاتف: `{ab[1]}` | الإيميل: `{ab[2]}` |"
          f" المنطقة: `{ab[4]}` | الميزانية: `{ab[5]} ر.ع`"
      )

  with tab5:
    st.subheader("إيرادات المكاتب والخدمات (بنك مسقط)")
    st.markdown(
        f"**البنك:** {BANK_INFO['bank_name']} | **الآيبان:**"
        f" `{BANK_INFO['iban']}`"
    )
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(amount_paid) FROM subscriptions WHERE payment_status = 'تم"
        " التحويل للحساب البنكي'"
    )
    tot = cursor.fetchone()[0] or 0.0
    conn.close()
    st.metric("إجمالي الإيرادات", f"{tot} ر.ع")

  with tab6:
    st.subheader("إضافة عقار جديد مع رقم المالك (سري)")
    with st.form("manual_prop"):
      m_title = st.text_input("عنوان العقار")
      m_loc = st.text_input("الموقع (مثال: مسقط، القرم)")
      m_price = st.number_input("السعر بالريال العماني", value=50000.0)
      m_details = st.text_area("تفاصيل العقار")
      m_phone = st.text_input("رقم تواصل المالك الحقيقي (مثال: +9689XXXXXXXX)")
      m_sub = st.form_submit_button("نشر العقار في الموقع العام")
      if m_sub and m_title:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO properties (title, location, price, details,"
            " source_url, owner_phone, status, created_at) VALUES (?, ?, ?, ?,"
            " ?, ?, ?, ?)",
            (
                m_title,
                m_loc,
                m_price,
                m_details,
                "https://gpic.om",
                m_phone,
                "نشط",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        conn.close()
        st.success("تم إضافة العقار بنجاح وتجهيزه للمطابقة والإعلانات!")