from datetime import datetime
import sqlite3
import urllib.parse
import streamlit as st

# استيراد البيانات الحساسة والإعدادات من الملف المنفصل
from config import BANK_INFO, SENDER_EMAIL, SENDER_PASSWORD

# رقم هاتف الشركة الثابت للواتساب
COMPANY_WHATSAPP = "+96896330139"

# كلمة المرور السرية للإدارة
ADMIN_PASSWORD = "GPI*2025"

# إعداد الصفحة وتصميم الواجهة الفاخرة
st.set_page_config(
    page_title="منصة العروض العقارية الاستثمارية",
    page_icon="🏢",
    layout="wide",
)

# حقن أكواد CSS لتنسيق الواجهة باحترافية تامة
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Cairo', sans-serif, Tahoma;
        background-color: #f4f6f8;
    }
    .property-card-modern {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
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
    }
    .whatsapp-btn {
        background-color: #25d366;
        color: white !important;
        padding: 8px 18px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 13px;
        display: inline-block;
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
            CREATE TABLE IF NOT EXISTS buyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                country TEXT,
                preferred_location TEXT,
                max_budget REAL,
                deal_status TEXT DEFAULT 'مهتم جديد',
                created_at TEXT
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

    cursor.execute("PRAGMA table_info(buildings)")
    b_columns = [col[1] for col in cursor.fetchall()]
    if "created_at" not in b_columns:
      cursor.execute("ALTER TABLE buildings ADD COLUMN created_at TEXT")

    cursor.execute("PRAGMA table_info(buyers)")
    buyers_columns = [col[1] for col in cursor.fetchall()]
    if "created_at" not in buyers_columns:
      cursor.execute("ALTER TABLE buyers ADD COLUMN created_at TEXT")

    conn.commit()
    conn.close()
  except Exception as e:
    print(f"Database Init Error: {e}")


init_db()

# تهيئة حالة الجلسة للتنقل المخفي للمشرف
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

if "admin_mode_active" not in st.session_state:
  st.session_state.admin_mode_active = False

# ==========================================
# منطقة الإدارة المخفية أعلى الصفحة
# ==========================================
with st.container():
  col_top1, col_top2 = st.columns([8, 2])
  with col_top2:
    if not st.session_state.authenticated:
      with st.popover("🔐 بوابة الإدارة"):
        pass_input = st.text_input("كلمة مرور المشرف:", type="password")
        if st.button("دخول لوحة التحكم"):
          if pass_input == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.admin_mode_active = True
            st.rerun()
          else:
            st.error("كلمة المرور غير صحيحة")
    else:
      if st.button("🚪 خروج من الإدارة"):
        st.session_state.authenticated = False
        st.session_state.admin_mode_active = False
        st.rerun()


# ==========================================
# وضع لوحة التحكم (خاص بالمسؤول)
# ==========================================
if st.session_state.authenticated and st.session_state.admin_mode_active:
  st.title("⚙ لوحة تحكم العروض العقارية (خاص بالوسيط)")
  st.warning(
      "⚠ أنت تصفح لوحة الإدارة السرية. هذه الواجهة لا تظهر للعملاء أو الزوار."
  )

  admin_action = st.selectbox(
      "اختر قسم الإدارة والتحكم:",
      [
          "🏢 1. إضافة بناية جديدة وتوليد رسالة واتساب",
          "✏️ 2. تعديل أو حذف البنايات",
          "👥 3. إدارة المستثمرين والمهتمين",
          "📥 4. تصدير التقارير (HTML أو PDF)",
          "💰 5. الإيرادات والعمولات",
      ],
  )

  st.markdown("---")

  if admin_action == "🏢 1. إضافة بناية جديدة وتوليد رسالة واتساب":
    st.subheader("➕ إضافة بناية استثمارية جديدة")

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
            "🔐 رقم هاتف المعلن / صاحب العقار (يُخزن سرياً):",
            value="+9689XXXXXXXX",
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

      submit_building = st.form_submit_button("حفظ البناية الجديدة")

      if submit_building and b_title_in:
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
                  "",
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              ),
          )
          conn.commit()
          conn.close()
          st.success(
              f"✅ تم حفظ البناية بنجاح! الدخل السنوي:"
              f" {calculated_annual_income:,.2f} ر.ع | العائد (ROI):"
              f" {calculated_roi}%"
          )
        except Exception as e:
          st.error(f"خطأ أثناء الحفظ: {e}")

    st.markdown("---")
    st.subheader("📲 توليد رسالة واتساب جاهزة")
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, title, type, location, units_count, monthly_income,"
          " annual_income, price, roi, owner_phone FROM buildings ORDER BY id"
          " DESC"
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
        bt, bty, bloc, buni, bminc, bainc, bpr, broi, bophone = (
            chosen_b[1],
            chosen_b[2],
            chosen_b[3],
            chosen_b[4],
            chosen_b[5],
            chosen_b[6],
            chosen_b[7],
            chosen_b[8],
            chosen_b[9],
        )

        ready_wa_text = (
            f"🔥 *فرصة استثمارية عقارية كبرى (بناية للبيع)* 🔥\n\n"
            f"🏢 *{bt}*\n\n"
            f"📍 الموقع: {bloc}\n"
            f"🏷 القطاع: {bty}\n"
            f"🚪 عدد الوحدات: {buni} وحدة\n"
            f"💵 الدخل الشهري: {bminc if bminc else 0:,.2f} ر.ع (السنوي:"
            f" {bainc if bainc else 0:,.2f} ر.ع)\n"
            f"💵 السعر المطلوب: {bpr if bpr else 0:,.2f} ر.ع\n"
            f"📈 العائد السنوي (ROI): ~{broi if broi else 0}%\n\n"
            f"📞 *للتواصل:* `{COMPANY_WHATSAPP}`"
        )

        st.text_area("نسخ النص التسويقي للواتساب:", ready_wa_text, height=200)
        direct_link = f"https://wa.me/{COMPANY_WHATSAPP.replace('+', '').replace(' ', '')}?text={urllib.parse.quote(ready_wa_text)}"
        st.markdown(
            f"[💬 اضغط هنا لفتح واتساب ومشاركة الرسالة مباشرة]"
            f"({direct_link})"
        )
        if bophone:
          st.info(f"🔒 رقم هاتف المالك المخزن سرياً: `{bophone}`")
    else:
      st.info("لا توجد بنايات مسجلة.")

  elif admin_action == "✏️ 2. تعديل أو حذف البنايات":
    st.subheader("✏️ إدارة وتعديل أو حذف البنايات")
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, title, type, location, units_count, monthly_income,"
          " price, owner_phone FROM buildings ORDER BY id DESC"
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
        eb_id, eb_title, eb_type, eb_loc, eb_units, eb_mincome, eb_price, eb_ophone = current_b

        with st.form(f"edit_building_form_{eb_id}"):
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
                "عدد الوحدات:", value=int(eb_units) if eb_units else 1, step=1
            )
            new_ophone = st.text_input(
                "🔐 رقم هاتف المالك:", value=eb_ophone if eb_ophone else ""
            )
          with col_e2:
            new_mincome = st.number_input(
                "الدخل الشهري (ر.ع):",
                value=float(eb_mincome) if eb_mincome else 0.0,
                step=50.0,
            )
            new_price = st.number_input(
                "السعر المطلوب (ر.ع):",
                value=float(eb_price) if eb_price else 0.0,
                step=10000.0,
            )

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
                                         owner_phone=? WHERE id=?""",
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
                      eb_id,
                  ),
              )
              conn.commit()
              conn.close()
              st.success("✨ تم تحديث البيانات بنجاح!")
              st.rerun()
            except Exception as err_up:
              st.error(f"خطأ: {err_up}")

          if submit_delete:
            try:
              conn = get_db_connection()
              cursor = conn.cursor()
              cursor.execute("DELETE FROM buildings WHERE id=?", (eb_id,))
              conn.commit()
              conn.close()
              st.success("🗑 تم الحذف بنجاح!")
              st.rerun()
            except Exception as err_del:
              st.error(f"خطأ: {err_del}")
    else:
      st.info("لا توجد بنايات مسجلة.")

  elif admin_action == "👥 3. إدارة المستثمرين والمهتمين":
    st.subheader("👥 قاعدة بيانات المستثمرين والمهتمين الواردة من العملاء")
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          "SELECT id, name, phone, country, preferred_location, max_budget,"
          " deal_status, created_at FROM buyers ORDER BY id DESC"
      )
      all_buyers = cursor.fetchall()
      conn.close()
    except:
      all_buyers = []

    if all_buyers:
      for ab in all_buyers:
        ab_id, ab_name, ab_phone, ab_country, ab_loc, ab_budget, ab_status, ab_date = ab
        with st.expander(
            f"👤 {ab_name} | الدولة: {ab_country} | الهاتف: {ab_phone}"
        ):
          st.markdown(
              f"📍 **المنطقة المطلوبة:** {ab_loc} | 💰 **الميزانية:**"
              f" `{ab_budget:,.2f} ر.ع` | 🕒 **التاريخ:** {ab_date}"
          )
          if st.button(f"🗑 حذف سجل المستثمر رقم ({ab_id})", key=f"del_b_{ab_id}"):
            try:
              conn = get_db_connection()
              cursor = conn.cursor()
              cursor.execute("DELETE FROM buyers WHERE id=?", (ab_id,))
              conn.commit()
              conn.close()
              st.success("تم الحذف بنجاح!")
              st.rerun()
            except Exception as e:
              st.error(f"خطأ: {e}")
    else:
      st.info("لا يوجد طلبات مستثمرين مسجلة حتى الآن.")

  elif admin_action == "📥 4. تصدير التقارير (HTML أو PDF)":
    st.subheader("📥 نظام تصدير التقارير الاحترافية (HTML / PDF)")

    report_type = st.radio(
        "اختر نوع التقرير المطلوب:",
        ["قائمة البنايات الاستثمارية", "قاعدة بيانات المستثمرين"],
    )
    format_choice = st.radio("اختر صيغة التصدير:", ["HTML", "PDF"])

    if st.button("توليد وتنزيل التقرير"):
      try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if report_type == "قائمة البنايات الاستثمارية":
          cursor.execute(
              "SELECT id, title, type, location, units_count, monthly_income,"
              " annual_income, price, roi, created_at FROM buildings ORDER BY id"
              " DESC"
          )
          rows = cursor.fetchall()
          title_text = "تقرير قائمة البنايات الاستثمارية"

          # إنشاء محتوى HTML منسق وجميل للتقارير
          html_content = f"""
                    <!DOCTYPE html>
                    <html lang="ar" dir="rtl">
                    <head>
                        <meta charset="UTF-8">
                        <title>{title_text}</title>
                        <style>
                            body {{ font-family: Tahoma, Arial, sans-serif; background: #f9f9f9; color: #333; padding: 20px; }}
                            h1 {{ color: #1b3b36; text-align: center; }}
                            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; }}
                            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; font-size: 14px; }}
                            th {{ background-color: #1b3b36; color: white; }}
                            tr:nth-child(even) {{ background-color: #f2f2f2; }}
                        </style>
                    </head>
                    <body>
                        <h1>🏢 {title_text}</h1>
                        <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <table>
                            <tr>
                                <th>ID</th>
                                <th>العنوان</th>
                                <th>النوع</th>
                                <th>الموقع</th>
                                <th>الوحدات</th>
                                <th>الدخل الشهري</th>
                                <th>السعر</th>
                                <th>العائد %</th>
                            </tr>
                    """
          for r in rows:
            html_content += f"""
                            <tr>
                                <td>{r[0]}</td>
                                <td>{r[1]}</td>
                                <td>{r[2]}</td>
                                <td>{r[3]}</td>
                                <td>{r[4]}</td>
                                <td>{r[5]:,.2f} ر.ع</td>
                                <td>{r[7]:,.2f} ر.ع</td>
                                <td>{r[8]}%</td>
                            </tr>
                        """
          html_content += "</table></body></html>"
          file_name_base = "buildings_report"

        else:
          cursor.execute(
              "SELECT id, name, phone, email, country, preferred_location,"
              " max_budget, deal_status, created_at FROM buyers ORDER BY id"
              " DESC"
          )
          rows = cursor.fetchall()
          title_text = "تقرير قاعدة بيانات المستثمرين"

          html_content = f"""
                    <!DOCTYPE html>
                    <html lang="ar" dir="rtl">
                    <head>
                        <meta charset="UTF-8">
                        <title>{title_text}</title>
                        <style>
                            body {{ font-family: Tahoma, Arial, sans-serif; background: #f9f9f9; color: #333; padding: 20px; }}
                            h1 {{ color: #1b3b36; text-align: center; }}
                            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; }}
                            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: right; font-size: 14px; }}
                            th {{ background-color: #1b3b36; color: white; }}
                            tr:nth-child(even) {{ background-color: #f2f2f2; }}
                        </style>
                    </head>
                    <body>
                        <h1>👥 {title_text}</h1>
                        <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <table>
                            <tr>
                                <th>ID</th>
                                <th>الاسم الكريم</th>
                                <th>رقم الهاتف</th>
                                <th>الدولة</th>
                                <th>الموقع المفضل</th>
                                <th>الميزانية</th>
                                <th>الحالة</th>
                            </tr>
                    """
          for r in rows:
            html_content += f"""
                            <tr>
                                <td>{r[0]}</td>
                                <td>{r[1]}</td>
                                <td>{r[2]}</td>
                                <td>{r[4]}</td>
                                <td>{r[5]}</td>
                                <td>{r[6]:,.2f} ر.ع</td>
                                <td>{r[7]}</td>
                            </tr>
                        """
          html_content += "</table></body></html>"
          file_name_base = "investors_report"

        conn.close()

        if format_choice == "HTML":
          st.download_button(
              label="📥 تنزيل التقرير بصيغة HTML",
              data=html_content.encode("utf-8-sig"),
              file_name=f"{file_name_base}.html",
              mime="text/html",
          )
          st.success("✅ تم تجهيز تقرير HTML للتحميل الفوري!")
        else:
          # تنبيه في حال اختيار PDF لتوفير بديل سلس وعملي عبر المتصفح
          st.info(
              "📄 لتصدير التقرير كملف **PDF** فائق الجودة: قم بتحميل ملف الـ"
              " HTML أعلاه ثم افتحه في المتصفح واضغط (Ctrl + P) ثم اختر"
              " (حفظ كملف PDF)."
          )
          st.download_button(
              label="📥 تنزيل ملف التقرير للطباعة (HTML لـ PDF)",
              data=html_content.encode("utf-8-sig"),
              file_name=f"{file_name_base}_for_pdf.html",
              mime="text/html",
          )

      except Exception as ex_rep:
        st.error(f"خطأ أثناء توليد التقرير: {ex_rep}")

  elif admin_action == "💰 5. الإيرادات والعمولات":
    st.subheader("💰 إيرادات وعمولات صفقات البنايات")
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

  st.markdown("---")
  st.stop()


# ==========================================
# منصة الزوار الاحترافية للعملاء (الوجهة الرسمية)
# ==========================================
st.markdown(
    "<h1 style='text-align: center; color: #1b3b36; margin-bottom:"
    " 0;'>محفظة العروض العقارية الاستثمارية</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='text-align: center; color: #0e6251; font-weight: 400;"
    " margin-bottom: 30px;'>اختر فرصتك الاستثمارية القادمة بكل أمان واحترافية</h3>",
    unsafe_allow_html=True,
)

# شريط التصفية الاحترافي للعملاء
col_f1, col_f2 = st.columns([2, 2])
with col_f1:
  b_filter_type = st.selectbox(
      "🏢 تصفية صفقات البنايات حسب القطاع:",
      ["الكل", "سكنية", "تجارية", "صناعية"],
  )

st.markdown("---")

# جلب وعرض البنايات
public_buildings = []
try:
  conn = get_db_connection()
  cursor = conn.cursor()
  if b_filter_type == "الكل":
    cursor.execute(
        "SELECT id, title, type, location, units_count, monthly_income,"
        " annual_income, price, roi, created_at FROM buildings ORDER BY id DESC"
    )
  else:
    cursor.execute(
        "SELECT id, title, type, location, units_count, monthly_income,"
        " annual_income, price, roi, created_at FROM buildings WHERE type = ?"
        " ORDER BY id DESC",
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
            b_date,
        ) = b_item
        with cols[j]:
          whatsapp_msg = (
              f"مرحباً، أهتم بالاستفسار عن البناية ({b_title}) - نوع"
              f" ({b_type}) في ({b_loc}) بسعر ({b_price:,.2f} ر.ع) وعائد"
              f" ({b_roi}%)."
          )
          wa_link = f"https://wa.me/{COMPANY_WHATSAPP.replace('+', '').replace(' ', '')}?text={urllib.parse.quote(whatsapp_msg)}"

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
                        💵 الدخل الشهري: <b>{b_mincome if b_mincome else 0:,.2f} ر.ع</b> | السنوي: <b>{b_aincome if b_aincome else 0:,.2f} ر.ع</b><br>
                        📈 العائد السنوي (ROI): <b>~{b_roi if b_roi else 0}%</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 14px;">
                        <span style="color: #94a3b8; font-size: 12px;">🕒 أُضيف في: {b_date.split(' ')[0] if b_date else ''}</span>
                        <a href="{wa_link}" target="_blank" class="whatsapp-btn">💬 تواصل واتساب</a>
                    </div>
                </div>
            """,
              unsafe_allow_html=True,
          )
else:
  st.info("لا توجد بنايات استثمارية معروضة حالياً. يرجى العودة لاحقاً.")

# نموذج إرسال طلب المستثمر (متمركز في المنتصف)
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; margin-top: 40px; margin-bottom: 20px;">
        <h2 style="color: #1b3b36; font-weight: 800; margin-bottom: 10px;">📋 نموذج إبداء رغبة استثمارية وطلب عقار</h2>
        <p style="color: #64748b; font-size: 16px;">هل تبحث عن مواصفات محددة؟ اترك بياناتك وسيقوم فريق الوساطة بالتواصل معك فوراً بالفرص المناسبة:</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("client_inquiry_form"):
  col_c1, col_c2 = st.columns(2)
  with col_c1:
    c_name = st.text_input("الاسم الكريم:")
    c_phone = st.text_input("رقم الهاتف (مع مفتاح الدولة):", value="+968")
    c_country = st.text_input("الدولة / مكان الإقامة:", value="سلطنة عمان")
  with col_c2:
    c_loc = st.text_input("المنطقة أو الولاية المفضلة للاستثمار:")
    c_budget = st.number_input(
        "الميزانية التقديرية (ريال عماني):", value=300000.0, step=10000.0
    )
    c_email = st.text_input("البريد الإلكتروني (اختياري):")

  submit_client_request = st.form_submit_button("إرسال الطلب لفريق الوساطة")

  if submit_client_request and c_name and c_phone:
    try:
      conn = get_db_connection()
      cursor = conn.cursor()
      cursor.execute(
          """INSERT INTO buyers (name, phone, email, country, preferred_location, max_budget, deal_status, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
          (
              c_name,
              c_phone,
              c_email,
              c_country,
              c_loc,
              c_budget,
              "مهتم جديد",
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          ),
      )
      conn.commit()
      conn.close()
      st.success(
          "✅ تم إرسال طلبك بنجاح! سيتواصل معك مستشارنا العقاري في أقرب وقت."
      )
    except Exception as err:
      st.error(f"حدث خطأ أثناء إرسال الطلب: {err}")