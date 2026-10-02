import streamlit as st

# كود إخفاء عناصر Streamlit
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {visibility: hidden !important;}
            /* إخفاء الشعار في الأسفل */
            .stApp [data-testid="stToolbar"] {visibility: hidden !important;}
            .stApp [data-testid="stDecoration"] {visibility: hidden !important;}
            .stApp [data-testid="stStatusWidget"] {visibility: hidden !important;}
            /* إخفاء علامة "Hosted with Streamlit" */
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
from datetime import datetime, timedelta
# ... باقي الكود الخاص بك

# دالة للتحقق من الكود
def check_activation():
    # كود التنشيط (يمكنك تغييره لاحقاً)
    SECRET_CODE = "MAS-2026" 
    
    # التحقق من الحالة في الجلسة (Session State)
    if 'activated' not in st.session_state:
        st.session_state.activated = False
        st.session_state.expiry_date = None

    if not st.session_state.activated:
        st.title("🔐 تفعيل نظام MAS-Guard")
        code = st.text_input("أدخل كود التفعيل:", type="password")
        
        if st.button("تفعيل"):
            if code == SECRET_CODE:
                st.session_state.activated = True
                # ضبط تاريخ الانتهاء بعد شهر من الآن
                st.session_state.expiry_date = datetime.now() + timedelta(days=30)
                st.success("تم التفعيل بنجاح! يعمل النظام لمدة 30 يوماً.")
                st.rerun()
            else:
                st.error("كود غير صحيح!")
        st.stop() # إيقاف البرنامج إذا لم يكن مفعلاً
    
    # التحقق من التاريخ
    if st.session_state.activated:
        if datetime.now() > st.session_state.expiry_date:
            st.warning("⚠️ انتهت فترة التنشيط، يرجى إدخال كود جديد.")
            st.session_state.activated = False
            st.rerun()

# استدعاء الدالة
check_activation()

# --- بقية كود تطبيقك يبدأ من هنا ---
st.title("مرحباً بك في نظام MAS-Guard")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from io import BytesIO
import requests

# استيراد مكتبات ReportLab لتوليد الـ PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# ==========================================
# 1. إعدادات الصفحة والمظهر العام (Dark Theme)
# ==========================================
# إعداد صفحة التطبيق بالهوية الجديدة
st.set_page_config(page_title="MAS-Guard ESP | System", page_icon="⚡", layout="wide")

# عرض اسم التطبيق بهوية ENG:Mohammad Ageel
st.markdown("""
    <style>
        .mas-header {
            background-color: #0e1117;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #333;
            border-top: 5px solid #ffc107;
            margin-bottom: 20px;
        }
        .brand-title {
            font-size: 26px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 5px;
        }
        .brand-desc {
            font-size: 14px;
            color: #a0a0a0;
            line-height: 1.5;
            max-width: 800px;
        }
        .signature {
            font-size: 12px;
            color: #ffc107;
            font-weight: bold;
            margin-top: 10px;
            text-transform: uppercase;
        }
    </style>
    <div class="mas-header">
        <div class="brand-title">⚡ MAS-GUARD | ESP SYSTEM</div>
        <div class="brand-desc">
            منصة تحليل بيانات المضخات الغاطسة الكهربائية (ESP) المتقدمة. توفر المراقبة الفورية، التشخيص الذكي للأعطال، وتحسين الإنتاج باستخدام معادلات تقييم التدفق (Vogel IPR) لضمان استمرارية التشغيل الآمن.
        </div>
        <div class="signature">© 2026 ARCHITECTED BY ENG. MOHAMMED AJEEL SULEIMAN (MAS)</div>
    </div>
""", unsafe_allow_html=True)

# إضافة تأثيرات المظهر المتقدمة والوميض عبر CSS
st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0; } }
    .blink-arrow { animation: blinker 1s linear infinite; display: inline-block; margin-left: 5px; }
    .normal-arrow { display: inline-block; margin-left: 5px; }
    
    @keyframes ambulance-flash {
        0% { background-color: rgba(220, 53, 69, 0.35); }
        50% { background-color: rgba(0, 123, 255, 0.35); }
        100% { background-color: rgba(220, 53, 69, 0.35); }
    }
    .ambulance-active {
        animation: ambulance-flash 0.4s infinite;
        padding: 15px;
        border-radius: 10px;
        border: 3px solid #dc3545;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. دالة تشغيل صفارة الإنذار (تمت تصفية أي مكتبات مفقودة)
# ==========================================
def play_siren_sound():
    """تشغيل صفارة إنذار إسعاف حقيقية ترددية مباشرة عبر المتصفح بدون مكتبات خارجية"""
    siren_js = """
    <script>
    if (typeof window.audioCtx === 'undefined') {
        window.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (typeof window.sirenInterval === 'undefined') {
        let osc = window.audioCtx.createOscillator();
        let gainNode = window.audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(600, window.audioCtx.currentTime); 
        window.sirenInterval = setInterval(function() {
            let time = window.audioCtx.currentTime;
            osc.frequency.linearRampToValueAtTime(900, time + 0.4);
            osc.frequency.linearRampToValueAtTime(600, time + 0.8);
        }, 800);
        gainNode.gain.setValueAtTime(0.15, window.audioCtx.currentTime); 
        osc.connect(gainNode);
        gainNode.connect(window.audioCtx.destination);
        osc.start();
        window.oscillatorNode = osc;
        window.gainNode = gainNode;
    }
    </script>
    """
    st.components.v1.html(siren_js, height=0, width=0)

# ==========================================
# 3. دالة إرسال الإشعارات عبر Telegram Bot
# ==========================================
def send_telegram_alert(well_name, status_list, details):
    bot_token = "8332791768:AAFLbetgy2bhr8fKE_ByiZLB49BTQRmpwKI"
    chat_id = "1607965956"
    status_text = " | ".join(status_list)
    text_message = f"🚨 ALERT: ESP Multiple Critical Failures\n-----------------------------------\nالبئر المستهدفة: {well_name}\nنوع التنبيهات المرصودة: {status_text}\nالتوقيت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nتفاصيل القراءات الفورية:\n{details}\n\nالرجاء اتخاذ الإجراءات التصحيحية فوراً لجميع المشاكل."
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text_message}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception:
        return False

# ==========================================
# 4. إدارة حالة التشغيل وسجل التنبؤات والأحداث
# ==========================================
if "stream_running" not in st.session_state:
    st.session_state.stream_running = True
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "history_log" not in st.session_state:
    st.session_state.history_log = []
if "last_alert_sent" not in st.session_state:
    st.session_state.last_alert_sent = None
if "event_alerts" not in st.session_state:
    st.session_state.event_alerts = [] 

# ==========================================
# 5. لوحة التحكم الجانبية المنظمة (Sidebar)
# ==========================================
st.sidebar.header("📡 بوابة ربط قراءات الحقل")

selected_well = st.sidebar.selectbox(
    "اختر البئر المستهدفة للمراقبة:",
    ["Well-01 (High GOR)", "Well-02 (Water Shut-off)", "Well-03 (Sand Risk)"]
)

with st.sidebar.expander("📲 إعدادات الاتصال والأمان الفوري", expanded=True):
    enable_telegram = st.checkbox("تفعيل نظام تنبيهات Telegram التلقائي", value=True)
    enable_audio = st.checkbox("🔊 تفعيل صفارات الإنذار الصوتية (Siren)", value=True)

if "Well-01" in selected_well:
    max_safe_temp = 240.0; base_reservoir_pressure = 3200.0; pi_index = 1.5; q_design = 2500.0
    norm_dp = (1400.0, 1800.0); norm_pip = (600.0, 1000.0); norm_pdp = (2200.0, 2800.0)
    norm_amps = (40.0, 55.0); norm_freq = (45.0, 60.0); norm_temp = (150.0, 220.0)
    norm_wh = (200.0, 400.0); norm_eff = (55.0, 80.0)
elif "Well-02" in selected_well:
    max_safe_temp = 220.0; base_reservoir_pressure = 2800.0; pi_index = 2.2; q_design = 3000.0
    norm_dp = (1200.0, 1600.0); norm_pip = (500.0, 900.0); norm_pdp = (2000.0, 2600.0)
    norm_amps = (35.0, 50.0); norm_freq = (40.0, 55.0); norm_temp = (140.0, 210.0)
    norm_wh = (150.0, 350.0); norm_eff = (50.0, 75.0)
else:
    max_safe_temp = 250.0; base_reservoir_pressure = 3500.0; pi_index = 0.9; q_design = 1500.0
    norm_dp = (1600.0, 2200.0); norm_pip = (700.0, 1100.0); norm_pdp = (2500.0, 3200.0)
    norm_amps = (45.0, 65.0); norm_freq = (50.0, 65.0); norm_temp = (160.0, 230.0)
    norm_wh = (250.0, 450.0); norm_eff = (55.0, 85.0)

with st.sidebar.expander("🎛️ إدارة تشغيل ومصدر البيانات", expanded=True):
    connection_mode = st.radio(
        "اختر مصدر بيانات النظام:",
        ["🎛️ محاكاة يدوية (Manual Sliders)", "🌐 بث حي من ملف بيانات الحقل (Field Data Stream)"]
    )

data_loaded = False
frequency, pip, pdp, current_base, noise_level = 50.0, 844.0, 2459.0, 44.7, "طبيعي (Normal)"
motor_temp, wellhead_press, pump_eff = 225.8, 369.0, 61.8

if connection_mode == "🌐 بث حي من ملف بيانات الحقل (Field Data Stream)":
    uploaded_file = st.sidebar.file_uploader("اختر ملف قراءات الـ ESP بصيغة CSV:", type=["csv"])
    if uploaded_file is not None:
        st.sidebar.success(f"✅ تم ربط تدفق بيانات {selected_well}")
        col_btn1, col_btn2 = st.sidebar.columns(2)
        with col_btn1:
            if st.button("▶️ تشغيل البث", use_container_width=True): st.session_state.stream_running = True; st.rerun()
        with col_btn2:
            if st.button("⏸️ إيقاف البث", use_container_width=True): st.session_state.stream_running = False; st.rerun()
            
        step_speed = st.sidebar.slider("معدل تخطي البيانات (قراءة / ثانية):", 1, 20, 1)
        df_field = pd.read_csv(uploaded_file)
        total_rows = len(df_field)
        
        if st.session_state.stream_running:
            refresh_count = st_autorefresh(interval=1000, key="esp_pro_stream_v15")
            st.session_state.current_index = (refresh_count * step_speed) % total_rows
            
        current_data = df_field.iloc[st.session_state.current_index]
        frequency = float(current_data['FREQ']) if 'FREQ' in current_data else 50.0
        pip = float(current_data['PIP']) if 'PIP' in current_data else 844.0
        pdp = float(current_data['PDP']) if 'PDP' in current_data else 2459.0
        current_base = float(current_data['AMPS']) if 'AMPS' in current_data else 44.7
        motor_temp = float(current_data['MOTOR_TEMP']) if 'MOTOR_TEMP' in current_data else 225.8
        wellhead_press = float(current_data['P_WH']) if 'P_WH' in current_data else 369.0
        pump_eff = float(current_data['EFF']) if 'EFF' in current_data else 61.8
        noise_level = str(current_data['NOISE']) if 'NOISE' in current_data else "طبيعي (Normal)"
        data_loaded = True
else:
    with st.sidebar.expander("🛠️ السلايدرات اليدوية لقراءات البئر", expanded=True):
        frequency = st.slider("تردد المضخة (VSD Frequency - Hz)", 30.0, 80.0, 50.0, 0.5)
        pip = st.slider("ضغط سحب المضخة (PIP - psi)", 0.0, 2000.0, 844.0, 1.0)
        pdp = st.slider("ضغط طرد المضخة (PDP - psi)", 500.0, 5000.0, 2459.0, 1.0)
        current_base = st.slider("تيار المحرك الأساسي (Motor Amps)", 10.0, 100.0, 44.7, 0.1)
        motor_temp = st.slider("درجة حرارة المحرك السفلية (Motor Temp - °F)", 100.0, 350.0, 225.8, 0.1)
        wellhead_press = st.slider("ضغط رأس البئر السطحي (P_wh - psi)", 50.0, 1000.0, 369.0, 1.0)
        pump_eff = st.slider("كفاءة المضخة الهيدروليكية (Efficiency %)", 10.0, 100.0, 61.8, 0.1)
        noise_level = st.selectbox("مستوى تذبذب التيار", ["طبيعي (Normal)", "متوسط (Moderate)", "عالي جداً (Critical Fluctuation)"])
    data_loaded = True
   # ==========================================
# قسم التحكم بالحدود الدنيا والعليا لجميع المؤشرات
# ==========================================
with st.sidebar.expander("⚙️ تخصيص حدود الإنذار للمؤشرات", expanded=True):
    st.markdown("حدد النطاق الآمن (الأدنى والأعلى) لكل مؤشر:")
    
    # 1. تردد المِفخة
    st.markdown("---")
    st.text("1. تردد المِفخة (VSD Frequency - Hz)")
    freq_min = st.slider("الأدنى - تردد", 30.0, 60.0, 45.0, key="freq_min")
    freq_max = st.slider("الأعلى - تردد", 60.0, 80.0, 75.0, key="freq_max")
    
    # 2. ضغط سحب المضخة (PIP - psi)
    st.markdown("---")
    st.text("2. ضغط سحب المضخة (PIP - psi)")
    pip_min = st.slider("الأدنى - سحب", 0.0, 1000.0, 200.0, key="pip_min")
    pip_max = st.slider("الأعلى - سحب", 1000.0, 2500.0, 1800.0, key="pip_max")
    
    # 3. ضغط طرد المضخة (PDP - psi)
    st.markdown("---")
    st.text("3. ضغط طرد المضخة (PDP - psi)")
    pdp_min = st.slider("الأدنى - طرد", 500.0, 2500.0, 1000.0, key="pdp_min")
    pdp_max = st.slider("الأعلى - طرد", 2500.0, 5000.0, 4000.0, key="pdp_max")
    
    # 4. تيار المحرك الأساسي (Motor Amps)
    st.markdown("---")
    st.text("4. تيار المحرك الأساسي (Motor Amps)")
    motor_amps_min = st.slider("الأدنى - التيار", 10.0, 50.0, 20.0, key="motor_amps_min")
    motor_amps_max = st.slider("الأعلى - التيار", 50.0, 120.0, 90.0, key="motor_amps_max")
    
    # 5. درجة حرارة المحرك السفلية (Motor Temp - °F)
    st.markdown("---")
    st.text("5. حرارة المحرك السفلية (Motor Temp - °F)")
    motor_temp_min = st.slider("الأدنى - الحرارة", 50.0, 150.0, 100.0, key="motor_temp_min")
    motor_temp_max = st.slider("الأعلى - الحرارة", 150.0, 250.0, 220.0, key="motor_temp_max")
    
    # 6. ضغط رأس البئر السطحي (P_wh - psi)
    st.markdown("---")
    st.text("6. ضغط رأس البئر السطحي (P_wh - psi)")
    pwh_min = st.slider("الأدنى - رأس البئر", 50.0, 500.0, 200.0, key="pwh_min")
    pwh_max = st.slider("الأعلى - رأس البئر", 500.0, 2000.0, 1500.0, key="pwh_max")
    
    # 7. كفاءة المضخة الهيدروليكية (Efficiency %)
    st.markdown("---")
    st.text("7. كفاءة المضخة الهيدروليكية (Efficiency %)")
    eff_min = st.slider("الأدنى - الكفاءة", 10.0, 50.0, 30.0, key="eff_min")
    eff_max = st.slider("الأعلى - الكفاءة", 50.0, 100.0, 85.0, key="eff_max")
# ==========================================
# 6. محرك التشخيص الهندسي (مُصحح وموحد)
# ==========================================
if data_loaded:
    delta_p = pdp - pip
    trigger_alert = False
    is_critical = False

    def get_scada_style(value, limits):
        low_limit, high_limit = limits
        margin = 5.0
        if value > high_limit:
            return "rgba(220, 53, 69, 0.2)", "#dc3545", "▲", "blink-arrow"
        elif value > (high_limit - margin):
            return "rgba(255, 193, 7, 0.2)", "#ffc107", "▲", "normal-arrow"
        elif value < low_limit:
            return "rgba(255, 193, 7, 0.2)", "#ffc107", "▼", "blink-arrow"
        elif value < (low_limit + margin):
            return "rgba(111, 66, 193, 0.1)", "#6f42c1", "▼", "normal-arrow"
        else:
            return "#1e2430", "#28a745", "➔", "normal-arrow"

    # تعريف وتحديث حالة الأنماط لجميع المؤشرات
    dp_bg, dp_color, dp_arrow, dp_class = get_scada_style(delta_p, norm_dp)
    pip_bg, pip_color, pip_arrow, pip_class = get_scada_style(pip, norm_pip)
    pdp_bg, pdp_color, pdp_arrow, pdp_class = get_scada_style(pdp, norm_pdp)
    amps_bg, amps_color, amps_arrow, amps_class = get_scada_style(current_base, norm_amps)
    freq_bg, freq_color, freq_arrow, freq_class = get_scada_style(frequency, norm_freq)
    temp_bg, temp_color, temp_arrow, temp_class = get_scada_style(motor_temp, norm_temp)
    wh_bg, wh_color, wh_arrow, wh_class = get_scada_style(wellhead_press, norm_wh)
    eff_bg, eff_color, eff_arrow, eff_class = get_scada_style(pump_eff, norm_eff)

    active_diagnostics = []
    # (هنا يمكنك إضافة منطق الـ rules الخاص بك كما كان سابقاً)

    diagnostic_status = " | ".join(active_diagnostics) if active_diagnostics else "طبيعية (مستقرة)"
    
    # تحديد لون شريط الحالة العام لضمان عدم وجود NameError
    if is_critical:
        status_color = "#dc3545"
    elif active_diagnostics:
        status_color = "#ffc107"
    else:
        status_color = "#28a745"
    active_diagnostics = []
    active_recommendations = []

    rules = [
        {"name": "تردد VSD", "val": frequency, "limits": norm_freq, "unit": "Hz",
         "low": {"diag": "ركود السوائل", "act": "زيادة التردد لتعزيز الجريان."},
         "high": {"diag": "إجهاد ميكانيكي حاد", "act": "خفض التردد لمنع انهيار المراحل."}},
        {"name": "حرارة المحرك", "val": motor_temp, "limits": norm_temp, "unit": "°F",
         "low": {"diag": "تبريد مفرط", "act": "فحص حساس الحرارة."},
         "high": {"diag": "خطر احتراق ملفات المحرك", "act": "إيقاف طارئ فوري (SOP). ممنوع التشغيل حتى تبرد تحت 160°F."}},
        {"name": "ضغط السحب PIP", "val": pip, "limits": norm_pip, "unit": "psi",
         "low": {"diag": "خطر التكهف", "act": "تقليل معدل الضخ لتعويض الضغط."},
         "high": {"diag": "ضغط دخول مرتفع", "act": "فحص صمام الخنق (Choke)."}},
        {"name": "تيار المحرك", "val": current_base, "limits": norm_amps, "unit": "A",
         "low": {"diag": "تحميل منخفض", "act": "فحص احتمالية وجود غاز."},
         "high": {"diag": "حمل زائد", "act": "فحص وجود رمال أو تآكل."}}
    ]

    for r in rules:
        if r["val"] < r["limits"][0]:
            trigger_alert = True
            active_diagnostics.append(f"انخفاض {r['name']}")
            active_recommendations.append({"title": f"توصية: {r['name']}", "diagnosis": r["low"]["diag"], "action": r["low"]["act"]})
        elif r["val"] > r["limits"][1]:
            trigger_alert = True; is_critical = True
            active_diagnostics.append(f"ارتفاع {r['name']}")
            active_recommendations.append({"title": f"تحذير: {r['name']}", "diagnosis": r["high"]["diag"], "action": r["high"]["act"]})

    diagnostic_status = " | ".join(active_diagnostics) if active_diagnostics else "طبيعية (مستقرة)"
    status_color = "#dc3545" if is_critical else "#ffc107" if active_diagnostics else "#28a745"

    if trigger_alert:
        current_time_str = datetime.now().strftime("%H:%M:%S")
        for diag in active_diagnostics:
            if not st.session_state.event_alerts or st.session_state.event_alerts[0]["التنبيه"] != diag:
                st.session_state.event_alerts.insert(0, {"التوقيت": current_time_str, "البئر": selected_well, "التنبيه": diag, "درجة الخطورة": "عالية 🔴" if is_critical else "متوسطة 🟡"})
    
    if is_critical and enable_audio: play_siren_sound()
    if trigger_alert and enable_telegram and st.session_state.last_alert_sent != diagnostic_status:
        send_telegram_alert(selected_well, active_diagnostics, f"Status: {diagnostic_status}")
        st.session_state.last_alert_sent = diagnostic_status
    elif not trigger_alert: st.session_state.last_alert_sent = None

    noise_level_map = {"عالي جداً (Critical Fluctuation)": ("rgba(220, 53, 69, 0.2)", "#dc3545", "▲", "blink-arrow", "عالي جداً ⚠️"), "متوسط (Moderate)": ("rgba(255, 193, 7, 0.15)", "#ffc107", "▲", "blink-arrow", "متوسط ⚡")}
    noise_bg, noise_display_color, noise_arrow, noise_class, noise_text_arabic = noise_level_map.get(noise_level, ("#1e2430", "#28a745", "➔", "normal-arrow", "طبيعي ✅"))
    # ==========================================
# 7. التبويبات الـ 5 المحدثة والمعزولة كلياً
# ==========================================
st.markdown("""
    <style>
        .stTabs [data-baseweb="tab-list"] { gap: 5px; display: flex; justify-content: center; }
        .stTabs [data-baseweb="tab"] {
            background-color: #000000; 
            color: #ffffff;
            border-radius: 8px;
            padding: 15px 20px;
            font-size: 16px;
            font-weight: bold;
            border: 1px solid #333;
            transition: all 0.3s ease;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffc107 !important; 
            color: #000000 !important;
            border: 1px solid #ffc107 !important;
        }
    </style>
""", unsafe_allow_html=True)

tab_monitor, tab_production, tab_logs, tab_schematic, tab_reports, tab_pump_curve, tab_about = st.tabs([
    "🎛️ شاشة المراقبة", 
    "🛢️ الإنتاج اليومي",
    "📋 سجل الإنذارات",
    "📐 المخطط الهيكلي",
    "📄 التقارير",
    "⚙️ منحنى الأداء",
    "ℹ️ حول النظام"
])

# ------------------------------------------
# التبويبة الأولى: شاشة المراقبة الفورية الحية
# ------------------------------------------
with tab_monitor:
    div_class = "ambulance-active" if is_critical else ""
    div_bg = f"background-color:{status_color};" if not is_critical else ""
    
    st.markdown(f"""
        <div class="{div_class}" style="{div_bg} padding:15px; border-radius:8px; text-align:center; margin-bottom:20px;">
            <h2 style="color:white; margin:0; font-size:22px;">⚡ نظام الطوارئ والتحليل الذكي المتعدد لـ {selected_well} ⚡</h2>
            <p style="color:white; margin:5px 0 0 0; font-size:16px;">المشاكل النشطة حالياً: {diagnostic_status}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not active_recommendations:
        st.success("🟢 حالة التشغيل الآمن: جميع القراءات الحالية متطابقة تماماً مع النطاق التصميمي الآمن للبئر. لا توجد إجراءات تصحيحية مطلوبة.")
    else:
        st.markdown(f"### 🚨 تم رصد عدد ({len(active_recommendations)}) مشاكل متزامنة تتطلب المتابعة الفورية:")
        
        for idx, rec in enumerate(active_recommendations, 1):
            border_color = "#dc3545" if is_critical else "#ffc107"
            
            st.markdown(f"""
            <div style="background-color: #131722; padding: 20px; border-radius: 8px; border-right: 6px solid {border_color}; margin-bottom: 20px; direction: rtl; text-align: right; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                <div style="font-size: 18px; font-weight: bold; color: #e0e0e0; margin-bottom: 12px; border-bottom: 1px solid #2a2f3a; padding-bottom: 6px;">
                    ⚠️ مشكلة رقم ({idx}): {rec['title']}
                </div>
                <div style="font-size: 15px; color: #b2b9c4; margin-bottom: 8px;">
                    <strong style="color: #ff9800;">🔍 التشخيص الهندسي:</strong> {rec['diagnosis']}
                </div>
                <div style="font-size: 15px; color: #b2b9c4;">
                    <strong style="color: #00e676;">🛠️ الإجراء الفوري المعتمد (SOP):</strong> {rec['action']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    row1_1, row1_2, row1_3, row1_4, row1_5 = st.columns(5)
    with row1_1: 
        st.markdown(f"""<div style="background-color:{dp_bg}; padding:12px; border-radius:10px; border-left: 5px solid {dp_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">معدل رفع الضغط (ΔP)</p>
            <h2 style="color:{dp_color}; margin:10px 0 0 0; font-size:22px;">{delta_p:,.0f} <span style="font-size:12px;">psi</span> <span class="{dp_class}">{dp_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)
    with row1_2: 
        st.markdown(f"""<div style="background-color:{pip_bg}; padding:12px; border-radius:10px; border-left: 5px solid {pip_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">ضغط سحب المضخة (PIP)</p>
            <h2 style="color:{pip_color}; margin:10px 0 0 0; font-size:22px;">{pip:,.0f} <span style="font-size:12px;">psi</span> <span class="{pip_class}">{pip_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)
    with row1_3: 
        st.markdown(f"""<div style="background-color:{pdp_bg}; padding:12px; border-radius:10px; border-left: 5px solid {pdp_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">ضغط طرد المضخة (PDP)</p>
            <h2 style="color:{pdp_color}; margin:10px 0 0 0; font-size:22px;">{pdp:,.0f} <span style="font-size:12px;">psi</span> <span class="{pdp_class}">{pdp_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)
    with row1_4: 
        st.markdown(f"""<div style="background-color:{amps_bg}; padding:12px; border-radius:10px; border-left: 5px solid {amps_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">تيار المحرك (Amps)</p>
            <h2 style="color:{amps_color}; margin:10px 0 0 0; font-size:22px;">{current_base:,.1f} <span style="font-size:12px;">A</span> <span class="{amps_class}">{amps_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)
    with row1_5: 
        st.markdown(f"""<div style="background-color:{freq_bg}; padding:12px; border-radius:10px; border-left: 5px solid {freq_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">تردد مغير السرعة (VSD)</p>
            <h2 style="color:{freq_color}; margin:10px 0 0 0; font-size:22px;">{frequency:,.1f} <span style="font-size:12px;">Hz</span> <span class="{freq_class}">{freq_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin:10px 0;'></div>", unsafe_allow_html=True)

    row2_1, row2_2, row2_3, row2_4 = st.columns(4)
    with row2_1: 
        st.markdown(f"""<div style="background-color:{temp_bg}; padding:12px; border-radius:10px; border-left: 5px solid {temp_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">🌡️ حرارة المحرك السفلية</p>
            <h2 style="color:{temp_color}; margin:10px 0 0 0; font-size:22px;">{motor_temp:,.1f} <span style="font-size:12px;">°F</span> <span class="{temp_class}">{temp_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)
    with row2_2: 
        st.markdown(f"""<div style="background-color:{wh_bg}; padding:12px; border-radius:10px; border-left: 5px solid {wh_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">🛑 ضغط رأس البئر السطحي</p>
            <h2 style="color:{wh_color}; margin:10px 0 0 0; font-size:22px;">{wellhead_press:,.0f} <span style="font-size:12px;">psi</span> <span class="{wh_class}">{wh_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)
    with row2_3: 
        st.markdown(f"""<div style="background-color:{eff_bg}; padding:12px; border-radius:10px; border-left: 5px solid {eff_color}; text-align:center;">
            <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">⚙️ كفاءة المضخة الهيدروليكية</p>
            <h2 style="color:{eff_color}; margin:10px 0 0 0; font-size:22px;">{pump_eff:,.1f} <span style="font-size:12px;">%</span> <span class="{eff_class}">{eff_arrow}</span></h2>
        </div>""", unsafe_allow_html=True)
    with row2_4: 
            st.markdown(f"""
                <div style="background-color:{noise_bg}; padding:12px; border-radius:10px; border-left: 5px solid {noise_display_color}; text-align:center;">
                    <p style="color:#8a99ad; margin:0; font-size:12px; font-weight:bold;">📈 مستوى تذبذب التيار</p>
                    <h2 style="color:{noise_display_color}; margin:10px 0 0 0; font-size:20px;">{noise_text_arabic} <span class="{noise_class}">{noise_arrow}</span></h2>
                </div>
            """, unsafe_allow_html=True)
            
            

    # هنا الحل: اجعل هذه الأسطر محاذية لبداية سطر "row1_1" (أي تحت الـ with مباشرة)
   # 1. إغلاق أي بلوكات سابقة (تأكد أن سطر الأعمدة يبدأ في بداية السطر)
    col_m1, col_m2 = st.columns([2, 1])
    
    # 2. إذا كنت تريد وضع معلومات داخل الأعمدة، ضعها هنا، وإلا احذف الأعمدة تماماً
    with col_m1:
        st.write("بيانات جانبية أو ملاحظات")
        
    # 3. هنا الخط الفاصل (يجب أن يكون محاذياً لسطر مع تعريف الـ with أو الأعمدة)
    st.markdown("---")
    
    # 4. كود الرسم البياني (بعرض كامل) - يجب أن يكون بمحاذاة سطر الأعمدة تماماً
    st.subheader("📈 المنحنى اللحظي المستمر لقراءات تيار السحب والضغوط")
    
    np.random.seed(42)
    time_chunks = [datetime.now() - timedelta(minutes=i*5) for i in range(30, 0, -1)]
    current_noise = np.random.normal(0, 0.4, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_chunks, y=current_base + current_noise, name="تيار المحرك (Amps)", line=dict(color="#1f77b4", width=3)))
    fig.add_trace(go.Scatter(x=time_chunks, y=np.random.normal(pip, 5, 30), name="ضغط السحب (PIP - psi)", line=dict(color="#ff7f0e", width=3), yaxis="y2"))
    
    fig.update_layout(
        template="plotly_dark",
        height=500,
        yaxis=dict(title="تيار المحرك (Amps)"),
        yaxis2=dict(title="ضغط السحب (psi)", overlaying="y", side="right"),
        margin=dict(l=40, r=40, t=20, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------
    # التبويبة الثانية: توقعات الإنتاج اليومي (Vogel IPR)
    # ------------------------------------------
    with tab_production:
        st.subheader("🛢️ التقييم الهيدروليكي التفاعلي للإنتاج اليومي المتوقع")
        st.markdown("##### ⚙️ لوحة محاكاة المستودع التفاعلية:")
        res_pressure_slider = st.slider("عدّل ضغط المستودع الثابت الحالي ($P_R$ - psi) لمعاينة التغير:", float(base_reservoir_pressure * 0.6), float(base_reservoir_pressure * 1.4), float(base_reservoir_pressure), 50.0)
        
        q_max_dynamic = pi_index * res_pressure_slider / 1.8
        ratio_dynamic = pip / res_pressure_slider
        vogel_eff_dynamic = (1.0 - 0.2 * ratio_dynamic - 0.8 * (ratio_dynamic ** 2)) if ratio_dynamic < 1 else 0.0
        estimated_flow_dynamic = q_max_dynamic * vogel_eff_dynamic if ratio_dynamic < 1 else 0.0

        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            st.markdown(f"""
                <div style="background-color:#1a1f2c; padding:25px; border-radius:10px; border-top: 5px solid #ff7f0e; text-align:center; margin-top:15px;">
                    <p style="color:#8a99ad; margin:0; font-size:14px; font-weight:bold;">معدل التدفق التقديري المحسوب</p>
                    <h1 style="color:#ff7f0e; margin:15px 0; font-size:38px; font-weight:bold;">{estimated_flow_dynamic:,.0f}</h1>
                    <p style="color:#ff7f0e; margin:0; font-size:16px; font-weight:bold;">STB/Day (برميل/يوم)</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_p2:
            st.markdown("#### 🔬 المعادلة التصميمية المعتمدة (Vogel's Inflow Performance Relationship):")
            st.latex(r"Q = Q_{max} \cdot \left[ 1 - 0.2 \cdot \left( \frac{PIP}{P_R} \right) - 0.8 \cdot \left( \frac{PIP}{P_R} \right)^2 \right]")

        st.markdown("---")
        pip_range = np.linspace(0, res_pressure_slider, 40)
        q_vogel_range = q_max_dynamic * (1.0 - 0.2 * (pip_range/res_pressure_slider) - 0.8 * (pip_range/res_pressure_slider)**2)
        fig_ipr = go.Figure()
        fig_ipr.add_trace(go.Scatter(x=q_vogel_range, y=pip_range, name="منحنى التدفق (Vogel IPR)", line=dict(color="#28a745", width=3)))
        fig_ipr.add_trace(go.Scatter(x=[estimated_flow_dynamic], y=[pip], mode="markers+text", name="نقطة الفلو", text=["📍 معدل التدفق الفوري"], textposition="top right", marker=dict(size=14, color="#ff7f0e", symbol="circle", line=dict(color="white", width=2))))
        fig_ipr.update_layout(template="plotly_dark", xaxis_title="معدل الإنتاج اليومي (STB/Day)", yaxis_title="ضغط سحب تدفق القاع (PIP - psi)", margin=dict(l=40, r=40, t=20, b=40))
        st.plotly_chart(fig_ipr, use_container_width=True)

    # ------------------------------------------
    # التبويبة الثالثة: المخطط الهيكلي للبئر
    # ------------------------------------------
    with tab_schematic:
        st.subheader("📐 المخطط الهيكلي الهندسي وجوف البئر التفاعلي (Wellbore Schematic)")
        fig_well = go.Figure()
        fig_well.add_trace(go.Scatter(x=[-2, -2, 2, 2], y=[0, -4000, -4000, 0], mode='lines', name='Casing', line=dict(color='gray', width=3, dash='dash')))
        fig_well.add_trace(go.Scatter(x=[-0.8, -0.8, 0.8, 0.8], y=[0, -3000, -3000, 0], mode='lines', name='Tubing', line=dict(color='lightblue', width=2)))
        
        pump_color_visual = 'red' if is_critical else 'green'
        pump_status_text_visual = 'Critical Alert' if is_critical else 'Normal Operation'
        
        fig_well.add_trace(go.Scatter(x=[-0.7, 0.7, 0.7, -0.7, -0.7], y=[-3000, -3000, -3300, -3300, -3300], fill="toself", fillcolor=pump_color_visual, mode='lines+text', name='ESP Pump', text=["", f"ESP Status: {pump_status_text_visual}"], textposition="bottom center", line=dict(color='white', width=1)))
        fig_well.add_trace(go.Scatter(x=[-2, -1.5, None, 1.5, 2], y=[-3700, -3700, None, -3700, -3700], mode='markers+lines', name='Perforations', marker=dict(symbol='x', color='orange', size=8)))
        
        fig_well.update_layout(
            template="plotly_dark", 
            xaxis=dict(visible=False, range=[-5, 5]), 
            yaxis=dict(title="Vertical Depth - ft", range=[-4200, 200]), 
            height=500, 
            showlegend=True, 
            margin=dict(l=20, r=20, t=10, b=10)
        )
        st.plotly_chart(fig_well, use_container_width=True)

    # ------------------------------------------
    # التبويبة الرابعة: ملخص التقرير الهندسي للإدارة
    # ------------------------------------------
    with tab_reports:
        st.subheader("📄 مسودة التقرير الهندسي الفوري الجاهز للإرسال:")
        report_content = f"""======================================================================
                  REPORT: ESP SMART-GUARD OPERATIONAL SUMMARY
======================================================================
Well Identifier        : {selected_well}
Report Generated On    : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Current Diagnostics    : {diagnostic_status}
----------------------------------------------------------------------
KEY PARAMETERS RECORDED:
- Operating Frequency  : {frequency:.1f} Hz
- Motor Amperage       : {current_base:.1f} Amps
- Downhole Temp        : {motor_temp:.1f} °F
- Total Pressure Lift  : {delta_p:,.0f} psi
- Estimated Inflow     : {estimated_flow_dynamic:,.0f} STB/Day
======================================================================
"""
        st.code(report_content, language="text")
        
        def generate_pdf_bytes(text_content):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()
            custom_style = ParagraphStyle('ReportStyle', parent=styles['Normal'], fontName='Courier', fontSize=10, leading=14, alignment=TA_LEFT)
            lines = text_content.split('\n')
            for line in lines:
                formatted_line = line.replace(' ', '&nbsp;')
                if formatted_line.strip() == '': story.append(Spacer(1, 10))
                else: story.append(Paragraph(formatted_line, custom_style))
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        pdf_data = generate_pdf_bytes(report_content)
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(label="📥 تصدير وتحميل التقرير كملف PDF معتمد", data=pdf_data, file_name=f"ESP_Report_{selected_well.replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)

    # ------------------------------------------
    # التبويبة الخامسة: منحنى أداء المضخة الهيدروليكي
    # ------------------------------------------
    with tab_pump_curve:
        st.subheader("📈 خريطة ميزان أداء وعمل المضخة السحابي (ESP Pump Curve)")
        q_range = np.linspace(0, q_design * 1.6, 50)
        head_design = delta_p * (1.2 - 0.4 * (q_range / q_design)**2)
        q_min_safe, q_max_safe = q_design * 0.8, q_design * 1.1
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(x=q_range, y=head_design, name="Performance Curve (H-Q)", line=dict(color="#1f77b4", width=3)))
        fig_curve.add_vrect(x0=q_min_safe, x1=q_max_safe, fillcolor="#28a745", opacity=0.15, line_width=0)
        fig_curve.add_trace(go.Scatter(x=[estimated_flow_dynamic], y=[delta_p], mode="markers+text", name="Operating Point", text=["📍 Operating Point"], textposition="top right", marker=dict(size=15, color="#ff7f0e", symbol="diamond", line=dict(color="white", width=2))))
        fig_curve.update_layout(template="plotly_dark", xaxis_title="Production Flowrate (STB/Day)", yaxis_title="Total Lift Pressure (ΔP - psi)", margin=dict(l=40, r=40, t=20, b=40))
        st.plotly_chart(fig_curve, use_container_width=True)
        # ------------------------------------------
    # التبويبة السادسة: سجل الإنذارات المستقل
    # ------------------------------------------
    with tab_logs:
        st.subheader("📋 سجل الأحداث والإنذارات التاريخي (Detailed Event Log)")
        if st.session_state.event_alerts:
            df_alerts = pd.DataFrame(st.session_state.event_alerts)
            # عرض السجل مع تنسيق كامل للجدول
            st.dataframe(df_alerts, use_container_width=True, hide_index=True)
            
            # إضافة زر لمسح السجل إذا أردت
            if st.button("🗑️ مسح سجل الإنذارات"):
                st.session_state.event_alerts = []
                st.rerun()
        else:
            st.success("🟢 سجل الأحداث فارغ، النظام يعمل ضمن النطاق الآمن.")
            # ------------------------------------------
# التبويبة السابعة: حول النظام (حقوق الملكية)
# ------------------------------------------
with tab_about:
    st.subheader("ℹ️ معلومات النظام وحقوق الملكية")
    st.markdown("""
        <div style="background-color: #131722; padding: 25px; border-radius: 10px; border: 1px solid #ffc107;">
            <h3 style="color: #ffc107;">MAS-Guard ESP System | Version 1.0</h3>
            <p style="color: #e0e0e0;">هذا البرنامج هو نتاج عمل هندسي وفكري متكامل، تم تطويره بالكامل بواسطة <strong>المهندس محمد عجيل سليمان (MAS)</strong>.</p>
            <hr style="border-color: #333;">
            <p style="color: #b2b9c4;"><strong>إشعار قانوني:</strong></p>
            <ul style="color: #b2b9c4;">
                <li>كافة الحقوق محفوظة للمطور.</li>
                <li>يمنع منعاً باتاً نسخ، توزيع، أو تعديل الكود المصدري لهذا البرنامج دون الحصول على إذن خطي صريح.</li>
                <li>هذا النظام مخصص للاستخدام المهني في إدارة الحقول الذكية وفقاً للترخيص الممنوح.</li>
            </ul>
            <p style="color: #ffc107; font-weight: bold;">حقوق الملكية الفكرية محمية قانونياً © 2026</p>
        </div>
    """, unsafe_allow_html=True)
        
            