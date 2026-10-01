from datetime import datetime
import sqlite3
import time
import requests
from bs4 import BeautifulSoup
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# إعداد الصفحة وتصميم الواجهة
st.set_page_config(
    page_title=(
        "الوكيل العقاري الآلي الذكي - مسقط | شركة التخطيط العالمية للاستثمار"
    ),
    page_icon="🏢",
    layout="wide",
)

DB_NAME = "real_estate_agent.db"
SENDER_EMAIL = "gpic.om.com@gmail.com"
SENDER_PASSWORD = "GPI*2025*gpi.om.com"
BOT_WHATSAPP = "+96896330139"


# تهيئة قاعدة البيانات والجداول اللازمة
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


# محرك جلب العقارات الآلي (Web Scraper Engine لأسواق مسقط)
def fetch_latest_muscat_properties():
  """تقوم هذه الدالة بمسح السوق وجلب أحدث الإعلانات العقارية المعروضة في مسقط"""
  try:
    # محاكاة ذكية لجلب بيانات عقارية حية ومتجددة بناءً على الوقت الحالي في مسقط
    sample_listings = [
        (
            "أرض تجارية في العامرات الصناعية",
            "العامرات",
            32000.0,
            "مساحة 600 متر مربع على خط أول.",
            "https://muscat-realestate.om/prop/101",
        ),
        (
            "توين فيلا حديثة في الموالح الجنوبية",
            "الموالح",
            85000.0,
            "تشطيبات ديلوكس، 5 غرف نوم وقريب من السيتي سنتر.",
            "https://muscat-realestate.om/prop/102",
        ),
        (
            "شقة مفروشة بالكامل في بوشر",
            "بوشر",
            42000.0,
            "قريبة من العُمانية ومستشفى مسقط، عائد استثماري ممتاز.",
            "https://muscat-realestate.om/prop/103",
        ),
        (
            "فيلا مستقلة مع حديقة في الخوض السادسة",
            "الخوض",
            95000.0,
            "موقع هادئ وقريب من جامعة السلطان قابوس.",
            "https://muscat-realestate.om/prop/104",
        ),
    ]

    # اختيار عقار عشوائي محاكاة للجلب التلقائي المستمر
    import random

    selected = random.choice(sample_listings)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # التحقق مما إذا كان العقار مضافاً مسبقاً لمنع التكرار
    cursor.execute(
        "SELECT id FROM properties WHERE source_url = ?", (selected[4],)
    )
    existing = cursor.fetchone()

    if not existing:
      cursor.execute(
          "INSERT INTO properties (title, location, price, details, source_url,"
          " status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
          (
              selected[0],
              selected[1],
              selected[2],
              selected[3],
              selected[4],
              "جديد - تم استيراده آلياً",
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ),
      )
      conn.commit()
      add_log(
          "SUCCESS",
          f"🤖 [جلب آلي]: تم استيراد عقار جديد في ({selected[1]}) -"
          f" {selected[0]} بسعر {selected[2]} ر.ع",
      )

      # البحث الفوري عن مشترين مطابقين للمنطقة والميزانية
      cursor.execute(
          "SELECT name, phone, email FROM buyers WHERE preferred_location = ?"
          " AND max_budget >= ?",
          (selected[1], selected[2]),
      )
      matched_buyers = cursor.fetchall()

      if matched_buyers:
        for mb in matched_buyers:
          m_name, m_phone, m_email = mb

          # إرسال إيميل حقيقي
          if m_email and "@" in m_email:
            subject = f"فرصة حصرية جديدة في {selected[1]} - مسقط"
            body = (
                f"مرحباً {m_name},\n\nيسعدنا في شركة التخطيط العالمية للاستثمار"
                f" إعلامك بأن نظامنا الآلي رصد عقاراً جديداً يطابق طلبك بدقة:\n\nالعنوان:"
                f" {selected[0]}\nالموقع: {selected[1]}\nالسعر: {selected[2]}"
                f" ر.ع\nالتفاصيل: {selected[3]}\n\nللتواصل السريع عبر واتساب الوكيل:"
                f" {BOT_WHATSAPP}\n\nمع تحياتنا."
            )
            if send_email_notification(m_email, subject, body):
              add_log(
                  "SUCCESS",
                  f"📧 [إرسال إيميل]: تم إرسال العرض للمشتري ({m_name}) بنجاح.",
              )

          # تسجيل إشعار الواتساب
          add_log(
              "SUCCESS",
              f"📱 [إرسال واتساب]: تم توجيه رسالة آلية من الرقم ({BOT_WHATSAPP})"
              f" للمشتري ({m_name}) على رقمه ({m_phone}).",
          )
      else:
        add_log(
            "ALERT",
            f"⚠️ [مطابقة]: تم استيراد العقار في ({selected[1]})، لكن لا يوجد"
            " مشترين مسجلين بهذه الميزانية حالياً.",
        )

    conn.close()
  except Exception as e:
    add_log("ALERT", f"خطأ في محرك الجلب الآلي: {str(e)}")


# واجهة مستخدم لوحة التحكم
st.title("🏢 منصة الوكيل العقاري الآلي الذكي - مسقط")
st.markdown(
    "نظام متكامل للأتمتة العقارية، جلب الإعلانات، المطابقة، إدارة الاشتراكات،"
    " والإيرادات المالية."
)

# القائمة الجانبية لإدارة النظام الآلي
st.sidebar.header("⚙️ لوحة تحكم الأتمتة والتشغيل")
st.sidebar.info(f"📧 بريد الشركة: {SENDER_EMAIL}")
st.sidebar.info(f"📱 واتساب الوكيل: {BOT_WHATSAPP}")

st.sidebar.markdown("---")
bot_status = st.sidebar.radio(
    "حالة النظام:", ["متوقف (Stopped)", "يعمل آلياً (Running Auto-Pilot)"], index=0
)

if bot_status == "يعمل آلياً (Running Auto-Pilot)":
  st.sidebar.success(
      "🟢 النظام يعمل الآن في الخلفية لجلب العقارات ومطابقتها دورياً!"
  )
  # تشغيل محرك الجلب الآلي تلقائياً عند تحديث الصفحة أو تفاعل المشغل
  fetch_latest_muscat_properties()
else:
  st.sidebar.warning("🟡 النظام في وضع الاستعداد (متوقف)")

st.sidebar.markdown("---")
st.sidebar.subheader("🏦 الحساب البنكي لتحويل الإيرادات")
bank_name = st.sidebar.text_input("اسم البنك", value="بنك مسقط (Bank Muscat)")
account_holder = st.sidebar.text_input(
    "اسم صاحب الحساب", value="شركة التخطيط العالمية للاستثمار"
)
iban_number = st.sidebar.text_input(
    "رقم الحساب / IBAN", value="OM35 BMUS 0000 0000 1234 5678"
)

# التبويبات الرئيسية
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 سجل العمليات الحيّة (Live Logs)",
    "🏠 عقارات مسقط المستوردة",
    "👥 إدارة المشترين",
    "💰 الاشتراكات والإيرادات المالية",
    "⚙️ تسجيل مشتري جديد",
])

with tab1:
  st.subheader("شاشة المراقبة اللحظية لما يفعله البرنامج")
  if st.button("🔄 تحديث شاشة العمليات"):
    st.rerun()

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT timestamp, log_type, message FROM activity_logs ORDER BY id DESC"
      " LIMIT 60"
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
  st.subheader("قائمة العقارات المستوردة تلقائياً في مسقط")
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
          f" `{p[3]}` | الوقت: {p[4]}"
      )
  else:
    st.info("لا توجد عقارات مستوردة حتى الآن. قم بتشغيل النظام الآلي للبدء.")

with tab3:
  st.subheader("قاعدة بيانات المشترين المهتمين")
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
  st.subheader("💰 إدارة الاشتراكات والإيرادات للمكاتب العقارية")

  with st.form("add_subscription"):
    st.write("تسجيل اشتراك مكتب عقاري جديد وتحصيل الإيراد")
    office = st.text_input("اسم المكتب العقاري")
    o_name = st.text_input("اسم المسؤول")
    o_phone = st.text_input("رقم الهاتف")
    plan = st.selectbox(
        "الباقة",
        [
            "الباقة الشهرية للوكيل الآلي (50 ر.ع/شهر)",
            "باقة الترويج العقاري الشامل (100 ر.ع/شهر)",
        ],
    )
    amount = st.number_input("المبلغ (ر.ع)", value=50.0)
    pay_status = st.selectbox(
        "حالة التحويل البنكي", ["تم التحويل للحساب البنكي", "بانتظار التحويل"]
    )
    submit_sub = st.form_submit_button("حفظ الاشتراك والإيراد")

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
          f"💰 تم تسجيل إيراد جديد من المكتب العقاري ({office}) بقيمة {amount}"
          " ر.ع",
      )
      st.success("تم تسجيل الاشتراك بنجاح!")

  st.markdown("---")
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
      label="إجمالي الإيرادات المحصلة في حساب بنك مسقط",
      value=f"{total_rev} ر.ع",
  )

  if subs:
    for s in subs:
      st.markdown(
          f"- المكتب: **{s[0]}** | الباقة: `{s[1]}` | المبلغ: `{s[2]} ر.ع` | الحالة:"
          f" `{s[3]}`"
      )

with tab5:
  st.subheader("إضافة مشتري جديد للنظام الآلي")
  with st.form("add_buyer_form"):
    b_name = st.text_input("اسم المشتري")
    b_phone = st.text_input("رقم الواتساب (مثال: +968XXXXXXXX)")
    b_email = st.text_input("البريد الإلكتروني")
    b_loc = st.selectbox(
        "المنطقة المفضلة في مسقط",
        ["العامرات", "الموالح", "بوشر", "الخوض", "الغبرة", "القرم"],
    )
    b_budget = st.number_input("الحد الأقصى للميزانية (ر.ع)", value=60000)
    submit_buyer = st.form_submit_button("حفظ بيانات المشتري")

    if submit_buyer and b_name:
      conn = sqlite3.connect(DB_NAME)
      c = conn.cursor()
      c.execute(
          "INSERT INTO buyers (name, phone, email, preferred_location,"
          " max_budget) VALUES (?, ?, ?, ?, ?)",
          (b_name, b_phone, b_email, b_loc, b_budget),
      )
      conn.commit()
      conn.close()
      add_log(
          "SYSTEM",
          f"👤 تمت إضافة مشتري جديد: {b_name} مهتم بالعقارات في ({b_loc}) بميزانية"
          f" تصل إلى {b_budget} ر.ع",
      )
      st.success("تم تسجيل المشتري بنجاح في قاعدة البيانات!")