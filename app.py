import os
import time
import random
import sqlite3
import pandas as pd
import requests
from datetime import datetime
import streamlit as st
import folium
from streamlit_folium import st_folium

# ================= 1. تهيئة الصفحة والثيم المظلم =================
st.set_page_config(
    page_title="منظومة MAS-GUARD ⚡ - الرادار التكتيكي",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #e6edf3; }
    
    /* صندوق أسود أنيق للعنوان الرئيسي */
    .title-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-right: 5px solid #58a6ff;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        display: inline-block;
        width: 100%;
    }
    .title-box h1 {
        color: #58a6ff !important;
        font-family: 'Courier New', Courier, monospace;
        margin: 0;
        font-size: 2rem;
    }

    /* صناديق أسود أنيقة للتبويبات (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #c9d1d9 !important;
        padding: 10px 20px !important;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    /* تأثير عند حوم الماوس فوق التبويب */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #21262d !important;
        border-color: #58a6ff !important;
        color: #58a6ff !important;
    }
    /* التبويب النشط/المحدد */
    .stTabs [aria-selected="true"] {
        background-color: #0d1117 !important;
        border: 2px solid #1f6feb !important;
        color: #58a6ff !important;
        box-shadow: 0 0 10px rgba(31, 111, 235, 0.4);
    }

    /* تنسيق كروت الإحصائيات والشريط العملياتي */
    [data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.8rem !important; font-weight: bold !important; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 0.9rem !important; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .log-box { background-color: #070a0e; border: 1px solid #21262d; border-radius: 8px; padding: 15px; height: 250px; overflow-y: auto; font-family: 'Courier New', Courier, monospace; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# ================= 2. نظام الحماية بكلمة مرور =================
def check_password():
    """عرض نموذج تسجيل دخول بسيط"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 MAS-GUARD ⚡ - دخول المصرح لهم")
        password = st.text_input("أدخل كلمة مرور القيادة:", type="password")
        if st.button("دخول"):
            if password == "MAS123456":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة!")
        return False
    return True

if not check_password():
    st.stop()

# ================= 3. إعدادات التليجرام والتنبيهات =================
TELEGRAM_BOT_TOKEN = "8665675697:AAHWbhL8RVVkqUJqBryUNZtcZhE9v6xjJJU" 
TELEGRAM_CHAT_ID = "1607965956"

def send_telegram_alert(message):
    """إرسال رسالة تنبيه فورية عبر بوت تليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"خطأ في إرسال تنبيه تليجرام: {e}")
        return False

# ================= 4. إدارة وقواعد البيانات (SQLite & Excel) =================
def init_db_from_excel():
    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soldiers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            rank TEXT NOT NULL,
            age INTEGER,
            service_location TEXT,
            blood_type TEXT,
            battalion TEXT,
            base_lat REAL,
            base_lon REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soldier_id INTEGER,
            timestamp TEXT,
            heart_rate INTEGER,
            spo2 INTEGER,
            temp REAL,
            status TEXT,
            lat REAL,
            lon REAL,
            battery INTEGER,
            signal_strength TEXT,
            FOREIGN KEY(soldier_id) REFERENCES soldiers(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action TEXT
        )
    ''')
    
    excel_file = "soldiers_list.xlsx"
    
    if not os.path.exists(excel_file):
        default_data = {
            'الرقم العسكري': [101, 102, 103, 104, 105],
            'الاسم': ["أحمد العتيبي", "خالد الشمري", "عمر القحطاني", "سلطان الدوسري", "فيصل المطيري"],
            'الرتبة': ["رقيب", "وكيل رقيب", "عريف", "جندي أول", "جندي"],
            'العمر': [29, 27, 25, 23, 22],
            'مكان الخدمة': ["الحد الجنوبي", "المنطقة الوسطى", "المنطقة الشرقية", "الحد الجنوبي", "المنطقة الشمالية"],
            'فصيلة الدم': ["O+", "A+", "B+", "AB+", "O-"],
            'الكتيبة': ["كتيبة المشاة الآلية 12", "كتيبة المدرعات 4", "كتيبة الإسناد القتالي", "كتيبة المشاة الآلية 12", "قوات المهام الخاصة"],
            'خط العرض': [24.7136, 24.7150, 24.7110, 24.7180, 24.7125],
            'خط الطول': [46.6753, 46.6780, 46.6720, 46.6710, 46.6795]
        }
        

def log_action(action):
    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    conn.execute("INSERT INTO audit_log (timestamp, action) VALUES (?, ?)", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action))
    conn.commit()
    conn.close()

def insert_log(soldier_id, heart_rate, spo2, temp, status, lat, lon, battery, signal_strength):
    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO health_logs (soldier_id, timestamp, heart_rate, spo2, temp, status, lat, lon, battery, signal_strength)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (soldier_id, timestamp, heart_rate, spo2, temp, status, lat, lon, battery, signal_strength))
    conn.commit()
    conn.close()

def get_latest_status():
    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    df = pd.read_sql_query('''
        SELECT 
            s.id AS id, s.name AS name, s.rank AS rank, s.age AS age, 
            s.service_location AS service_location, s.blood_type AS blood_type, 
            s.battalion AS battalion, s.base_lat AS base_lat, s.base_lon AS base_lon,
            hl.timestamp, hl.heart_rate, hl.spo2, hl.temp, hl.status, hl.lat, hl.lon, hl.battery, hl.signal_strength
        FROM soldiers s
        LEFT JOIN health_logs hl ON s.id = hl.soldier_id
        WHERE hl.id = (SELECT MAX(id) FROM health_logs WHERE soldier_id = s.id)
        OR hl.id IS NULL
    ''', conn)
    conn.close()
    return df

def get_soldier_history(soldier_id):
    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    df = pd.read_sql_query('''
        SELECT timestamp, heart_rate, spo2 FROM health_logs 
        WHERE soldier_id = ? ORDER BY id DESC LIMIT 10
    ''', conn, params=(soldier_id,))
    conn.close()
    if not df.empty:
        return df.iloc[::-1]
    return df

def auto_generate_data():
    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    df_soldiers = pd.read_sql_query("SELECT * FROM soldiers", conn)
    conn.close()
    
    if df_soldiers.empty: return

    target = df_soldiers.sample().iloc[0]
    lat_offset = random.uniform(-0.003, 0.003)
    lon_offset = random.uniform(-0.003, 0.003)
    
    dice = random.random()
    if dice > 0.88: 
        heart_rate = random.randint(35, 48)
        spo2 = random.randint(82, 87)
        temp = round(random.uniform(34.8, 35.5), 1)
        status = "إصابة / سقوط"
        battery = random.randint(15, 40)
    elif dice < 0.12: 
        heart_rate = random.randint(70, 85)
        spo2 = random.randint(97, 100)
        temp = round(random.uniform(36.6, 37.1), 1)
        status = "مستقر"
        battery = random.randint(5, 12)
    else: 
        heart_rate = random.randint(65, 95)
        spo2 = random.randint(96, 100)
        temp = round(random.uniform(36.5, 37.4), 1)
        status = "مستقر"
        battery = random.randint(50, 99)
        
    signal = random.choice(["ممتاز 🟢", "متوسط 🟡", "ضعيف 🔴"])
    insert_log(int(target['id']), heart_rate, spo2, temp, status, target['base_lat']+lat_offset, target['base_lon']+lon_offset, battery, signal)
    
    if status == "إصابة / سقوط":
        send_telegram_alert(f"🚨 *بلاغ تكتيكي عاجل*\n\n👤 *الجندي:* {target['rank']} / {target['name']}\n🏢 *الموقع:* {target['service_location']} - {target['battalion']}\n⚠️ *الحالة:* سقوط أو إصابة ميدانية حادة!\n💓 *النبض:* {heart_rate} BPM")
    elif battery < 15:
        send_telegram_alert(f"🪫 *تنبيه صيانة السترة*\n\n👤 *الجندي:* {target['rank']} / {target['name']}\n⚠️ *البطارية:* {battery}% منخفضة جداً.")

# تهيئة قاعدة البيانات والملفات
init_db_from_excel()

# ================= 5. القائمة الجانبية وزر الاستغاثة =================
st.sidebar.title("🛡️ MAS-GUARD ⚡")

# زر الاستغاثة العاجلة
if st.sidebar.button("🚨 زر الاستغاثة الصامت (Panic Button)", use_container_width=True):
    st.error("⚠️ حالة طوارئ مشددة! جميع القوات في حالة تأهب...")
    log_action("🚨 تفعيل حالة الطوارئ القصوى (Panic Button)")
    send_telegram_alert("🚨 *حالة طوارئ قصوى!* تم ضغط زر الاستغاثة من مركز القيادة.")

st.sidebar.write("---")
st.sidebar.header("📡 وضع الرادار والمحاكاة")
radar_active = st.sidebar.toggle("🟢 تفعيل الرادار الحي (Auto-Refresh)", value=False)
refresh_interval = st.sidebar.slider("⏱️ سرعة التحديث (بالثواني):", 2, 10, 4)

st.sidebar.write("---")
st.sidebar.header("🕹️ البث اليدوي التكتيكي")

conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
soldiers_df = pd.read_sql_query("SELECT * FROM soldiers", conn)
conn.close()

selected_soldier_name = st.sidebar.selectbox(
    "اختر جندي للبث اليدوي:", 
    soldiers_df['name'].tolist() if not soldiers_df.empty else ["لا يوجد جنود"]
)

selected_status_ui = st.sidebar.selectbox(
    "حدد الحالة الصحية للجندي:",
    ["🟢 طبيعي (مستقر)", "🟡 إصابة خفيفة", "🚨 إصابة حرجة / سقوط", "⚫ متوفي"]
)

if not soldiers_df.empty and selected_soldier_name != "لا يوجد جنود":
    selected_soldier_id = int(soldiers_df[soldiers_df['name'] == selected_soldier_name]['id'].values[0])
    selected_soldier_row = soldiers_df[soldiers_df['name'] == selected_soldier_name].iloc[0]
    
    if selected_status_ui == "🟢 طبيعي (مستقر)":
        h_rate, s_o2, t_val, db_status, bat, sig = random.randint(72, 88), random.randint(97, 100), round(random.uniform(36.5, 37.2), 1), "مستقر", random.randint(75, 98), "ممتاز 🟢"
    elif selected_status_ui == "🟡 إصابة خفيفة":
        h_rate, s_o2, t_val, db_status, bat, sig = random.randint(105, 120), random.randint(92, 95), round(random.uniform(37.5, 38.2), 1), "إصابة خفيفة", random.randint(45, 70), "متوسط 🟡"
    elif selected_status_ui == "🚨 إصابة حرجة / سقوط":
        h_rate, s_o2, t_val, db_status, bat, sig = random.randint(35, 48), random.randint(80, 86), round(random.uniform(34.5, 35.4), 1), "إصابة / سقوط", random.randint(10, 35), "ضعيف 🔴"
    elif selected_status_ui == "⚫ متوفي":
        h_rate, s_o2, t_val, db_status, bat, sig = 0, 0, round(random.uniform(28.0, 32.0), 1), "متوفي", random.randint(10, 90), "انقطاع الخدمة 🔴"

    if st.sidebar.button("إرسال النبضة المحددة 📡", use_container_width=True):
        insert_log(selected_soldier_id, h_rate, s_o2, t_val, db_status, selected_soldier_row['base_lat'], selected_soldier_row['base_lon'], bat, sig)
        log_action(f"بث يدوي للجندي {selected_soldier_name}: {selected_status_ui}")
        
        if db_status == "إصابة / سقوط":
            send_telegram_alert(f"🚨 *بلاغ تكتيكي عاجل (بث يدوي)*\n\n👤 *الجندي:* {selected_soldier_row['rank']} / {selected_soldier_row['name']}\n⚠️ *الحالة:* إصابة ميدانية حرجة أو سقوط مفاجئ!\n💓 *النبض:* {h_rate} BPM")
        elif db_status == "متوفي":
            send_telegram_alert(f"🚨💥 *إنذار شهيد حرج للغاية*\n\n👤 *الشهيد:* {selected_soldier_row['rank']} / {selected_soldier_row['name']}\n💔 *النبض:* 0 BPM (انقطاع المؤشرات الحيوية بالكامل)")
        elif db_status == "إصابة خفيفة":
            send_telegram_alert(f"🟡 *تنبيه طبي متوسط*\n\n👤 *الجندي:* {selected_soldier_row['rank']} / {selected_soldier_row['name']}\n⚠️ *الحالة:* إصابة خفيفة ومستقرة.")
            
        st.sidebar.success(f"تم بث الحالة: {selected_status_ui}")

if radar_active:
    auto_generate_data()

latest_data = get_latest_status()

# ================= 6. الهيكل الرئيسي للمنظومة والتبويبات =================
st.markdown("""
    <div class="title-box">
        <h1>🛡️ منظومة MAS-GUARD ⚡ - مركز القيادة </h1>
    </div>
""", unsafe_allow_html=True)

# لوحة المقاييس الرئيسية أعلى الصفحة
col_total, col_stable, col_danger, col_low_bat = st.columns(4)
low_battery_count = len(latest_data[latest_data['battery'].apply(lambda x: x < 15 if pd.notna(x) else False)]) if not latest_data.empty else 0

with col_total: st.metric("👥 إجمالي القوة", f"{len(latest_data)} جنود")
with col_stable: st.metric("🟢 الجاهزية القتالية", f"{len(latest_data[~latest_data['status'].isin(['إصابة / سقوط', 'متوفي'])])} جنود" if not latest_data.empty else "0 جنود")
with col_danger: st.metric("🚨 الطوارئ النشطة", f"{len(latest_data[latest_data['status'].isin(['إصابة / سقوط', 'متوفي'])])} حالات" if not latest_data.empty else "0 حالات")
with col_low_bat: st.metric("🪫 أجهزة حرجة الطاقة", f"{low_battery_count} أجهزة")

st.write("---")

# إنشاء التبويبات الرئيسية
tab_dashboard, tab_map, tab_vitals, tab_analytics, tab_logs, tab_excel = st.tabs([
    "عرفة العمليات", 
    "التموضع والتتبع", 
    "المؤشرات الحيوية", 
    "التحليل والأداء", 
    "التقارير والأحداث", 
    "إدارة وتعديل البيانات"
])

# ----------------- التبويب 1: غرفة العمليات والإنذارات -----------------
with tab_dashboard:
    col_audio, col_events = st.columns([1, 2])

    with col_audio:
        st.markdown("### 🔊 البث الصوتي والتنبيه المباشر")
        if not latest_data.empty:
            dangerous_cases = latest_data[latest_data['status'] == "إصابة / سقوط"]
            death_cases = latest_data[latest_data['status'] == "متوفي"]
            
            if not death_cases.empty:
                for idx, row in death_cases.iterrows():
                    st.error(f"⚫ **انقطاع مؤشرات الجندي:** {row['name']}")
                    announcement_text = f"تحذير! انقطاع مؤشرات الجندي {row['name']} بالكامل"
                    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ar&client=tw-ob&q={announcement_text.replace(' ', '%20')}"
                    st.audio(tts_url, format="audio/mp3", autoplay=True)
            elif not dangerous_cases.empty:
                for idx, row in dangerous_cases.iterrows():
                    st.warning(f"🚨 **سقوط ميداني:** {row['name']}")
                    announcement_text = f"تحذير! سقوط الجندي {row['name']}"
                    tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=ar&client=tw-ob&q={announcement_text.replace(' ', '%20')}"
                    st.audio(tts_url, format="audio/mp3", autoplay=True)
            else:
                st.success("🟢 جميع أفراد الفصيل في وضع استقرار عملياتي.")

    with col_events:
        st.markdown("### 📜 شريط الأحداث الميداني (Live Log)")
        log_html = "<div class='log-box'>"
        conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
        logs_df = pd.read_sql_query('''
            SELECT hl.timestamp, s.name, s.rank, hl.status, hl.battery FROM health_logs hl 
            JOIN soldiers s ON s.id = hl.soldier_id ORDER BY hl.id DESC LIMIT 15
        ''', conn)
        conn.close()
        
        if not logs_df.empty:
            for _, log_row in logs_df.iterrows():
                time_str = log_row['timestamp'].split(" ")[1] if " " in log_row['timestamp'] else log_row['timestamp']
                if log_row['status'] == "إصابة / سقوط":
                    log_html += f"<p style='color:#ff7b72;'>[{time_str}] 🚨 إنذار سقوط حرج للجندي {log_row['rank']}/ {log_row['name']}!</p>"
                elif log_row['status'] == "متوفي":
                    log_html += f"<p style='color:#ffffff; background-color:#330000; padding:2px;'>[{time_str}] ⚫ انقطاع تام لنبض الجندي {log_row['name']}!</p>"
                elif log_row['status'] == "إصابة خفيفة":
                    log_html += f"<p style='color:#ffa500;'>[{time_str}] 🟡 رصد إصابة خفيفة للجندي {log_row['name']}.</p>"
                elif log_row['battery'] < 15:
                    log_html += f"<p style='color:#f2cc60;'>[{time_str}] 🪫 تنبيه: بطارية سترة الجندي {log_row['name']} منخفضة ({log_row['battery']}%).</p>"
                else:
                    log_html += f"<p style='color:#7ee787;'>[{time_str}] 🟢 نبضة لاسلكية مستقرة للجندي {log_row['name']}.</p>"
        else:
            log_html += "<p style='color:#8b949e;'>[--:--:--] في انتظار استقبال الإشارات اللاسلكية...</p>"
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)

# ----------------- التبويب 2: التموضع والتتبع الميداني -----------------
with tab_map:
    st.markdown("### 📍 الخريطة التكتيكية ونظام Geofencing")
    if not latest_data.empty:
        map_data = latest_data.dropna(subset=['lat', 'lon']).copy()
        if not map_data.empty:
            # تحويل الإحداثيات آمنة إلى float لمنع خطأ TypeError
            map_data['lat'] = pd.to_numeric(map_data['lat'], errors='coerce')
            map_data['lon'] = pd.to_numeric(map_data['lon'], errors='coerce')
            map_data['base_lat'] = pd.to_numeric(map_data['base_lat'], errors='coerce')
            map_data['base_lon'] = pd.to_numeric(map_data['base_lon'], errors='coerce')
            
            # حذف أي صفوف تحتوي على إحداثيات غير صالحة بعد التحويل
            map_data = map_data.dropna(subset=['lat', 'lon', 'base_lat', 'base_lon'])

            center_lat = map_data['lat'].mean()
            center_lon = map_data['lon'].mean()
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="OpenStreetMap")
            
            for _, row in map_data.iterrows():
                # تحويل القيم إلى float بضمان تام قبل العمليات الحسابية
                curr_lat = float(row['lat'])
                curr_lon = float(row['lon'])
                b_lat = float(row['base_lat'])
                b_lon = float(row['base_lon'])

                # تحديد اللون بناءً على الحالة والحدود الميدانية
                if row['status'] == "متوفي":
                    marker_color = "black"
                elif row['status'] == "إصابة / سقوط":
                    marker_color = "red"
                elif abs(curr_lat - b_lat) > 0.005 or abs(curr_lon - b_lon) > 0.005:
                    marker_color = "purple" # خارج النطاق التكتيكي
                elif row['status'] == "إصابة خفيفة" or (pd.notna(row['battery']) and row['battery'] < 15):
                    marker_color = "orange"
                else:
                    marker_color = "green"
                
                popup_text = f"""
                <div style="direction: rtl; text-align: right; font-family: Arial; font-size: 13px; width: 180px;">
                    <b>👤 الجندي:</b> {row['rank']} / {row['name']}<br>
                    <b>🏢 الكتيبة:</b> {row['battalion']}<br>
                    <b>🩺 الحالة:</b> {row['status']}<br>
                    <b>💓 النبض:</b> {int(row['heart_rate'] if pd.notna(row['heart_rate']) else 0)} BPM<br>
                    <b>🪫 البطارية:</b> {int(row['battery'] if pd.notna(row['battery']) else 0)}%
                </div>
                """
                
                folium.CircleMarker(
                    location=[curr_lat, curr_lon],
                    radius=10,
                    popup=folium.Popup(popup_text, max_width=250),
                    color=marker_color,
                    fill=True,
                    fill_color=marker_color,
                    fill_opacity=0.8
                ).add_to(m)
            
            st_folium(m, use_container_width=True, height=520, returned_objects=[])

# ----------------- التبويب 3: المؤشرات الحيوية للسترة -----------------
with tab_vitals:
    st.markdown("### 🎛️ حالة السترات والمؤشرات الحيوية الفردية")
    if not latest_data.empty:
        for index, row in latest_data.iterrows():
            bat_val = row['battery'] if pd.notna(row['battery']) else 100
            
            if row['status'] == "متوفي":
                status_lbl = "⚫ انقطاع النبض (تنبيه حرج)"
            elif row['status'] == "إصابة / سقوط":
                status_lbl = "🚨 حالة حرجة / سقوط"
            elif row['status'] == "إصابة خفيفة":
                status_lbl = "🟡 إصابة خفيفة"
            else:
                status_lbl = "🟢 مستقر وعامل"
            
            with st.expander(f"👤 {row['rank']} / {row['name']} ({row['battalion']}) - 【 {status_lbl} 】", expanded=False):
                col_info, col_vitals, col_chart = st.columns([1, 1, 1.5])
                
                with col_info:
                    st.markdown("**🪪 الملف العسكري:**")
                    st.write(f"• **الرقم العسكري:** {row['id']}")
                    st.write(f"• **العمر:** {row['age']} عاماً")
                    st.write(f"• **الموقع:** {row['service_location']}")
                    st.write(f"• **فصيلة الدم:** {row['blood_type']}")
                    
                with col_vitals:
                    st.markdown("**🩺 العلامات الحيوية الآن:**")
                    st.write(f"• **النبض:** {int(row['heart_rate']) if pd.notna(row['heart_rate']) else '--'} BPM")
                    st.write(f"• **الأكسجين:** {int(row['spo2']) if pd.notna(row['spo2']) else '--'}%")
                    st.write(f"• **الحرارة:** {row['temp'] if pd.notna(row['temp']) else '--'} °C")
                    st.write(f"• **طاقة السترة:** {int(bat_val)}% | **الإشارة:** {row['signal_strength'] if row['signal_strength'] else 'ممتاز 🟢'}")
                    
                with col_chart:
                    st.markdown("**📈 السجل البياني للنبض (آخر 10 قراءات):**")
                    history_df = get_soldier_history(int(row['id']))
                    if not history_df.empty and 'heart_rate' in history_df.columns:
                        st.line_chart(history_df.set_index('timestamp')['heart_rate'], height=130, use_container_width=True)
                    else:
                        st.caption("في انتظار وصول البيانات...")
    else:
        st.info("لا توجد بيانات جنود مسجلة.")

# ----------------- التبويب 4: تحليل مقارنة أداء الفصيل -----------------
with tab_analytics:
    st.markdown("### 📊 مقارنة أداء وطاقة الفصيل (Squad Comparison)")
    if not latest_data.empty:
        chart_df = latest_data.set_index('name')[['battery', 'heart_rate', 'spo2']].dropna()
        chart_df.columns = ['البطارية (%)', 'نبض القلب (BPM)', 'مستوى الأكسجين (%)']
        st.bar_chart(chart_df, height=400)
    else:
        st.info("لا توجد بيانات للمقارنة.")

# ----------------- التبويب 5: التقارير وسجل العمليات -----------------
with tab_logs:
    st.markdown("### 📜 السجل التاريخي وتصدير التقارير العملياتية")
    col_rep1, col_rep2 = st.columns(2)
    
    with col_rep1:
        st.markdown("#### 📥 تصدير تقرير الحالة الفورية")
        if not latest_data.empty:
            csv_data = latest_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="تحميل التقرير الشامل (CSV)",
                data=csv_data,
                file_name=f"MAS_Sentinel_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col_rep2:
        st.markdown("#### 📋 جدول البيانات الفوري")
        if not latest_data.empty:
            st.dataframe(latest_data[['id', 'name', 'rank', 'status', 'heart_rate', 'spo2', 'battery']], use_container_width=True)

    st.write("---")
    st.markdown("#### 🔐 سجل إجراءات النظام (Audit Log)")
    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    audit_df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY id DESC LIMIT 10", conn)
    conn.close()
    st.table(audit_df)
    # ----------------- التبويب 6: إدارة وتعديل البيانات -----------------
with tab_excel:
    st.subheader("لوحة إدخال وتعديل بيانات الجنود (شبيه الإكسل)")
    st.markdown("يمكنك إضافة، تعديل، أو حذف بيانات الجنود مباشرة في الجدول أدناه، ثم الضغط على زر الحفظ:")

    import pandas as pd
    import sqlite3

    conn = sqlite3.connect("sanad_system.db", check_same_thread=False)
    
    try:
        current_df = pd.read_sql_query("SELECT * FROM soldiers", conn)
    except Exception:
        current_df = pd.DataFrame(columns=['id', 'name', 'rank', 'age', 'service_location', 'blood_type', 'battalion', 'lat', 'lon'])

    edited_df = st.data_editor(
        current_df,
        num_rows="dynamic",
        use_container_width=True,
        key="soldiers_excel_editor"
    )

    if st.button("حفظ التعديلات وتحديث قاعدة البيانات"):
        try:
            edited_df.to_sql("soldiers", conn, if_exists="replace", index=False)
            st.success("تم حفظ وتحديث بيانات الجنود بنجاح تام! قم بتحديث الصفحة (F5) لرؤية التغييرات.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء الحفظ: {e}")
            
    conn.close()

# ================= 7. إعادة التحديث الآلي للرادار =================
if radar_active:
    time.sleep(refresh_interval)
    st.rerun()