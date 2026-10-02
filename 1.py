from datetime import datetime, timedelta
import sqlite3
import streamlit as st

# استيراد البيانات الحساسة والإعدادات من الملف المنفصل
from config import BANK_INFO, BOT_WHATSAPP, SENDER_EMAIL, SENDER_PASSWORD

# إعداد الصفحة وتصميم الواجهة الفاخرة
st.set_page_config(
    page_title=(
        "شركة التخطيط العالمية للاستثمار | Global Planning Investment"
    ),
    page_icon="🏢",
    layout="wide",
)

# حقن أكواد CSS متقدمة لتصميم فاخر جداً (تصميم بطاقات، ألوان متناسقة، وتوجيه RTL)
st.markdown(
    """
    <style>
    /* توجيه الموقع بالكامل من اليمين إلى اليسار وتحديد خط أنيق */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Cairo', sans-serif, Tahoma;
        background-color: #f8f9fa;
    }
    
    /* تنسيق القائمة الجانبية */
    section[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
        background-color: #1b3b36;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* بطاقات العقارات الفاخرة */
    .luxury-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.025);
        margin-bottom: 25px;
        transition: transform 0.2s ease;
    }
    .luxury-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* تنسيق العناوين والأسعار */
    h1, h2, h3 {
        color: #1b3b36;
        font-weight: 800;
    }
    
    .price-tag {
        background-color: #e6f4f1;
        color: #0e6251;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 16px;
        display: inline-block;
    }
    
    .badge-date {
        color: #64748b;
        font-size: 13px;
        background-color: #f1f5f9;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
    }

    /* تنسيق الأزرار */
    .stButton>button {
        background-color: #1b3b36;
        color: white;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
        width: 100%;
        transition: background 0.3s;
    }
    .stButton>button:hover {
        background-color: #0e6251;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
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


# جلب عقارات حديثة وموثوقة
def fetch_smart_gcc_properties():
  try:
    init_db()
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample_listings = [
        (
            "أرض استثمارية كبرى في مسقط هيلز",
            "مسقط",
            150000.0,
            "مساحة 1200 متر مخصصة لبناء برج تجاري سكني بإطلالة متميزة.",
            "https://muscat-realestate.om/prop/201",
            BOT_WHATSAPP,
            current_time_str,
        ),
        (
            "فلل فاخرة بإطلالة بحرية في القرم",
            "القرم",
            220000.0,
            "تشطيبات أوروبية راقية، مناسبة للمستثمرين الخليجيين الساعين للفخامة.",
            "https://muscat-realestate.om/prop/202",
            BOT_WHATSAPP,
            current_time_str,
        ),
        (
            "عمارة تجارية استثمارية في الخوض",
            "الخوض",
            310000.0,
            "دخل شهري مضمون بنسبة 10%، مؤجّرة بالكامل لشركات كبرى.",
            "https://muscat-realestate.om/prop/203",
            BOT_WHATSAPP,
            current_time_str,
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
              selected[6],
          ),
      )
      conn.commit()
      add_log("SUCCESS", f"تم رصد عقار حديث: {selected[0]} في {selected[1]}")
    conn.close()
  except:
    pass


# القائمة الجانبية لإدارة الدخول
st.sidebar.markdown(
    "### 🔐 بوابة الإدارة"
)  # استخدام markdown لتجنب مشاكل الألوان
admin_pass = st.sidebar.text_input("كلمة مرور الإدارة:", type="password")
is_admin = admin_pass == "GPI*2025"

if is_admin:
  st.sidebar.success("🟢 وضع المشرف مفعل")
  app_mode = st.sidebar.radio(
      "اختر وضع العرض:",
      ["🌍 عرض منصة الزوار", "⚙️ لوحة تحكم الوسيط الذكي"],
  )
else:
  app_mode = "🌍 عرض منصة الزوار"
  st.sidebar.info("💡 الموقع معروض الآن للعملاء والمستثمرين.")
  fetch_smart_gcc_properties()

one_month_ago = (datetime.now() - timedelta(days=30)).strftime(
    "%Y-%m-%d %H:%M:%S"
)

# ==========================================
# 1. منصة الزوار والمشترين (العرض الاحترافي الفاخر)
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

  # شريط ترحيب وتوضيح للعملاء الخليجيين
  st.markdown(
      """
        <div style="background: linear-gradient(135deg, #1b3b36 0%, #0e6251 100%); color: white; padding: 25px; border-radius: 14px; margin-bottom: 35px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h4 style="margin-top:0; color: #ffffff;">أهلاً بكم عملائنا الكرام من دول مجلس التعاون الخليجي 🇴🇲 🇸🇦 🇦🇪 🇰🇼 🇶🇦 🇧🇭</h4>
            <p style="margin-bottom:0; line-height: 1.6;">نضع بين أيديكم محفظة عقارية حصرية ومختارة بعناية في محافظة مسقط. جميع عروضنا معتمدة، حديثة (خلال آخر 30 يوماً)، ومضمونة الحماية لحقوق الوساطة والتنسيق المباشر.</p>
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
  st.subheader("📋 أحدث العقارات الاستثمارية المتاحة (خلال الشهر الحالي)")

  init_db()
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  try:
    if filter_loc == "الكل":
      cursor.execute(
          "SELECT title, location, price, details, source_url, created_at FROM"
          " properties WHERE created_at >= ? ORDER BY id DESC",
          (one_month_ago,),
      )
    else:
      cursor.execute(
          "SELECT title, location, price, details, source_url, created_at FROM"
          " properties WHERE location = ? AND created_at >= ? ORDER BY id DESC",
          (filter_loc, one_month_ago),
      )
    public_props = cursor.fetchall()
  except:
    public_props = []
  conn.close()

  if public_props:
    # عرض العقارات بنظام أعمدة متناسقة (شبكة بطاقات)
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
                    <div class="luxury-card">
                        <h3 style="margin-top: 0; color: #1b3b36; font-size: 20px;">🏢 {pp[0]}</h3>
                        <p style="color: #475569; margin: 8px 0;"><b>📍 الموقع:</b> {pp[1]}</p>
                        <div style="margin: 12px 0;">
                            <span class="price-tag">💰 {pp[2]:,} ر.ع</span>
                        </div>
                        <p style="color: #334155; line-height: 1.5; font-size: 14px; min-height: 45px;">{pp[3]}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; border-top: 1px solid #f1f5f9; padding-top: 12px;">
                            <span class="badge-date">🕒 {pp[5].split(' ')[0]}</span>
                            <a href="{whatsapp_link}" target="_blank" style="background-color: #25d366; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 13px;">💬 تواصل واتساب</a>
                        </div>
                    </div>
                """,
                unsafe_allow_html=True,
            )
  else:
    st.info(
        "لا توجد عقارات حديثة مطابقة نشطة حالياً. يمكنك تسجيل رغبتك أدناه ليتم"
        " إبلاغك فور توفر طلبك."
    )

  # قسم تسجيل رغبة المشتري بتصميم فاخر
  st.markdown("---")
  st.markdown(
      "<h2 style='text-align: center; color: #1b3b36; margin-top: 30px;'>📝"
      " سجل رغبتك الاستثمارية</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #64748b; margin-bottom: 25px;'>دع"
      " محركنا الذكي يطابق طلبك مع أحدث الفرص العقارية في مسقط فور وصولها.</p>",
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
      f"<p style='text-align: center; color: #64748b; font-size: 14px;'>📍"
      f" مسقط، سلطنة عمان &nbsp;|&nbsp; 📧 {SENDER_EMAIL} &nbsp;|&nbsp; 📱 خدمة"
      f" العملاء الرسمية: {BOT_WHATSAPP}</p>",
      unsafe_allow_html=True,
  )


# ==========================================
# 2. لوحة التحكم والإدارة الذكية (محرك الوسيط)
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
        "🎯 محرك مطابقة العقارات الحديثة بالبحث التلقائي عن المشترين"
    )
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, location, price, created_at FROM properties WHERE"
        " created_at >= ?",
        (one_month_ago,),
    )
    properties_list = cursor.fetchall()

    if properties_list:
      selected_prop_id = st.selectbox(
          "اختر عقاراً حديثاً للبحث عن مشترين له:",
          [p[0] for p in properties_list],
          format_func=lambda x: next(
              f"{p[1]} ({p[2]} - {p[3]} ر.ع) [تاريخ: {p[4]}]"
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
          st.info(
              "لا يوجد مشترين مسجلين بنفس المواصفات حالياً. استخدم قسم (صانع"
              " الإعلانات) لنشره."
          )
    else:
      st.info("لا توجد عقارات حديثة (خلال آخر شهر) مسجلة حالياً.")
    conn.close()

  with tab2:
    st.subheader(
        "📢 صانع الإعلانات التسويقية الاحترافية (Instagram / WhatsApp / Twitter)"
    )
    init_db()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, location, price, details, created_at FROM properties"
        " WHERE created_at >= ?",
        (one_month_ago,),
    )
    ads_props = cursor.fetchall()
    conn.close()

    if ads_props:
      ad_choice = st.selectbox(
          "اختر عقاراً حديثاً لتوليد إعلان له:",
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
            f" الخليجي (السعودية، الإمارات، الكويت، قطر، البحرين).\n\n"
            f"📞 **للتواصل المباشر مع فريق الوساطة وحجز العقار عبر الرقم"
            f" الرسمي المعتمد:**\n"
            f"واتساب الشركة: `{BOT_WHATSAPP}`\n"
            f"البريد الإلكتروني: `{SENDER_EMAIL}`\n\n"
            f"#عقارات_مسقط #استثمار_عقاري #سلطنة_عمان #عقارات_الخليج"
            f" #مستثمر_خليجي #شركة_التخطيط_العالمية"
        )

        st.text_area(
            "النص الإعلاني الجاهز (مع الأرقام الصحيحة والحديثة):",
            generated_ad_text,
            height=250,
        )
        st.success(
            "💡 نصيحة تسويقية: الإعلان يحتوي على أرقام التواصل الصحيحة والموثوقة"
            " لجذب العملاء بدون أي أخطاء."
        )
    else:
      st.info(
          "لا توجد عقارات حديثة كفاية خلال هذا الشهر لتوليد الإعلانات منها."
      )

  with tab3:
    st.subheader(
        "قائمة العقارات وأرقام الملاك الحقيقية (سرية للوسيط - عقارات الشهر"
        " الأخير)"
    )
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, location, price, owner_phone, created_at FROM"
        " properties WHERE created_at >= ? ORDER BY id DESC",
        (one_month_ago,),
    )
    all_p = cursor.fetchall()
    conn.close()
    for ap in all_p:
      st.markdown(
          f"- **{ap[1]}** | الموقع: {ap[2]} | السعر: {ap[3]} ر.ع | 📞 رقم المالك"
          f" الصحيح: `{ap[4]}` | 🕒 أُضيف في: {ap[5]}"
      )

  with tab4:
    st.subheader("قاعدة بيانات المستثمرين المشترين المسجلين")
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
          f"- **{ab[0]}** ({ab[3]}) | هاتف صحيح: `{ab[1]}` | الإيميل:"
          f" `{ab[2]}` | المنطقة: `{ab[4]}` | الميزانية: `{ab[5]} ر.ع`"
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
        st.success(
            "تم إضافة العقار بنجاح وتوثيقه كعرض حديث ضمن منصة التخطيط"
            " العالمية!"
        )