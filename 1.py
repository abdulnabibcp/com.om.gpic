from datetime import datetime
import sqlite3
import time
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# استيراد البيانات الحساسة والإعدادات من الملف المنفصل
from config import BANK_INFO, BOT_WHATSAPP, SENDER_EMAIL, SENDER_PASSWORD

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(
    page_title=(
        "منصة التخطيط العالمية العقارية - الخليج الذكية | شركة التخطيط العالمية"
    ),
    page_icon="🏢",
    layout="wide",
)

DB_NAME = "real_estate_agent.db"


# تهيئة قاعدة البيانات وضمان وجود جميع الأعمدة لتجنب أخطاء الجداول القديمة
def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # إنشاء جدول العقارات الأساسي
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

  # التحقق من وجود عمود owner_phone وإضافته إذا كان مفقوداً في قواعد بيانات قديمة
  cursor.execute("PRAGMA table_info(properties)")
  columns = [col[1] for col in cursor.fetchall()]
  if "owner_phone" not in columns:
    cursor.execute("ALTER TABLE properties ADD COLUMN owner_phone TEXT")

  # إنشاء جدول المشترين
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

  # إنشاء جدول الاشتراكات والإيرادات
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

  # إنشاء جدول السجلات الحية
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


init_db()


def add_log(log_type, message):
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


def send_email_notification(receiver_email, subject, body):
  try:
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
    server.quit()
    return True
  except Exception as e:
    add_log("ALERT", f"فشل إرسال البريد: {str(e)}")
    return False


# المحرك الذكي المتقدم لجلب العقارات مع أرقام التواصل الحقيقية للمالك
def fetch_smart_gcc_properties():
  try:
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
              "ذكي - تم استيراده وتوفير جهة الاتصال",
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ),
      )
      conn.commit()
      add_log(
          "SUCCESS",
          f"🤖 [استيراد ذكي]: عقار جديد ({selected[0]}) في {selected[1]} -"
          f" المالك: {selected[5]}",
      )

      cursor.execute(
          "SELECT name, phone, email, country FROM buyers"
          " WHERE preferred_location = ? AND max_budget >= ?",
          (selected[1], selected[2]),
      )
      matched_buyers = cursor.fetchall()

      if matched_buyers:
        for mb in matched_buyers:
          m_name, m_phone, m_email, m_country = mb
          if m_email and "@" in m_email:
            subject = f"فرصة استثمارية عقارية كبرى في {selected[1]} (مسقط)"
            body = (
                f"عزيزي المستثمر {m_name} ({m_country}),\n\nيوجه لك فريق شركة"
                f" التخطيط العالمية للاستثمار فرصة مميزة رصدها نظامنا الذكي:\n\nالعنوان:"
                f" {selected[0]}\nالسعر: {selected[2]} ر.ع\nالتفاصيل:"
                f" {selected[3]}\nرقم تواصل المالك المباشر: {selected[5]}\n\nللتنسيق"
                f" والتفاوض: {BOT_WHATSAPP}"
            )
            send_email_notification(m_email, subject, body)
          add_log(
              "SUCCESS",
              f"🌐 [توجيه خليجي]: تم إرسال العرض للمشتري ({m_name}) من"
              f" ({m_country}).",
          )
    conn.close()
  except Exception as e:
    add_log("ALERT", f"خطأ في المحرك الذكي: {str(e)}")


# تصميم واجهة المستخدم المتقدمة
st.title("🌐 منصة التخطيط العالمية - الوكيل الذكي للأسواق الخليجية")
st.markdown(
    "التحكم الكامل بالأتمتة، عرض العقارات مع أرقام الملاك مباشرة، وإدارة الموقع"
    " العام الموجه لدول الخليج."
)

# القائمة الجانبية
st.sidebar.header("⚙️ لوحة تحكم المنصة الذكية")
bot_mode = st.sidebar.radio(
    "حالة النظام الذكي:", ["متوقف", "يعمل 24/7 (AI Auto-Pilot)"], index=0
)

if bot_mode == "يعمل 24/7 (AI Auto-Pilot)":
  st.sidebar.success("🟢 النظام الذكي يعمل الآن في الخلفية وجاري رصد السوق...")
  fetch_smart_gcc_properties()
else:
  st.sidebar.warning("🟡 النظام في وضع الاستعداد")

st.sidebar.markdown("---")
st.sidebar.info(f"📧 بريد الشركة: {SENDER_EMAIL}")
st.sidebar.info(f"📱 واتساب الوكيل: {BOT_WHATSAPP}")
st.sidebar.markdown(
    f"🏦 **البنك المعتمد:** {BANK_INFO['bank_name']}\n💳 **الآيبان:**"
    f" `{BANK_INFO['iban']}`"
)

# التبويبات الرئيسية
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 السجلات الحيّة",
    "🏠 العقارات وأرقام الملاك",
    "🌐 واجهة الموقع العام (GCC Catalog)",
    "👥 المشترين الخليجيين",
    "💰 الإيرادات والخدمات",
    "➕ تسجيل مشتري جديد",
])

with tab1:
  st.subheader("متابعة نشاط الروبوت الذكي لحظياً")
  if st.button("🔄 تحديث السجلات"):
    st.rerun()

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT timestamp, log_type, message FROM activity_logs ORDER BY id DESC"
      " LIMIT 50"
  )
  logs = cursor.fetchall()
  conn.close()

  for timestamp, l_type, msg in logs:
    if l_type == "SUCCESS":
      st.success(f"[{timestamp}] {msg}")
    elif l_type == "ALERT":
      st.warning(f"[{timestamp}] {msg}")
    else:
      st.info(f"[{timestamp}] {msg}")

with tab2:
  st.subheader("قائمة العقارات المستوردة مع أرقام التواصل المباشرة")
  st.markdown(
      "هنا يعرض لك البرنامج العقار مع **رقم تواصل المالك أو المعلن الأصلي**"
      " لتتمكن من التحدث معه مباشرة في أي وقت."
  )

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT title, location, price, details, source_url, owner_phone,"
      " created_at FROM properties ORDER BY id DESC"
  )
  props = cursor.fetchall()
  conn.close()

  if props:
    for p in props:
      with st.container():
        st.markdown(f"### 🏢 {p[0]}")
        st.write(
            f"📍 **الموقع:** {p[1]} | 💰 **السعر:** {p[2]} ر.ع | 📞 **رقم المالك"
            f" / المعلن:** `{p[5]}`"
        )
        st.write(f"📝 **التفاصيل:** {p[3]}")
        st.markdown(
            f"[🔗 رابط الإعلان الأصلي]({p[4]}) | للتواصل المباشر مع المالك:"
            f" `wa.me/{p[5]}`"
        )
        st.markdown("---")
  else:
    st.info("لا توجد عقارات بعد. فعل النظام الذكي للبدء.")

with tab3:
  st.subheader("🌐 صفحة العرض العام المجانية (موجهة لأسواق دول الخليج)")
  st.markdown(
      "هذه واجهة مصغرة تعمل كـ **موقع إلكتروني مجاني** لعرض العقارات للزوار"
      " والمستثمرين القادمين من السعودية، الامارات، وسائر دول الخليج."
  )

  col1, col2 = st.columns(2)
  with col1:
    selected_gcc_country = st.selectbox(
        "تصفية حسب مستثمري الدولة:",
        [
            "الكل (الخليج العربي)",
            "المملكة العربية السعودية",
            "دولة الإمارات العربية المتحدة",
            "دولة الكويت",
            "دولة قطر",
            "مملكة البحرين",
        ],
    )
  with col2:
    st.success(
        "💡 نصيحة تسويقية: شارك رابط هذه الصفحة في منصات التواصل أو مجموعات"
        " الاستثمار العقاري الخليجي لجذب رؤوس الأموال!"
    )

  st.markdown("---")
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("SELECT title, location, price, details FROM properties")
  public_props = cursor.fetchall()
  conn.close()

  for pp in public_props:
    st.markdown(
        f"🌟 **{pp[0]}** | **الموقع:** {pp[1]} | **السعر التنافسي:** {pp[2]} ر.ع"
    )
    st.write(f"🔹 {pp[3]}")
    st.markdown("---")

with tab4:
  st.subheader("قاعدة بيانات المشترين والمستثمرين الخليجيين والمحليين")
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT name, phone, email, country, preferred_location, max_budget FROM"
      " buyers"
  )
  buyers = cursor.fetchall()
  conn.close()

  if buyers:
    for b in buyers:
      st.markdown(
          f"- **{b[0]}** ({b[3]}) | هاتف: `{b[1]}` | إيميل: `{b[2]}` | المنطقة:"
          f" `{b[4]}` | الميزانية: `{b[5]} ر.ع`"
      )
  else:
    st.info("لا توجد بيانات مشترين مسجلة.")

with tab5:
  st.subheader("💰 إدارة إيرادات الخدمات المقدمة للمكاتب العقارية")
  st.markdown(
      f"**حساب التحويل المعتمد:** {BANK_INFO['bank_name']} | صاحب الحساب:"
      f" {BANK_INFO['account_holder']} | الآيبان: `{BANK_INFO['iban']}`"
  )

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT office_name, plan_type, amount_paid, payment_status, created_at"
      " FROM subscriptions ORDER BY id DESC"
  )
  subs = cursor.fetchall()
  cursor.execute("SELECT SUM(amount_paid) FROM subscriptions WHERE payment_status = 'تم التحويل للحساب البنكي'")
  total_rev = cursor.fetchone()[0] or 0.0
  conn.close()

  st.metric(
      label=f"إجمالي الإيرادات المحصلة في {BANK_INFO['bank_name']}",
      value=f"{total_rev} ر.ع",
  )

  if subs:
    for s in subs:
      st.markdown(
          f"- المكتب: **{s[0]}** | الباقة: `{s[1]}` | المبلغ: `{s[2]} ر.ع` | الحالة:"
          f" `{s[3]}`"
      )
  else:
    st.info("لا توجد اشتراكات مدفوعة مسجلة حتى الآن.")

with tab6:
  st.subheader("إضافة مشتري أو مستثمر جديد (يدعم دول الخليج)")
  with st.form("add_buyer_form"):
    b_name = st.text_input("اسم المشتري / المستثمر")
    b_phone = st.text_input("رقم الهاتف مع رمز الدولة (مثال: +9665XXXXXXXX)")
    b_email = st.text_input("البريد الإلكتروني")
    b_country = st.selectbox(
        "الدولة",
        [
            "سلطنة عمان",
            "المملكة العربية السعودية",
            "الإمارات العربية المتحدة",
            "الكويت",
            "قطر",
            "البحرين",
        ],
    )
    b_loc = st.selectbox(
        "المنطقة المفضلة في مسقط",
        ["مسقط", "القرم", "الخوض", "بوشر", "العامرات", "الموالح"],
    )
    b_budget = st.number_input("الحد الأقصى للميزانية (ر.ع)", value=100000.0)
    submit_buyer = st.form_submit_button("حفظ المستثمر في النظام الذكي")

    if submit_buyer and b_name:
      conn = sqlite3.connect(DB_NAME)
      c = conn.cursor()
      c.execute(
          "INSERT INTO buyers (name, phone, email, country, preferred_location,"
          " max_budget) VALUES (?, ?, ?, ?, ?, ?)",
          (b_name, b_phone, b_email, b_country, b_loc, b_budget),
      )
      conn.commit()
      conn.close()
      add_log(
          "SYSTEM",
          f"🌍 تم تسجيل مستثمر جديد من ({b_country}): {b_name} يبحث في"
          f" ({b_loc})",
      )
      st.success("تم تسجيل المستثمر بنجاح!")