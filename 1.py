# استبدل هذا الجزء حصرياً في القائمة الجانبية (Sidebar) في الكود لديك:

st.sidebar.markdown("### 🔐 الإدارة")

if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

if not st.session_state.authenticated:
  # استخدام Popover لجعلها زر صغير يفتح خانة الباسورد عند الضغط عليه فقط
  with st.sidebar.popover("🔑 دخول المشرف"):
    with st.form("admin_login_form"):
      password_input = st.text_input("كلمة المرور:", type="password")
      submit_login = st.form_submit_button("دخول")

      if submit_login:
        if password_input == ADMIN_PASSWORD:
          st.session_state.authenticated = True
          st.rerun()
        else:
          st.error("❌ خطأ")

  app_mode = "🌍 عرض منصة الزوار"
else:
  st.sidebar.success("🟢 مسجل")
  if st.sidebar.button("🚪 خروج"):
    st.session_state.authenticated = False
    st.rerun()

  app_mode = st.sidebar.radio(
      "اختر وضع العرض:",
      ["🌍 عرض منصة الزوار", "⚙️ لوحة تحكم الوسيط الذكي"],
  )