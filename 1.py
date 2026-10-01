import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
from datetime import datetime
import time
import streamlit as st

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(
    page_title=(
        "نظام الوكيل العقاري الآلي - الخدمات المدفوعة (شركة التخطيط العالمية)"
    ),
    page_icon="🏢",
    layout="wide",
)

DB_NAME = "real_estate_agent.db"
SENDER_EMAIL = "gpic.om.com@gmail.com"
SENDER_PASSWORD = "GPI*2025*gpi.om.com"
BOT_WHATSAPP = "+96896330139"


# تهيئة قاعدة البيانات مع جدول الإيرادات والمشتركين
def init_db():
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
    add_log("ALERT", f"فشل إرسال الإيميل إلى {receiver_email}: {str(e)}")
    return False


# واجهة المستخدم (Dashboard)
st.title("🏢 منصة الوكيل العقاري الآلي والخدمات المدفوعة - مسقط")
st.markdown(
    "نظام متكامل لإدارة العقارات، تقديم خدمات مدفوعة للمكاتب العقارية، وتحصيل"
    " الإيرادات."
)

# القائمة الجانبية لإدارة الحساب البنكي والإعدادات
st.sidebar.header("⚙️ إعدادات النظام المالي")
st.sidebar.info(f"📧 الإيميل النشط: {SENDER_EMAIL}")
st.sidebar.info(f"📱 واتساب الوكيل: {BOT_WHATSAPP}")

st.sidebar.markdown("---")
st.sidebar.subheader("🏦 إعدادات الحساب البنكي لاستقبال الإيرادات")
bank_name = st.sidebar.text_input("اسم البنك", value="بنك مسقط (Bank Muscat)")
account_holder = st.sidebar.text_input(
    "اسم صاحب الحساب", value="شركة التخطيط العالمية للاستثمار"
,
)
iban_number = st.sidebar.text_input(
    "رقم الحساب / IBAN", value="OM35 BMUS 0000 0000 1234 5678"
)

if st.sidebar.button("💾 حفظ وتحديث بيانات البنك"):
  st.sidebar.success("تم تحديث بيانات الحساب بنجاح لتظهر للعملاء!")

st.sidebar.markdown("---")
bot_status = st.sidebar.radio(
    "حالة النظام:", ["متوقف (Stopped)", "يعمل (Running)"], index=0
)

# التبويبات الرئيسية
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 شاشة العمليات الحيّة",
    "🏠 عقارات مسقط",
    "👥 المشترين",
    "💰 إدارة الاشتراكات والإيرادات",
    "⚙️ تشغيل دورة العمل الآلية",
])

with tab1:
  st.subheader("سجل الأحداث والعمليات لحظياً")
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
      st.success(f"[{timestamp}] **{l_type}**: {msg}")
    elif l_type == "ALERT":
      st.warning(f"[{timestamp}] **{l_type}**: {msg}")
    else:
      st.info(f"[{timestamp}] **{l_type}**: {msg}")

with tab2:
  st.subheader("قائمة العقارات المستوردة في مسقط")
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT title, location, price, status, created_at FROM properties ORDER"
      " BY id DESC"
  )
  props = cursor.fetchall()
  conn.close()

  if props:
    for p in props:
      st.markdown(
          f"- **{p[0]}** | الموقع: `{p[1]}` | السعر: `{p[2]} ر.ع` | الحالة:"
          f" `{p[3]}` | التاريخ: {p[4]}"
      )
  else:
    st.info("لا توجد عقارات مسجلة حتى الآن.")

with tab3:
  st.subheader("قاعدة بيانات المشترين")
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT name, phone, email, preferred_location, max_budget FROM buyers"
  )
  buyers = cursor.fetchall()
  conn.close()

  if buyers:
    for b in buyers:
      st.markdown(
          f"- **{b[0]}** | هاتف: `{b[1]}` | إيميل: `{b[2]}` | المنطقة: `{b[3]}`"
          f" | الميزانية: `{b[4]} ر.ع`"
      )
  else:
    st.info("لا يوجد مشترين مسجلين.")

with tab4:
  st.subheader("💰 إدارة اشتراكات المكاتب العقارية والإيرادات")
  st.markdown(
      "سجل المكاتب العقارية المشتركة في الخدمة المدفوعة وحالة التحويلات المالية"
      " على حسابك البنكي."
  )

  with st.form("add_subscription"):
    st.write("إضافة اشتراك جديد لمكتب عقاري")
    office = st.text_input("اسم المكتب العقاري")
    o_name = st.text_input("اسم المسؤول / الشريك")
    o_phone = st.text_input("رقم الهاتف / الواتساب")
    plan = st.selectbox(
        "نوع الباقة المدفوعة",
        [
            "الباقة الشهرية للوكيل الآلي (50 ر.ع/شهر)",
            "باقة الترويج العقاري الشامل (100 ر.ع/شهر)",
            "تقرير سوق مسقط العقاري (20 ر.ع)",
        ],
    )
    amount = st.number_input("المبلغ المحول (ر.ع)", value=50.0)
    pay_status = st.selectbox(
        "حالة الدفع", ["تم التحويل للحساب البنكي", "بانتظار التحويل"]
    )
    submit_sub = st.form_submit_button("تسجيل الاشتراك والإيراد")

    if submit_sub and office:
      conn = sqlite3.connect(DB_NAME)
      c = conn.cursor()
      c.execute(
          "INSERT INTO subscriptions (office_name, owner_name, phone,"
          " plan_type, amount_paid, payment_status, created_at) VALUES (?, ?,"
          " ?, ?, ?, ?, ?)",
          (
              office,
              o_name,
              o_phone,
              plan,
              amount,
              pay_status,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ),
      )
      conn.commit()
      conn.close()
      add_log(
          "SUCCESS",
          f"تم تسجيل اشتراك المكتب العقاري ({office}) بقيمة {amount} ر.ع - الباقة:"
          f" {plan}",
      )
      st.success("تم تسجيل الاشتراك بنجاح وإضافة الإيراد!")

  st.markdown("---")
  st.subheader("سجل المشتركين الحاليين وإجمالي الإيرادات")
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT office_name, plan_type, amount_paid, payment_status, created_at"
      " FROM subscriptions ORDER BY id DESC"
  )
  subs = cursor.fetchall()

  cursor.execute("SELECT SUM(amount_paid) FROM subscriptions WHERE payment_status = 'تم التحويل للحساب البنكي'")
  total_revenue = cursor.fetchone()[0] or 0.0
  conn.close()

  st.metric(
      label="إجمالي الإيرادات المحصلة في الحساب البنكي",
      value=f"{total_revenue} ر.ع",
  )

  if subs:
    for s in subs:
      st.markdown(
          f"- المكتب: **{s[0]}** | الباقة: `{s[1]}` | المبلغ: `{s[2]} ر.ع` | الحالة:"
          f" `{s[3]}` | التاريخ: {s[4]}"
      )
  else:
    st.info("لا توجد اشتراكات مسجلة بعد.")

with tab5:
  st.subheader("محاكاة ودورة العمل الآلية لأسواق مسقط")
  st.write(
      "عند الضغط على الزر أدناه، سيقوم البرنامج بمحاكاة جلب عقار جديد معروض في"
      " مسقط، مطابقتها، وإرسال الإشعارات بناءً على الاشتراكات النشطة."
  )

  if st.button("🚀 تشغيل محاكاة جلب عقار وبحث عن مشتري"):
    with st.spinner("جاري جلب العقار، الفحص، والإرسال..."):
      time.sleep(1)
      sim_title = "فيلا فاخرة في القرم - مسقط"
      sim_loc = "القرم"
      sim_price = 120000.0
      sim_details = "فيلا مستقلة مع مسبح وإطلالة ممتازة."

      conn = sqlite3.connect(DB_NAME)
      cursor = conn.cursor()
      cursor.execute(
          "INSERT INTO properties (title, location, price, details, source_url,"
          " status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (
              sim_title,
              sim_loc,
              sim_price,
              sim_details,
              "https://muscat-realestate-example.com/prop/555",
              "جديد - تم تحليله",
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ),
      )
      conn.commit()
      add_log(
          "SUCCESS",
          f"تم استيراد عقار مدفوع جديد في مسقط: {sim_title} بسعر {sim_price} ر.ع",
      )
      conn.close()

    st.success(
        "تمت دورة العمل بنجاح وتسجيل العقار ضمن الخدمات المقدمة للمكاتب!"
    )
    st.rerun()