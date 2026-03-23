import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Electricity Anomaly Detection", layout="wide")

st.title("⚡ Smart Grid Anomaly Detection System")
st.markdown("Prototype สำหรับตรวจจับการใช้ไฟฟ้าผิดปกติ (Crypto Mining)")

# -----------------------------
# 📊 Generate Data
# -----------------------------
def generate_data(mode):
    hours = np.arange(24)
    if mode == "🏠 บ้านปกติ":
        data = 2 + np.sin(hours/24 * 2*np.pi) * 2 + np.random.normal(0, 0.3, 24)
    elif mode == "🏢 ธุรกิจ":
        data = 7 + np.sin((hours-6)/24 * 2*np.pi) * 3 + np.random.normal(0, 0.5, 24)
    elif mode == "⚠️ ขุดคริปโต":
        data = np.ones(24) * 8 + np.random.normal(0, 0.1, 24)
    return np.clip(data, 0, None)

# -----------------------------
# 🤖 Feature Extraction
# -----------------------------
def extract_features(data):
    mean = np.mean(data)
    std = np.std(data)
    peak = np.max(data) - np.min(data)
    night = np.mean(data[0:6])
    day = np.mean(data[12:18])
    ratio = night / (day + 1e-5)
    return mean, std, peak, ratio

# -----------------------------
# 🧠 Detection Logic
# -----------------------------
def detect(mean, std, peak, ratio):
    if std < 0.5 and peak < 1.5 and ratio > 0.9:
        return "⚠️ Suspected Crypto Mining", 0.9
    elif std < 1.2:
        return "🤔 Slightly Abnormal", 0.6
    else:
        return "✅ Normal", 0.95

# -----------------------------
# 🎛️ Sidebar Control
# -----------------------------
st.sidebar.header("⚙️ Control Panel")
mode = st.sidebar.selectbox(
    "เลือกประเภทข้อมูล",
    ["🏠 บ้านปกติ", "🏢 ธุรกิจ", "⚠️ ขุดคริปโต"]
)
miners = st.sidebar.slider("จำนวนเครื่องขุด (Simulation)", 0, 10, 0)
uploaded_file = st.sidebar.file_uploader("📂 Upload CSV", type=["csv"])

# -----------------------------
# 📊 Data Source
# -----------------------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    data = df.iloc[:, 0].values[:24]
    source = "📂 Uploaded Data"
else:
    base = generate_data(mode)
    data = base + (miners * 1.0) 
    source = "🧪 Simulated Data"

# -----------------------------
# 📈 Plot Load Profile
# -----------------------------
st.subheader(f"📊 Load Profile ({source})")
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(data, marker='o', color='#1f77b4', label='Actual Usage')
ax.set_xlabel("Hour")
ax.set_ylabel("Load (kW)")
ax.set_ylim(0, max(data)+5)
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# -----------------------------
# 🔍 Analysis Result
# -----------------------------
mean_val, std_val, peak_val, ratio_val = extract_features(data)
label, confidence = detect(mean_val, std_val, peak_val, ratio_val)

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔍 Detection Result")
    st.write(f"**Result:** {label}")
    st.write(f"**Confidence:** {confidence*100:.1f}%")
with col2:
    st.subheader("📊 Key Features")
    st.write(f"Mean Load: {mean_val:.2f} kW")
    st.write(f"Std Dev: {std_val:.2f}")

# -----------------------------
# 💡 Explanation & 🚨 Alert System
# -----------------------------
st.subheader("💡 Explanation")

if "Crypto" in label:
    # แสดงกล่องสีแดงสำหรับเคสที่สงสัยว่าขุดคริปโต
    st.error(f"""
    **⚠️ พฤติกรรมเข้าข่ายการขุดคริปโต:**
    * **ใช้ไฟคงที่ตลอด 24 ชม.** (Std Dev: {std_val:.2f})
    * **ความแปรปรวนต่ำ** ไม่มีจังหวะลดโหลดไฟฟ้า
    * **ไม่มีช่วง peak usage** รูปแบบกราฟเป็นเส้นตรง (Flat Load)
    """)
    
    # เพิ่มส่วน Alert System ด้านล่าง
    st.subheader("🚨 Alert System")
    st.error("⚠️ High Risk: ตรวจพบความเสี่ยงสูงในการลักลอบขุดคริปโต")

elif "Abnormal" in label:
    # แสดงกล่องสีเหลืองสำหรับเคสที่เริ่มผิดปกติ
    st.warning(f"""
    **🤔 พบความผิดปกติบางส่วน:**
    * **รูปแบบการใช้ไฟเริ่มนิ่งเกินไป** สวนทางกับพฤติกรรมบ้านพักอาศัย
    * **ควรตรวจสอบเพิ่มเติม** ว่ามีการใช้เครื่องจักรหรืออุปกรณ์ไฟฟ้ากำลังสูงต่อเนื่องหรือไม่
    """)

else:
    # แสดงกล่องสีเขียวสำหรับเคสปกติ
    st.success(f"""
    **✅ การใช้ไฟปกติ:**
    * **มี pattern กลางวัน/กลางคืน** ที่ชัดเจน
    * **มี peak usage ชัดเจน** ตามช่วงเวลาการใช้ชีวิตปกติ
    """)

# -----------------------------
# 🔌 Transformer Monitoring (Power Theft Detection)
# -----------------------------
st.markdown("---")
st.subheader("🔌 Transformer Monitoring (Power Theft Detection)")
st.sidebar.header("⚡ Transformer Settings")
transformer_input = st.sidebar.slider("โหลดรวมจากหม้อแปลง (kW)", 0, 500, 150)
loss_threshold = st.sidebar.slider("Loss Threshold (%)", 0, 50, 15)
house_count = st.sidebar.slider("จำนวนบ้านในระบบ (House Count)", 1, 50, 10)

measured_mode = st.sidebar.radio(
    "Measured Load Source",
    ["ใช้ค่าจากระบบ (Auto)", "กำหนดเอง (Manual)"]
)

# 📊 คำนวณ Measured Load สวนทางกับจำนวนเครื่องขุด
bypass_per_miner = 1.5 
if measured_mode == "ใช้ค่าจากระบบ (Auto)":
    base_mean = np.mean(base) 
    total_normal_load = base_mean * house_count
    theft_loss = miners * bypass_per_miner
    measured_load = total_normal_load - theft_loss
    measured_load = max(0, measured_load) 
    st.session_state.manual_load = int(measured_load)
else:
    if 'manual_load' not in st.session_state:
        st.session_state.manual_load = 100
    measured_load = st.sidebar.slider("Measured Load (kW)", 0, 500, key="manual_slider_input", value=st.session_state.manual_load)
    st.session_state.manual_load = measured_load
    theft_loss = 0 # ในโหมด Manual เราจะไม่คำนวณ theft_loss จาก miner อัตโนมัติ

# 📋 คำนวณ Loss และแสดงผล
loss = transformer_input - measured_load
loss_percent = (loss / transformer_input) * 100 if transformer_input > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Transformer Input", f"{transformer_input:.2f} kW")
c2.metric("Total Measured Load", f"{measured_load:.2f} kW", delta=f"{-theft_loss if miners > 0 else 0:.2f} kW Bypass", delta_color="inverse")
c3.metric("System Loss (%)", f"{loss_percent:.2f}%", delta=f"{loss_percent - loss_threshold:.1f}% vs Threshold", delta_color="inverse")

if loss_percent > loss_threshold:
    st.error(f"🚨 High Risk: ตรวจพบการลักลอบใช้ไฟ (Bypass) สัญญาณสูญหายผิดปกติ {loss_percent:.2f}%")
elif loss_percent < 0:
    st.info("ℹ️ Note: Measured Load สูงกว่า Input (อาจมีการป้อนไฟกลับเข้าเข้าระบบ)")
else:
    st.success("✅ สถานะปกติ: พลังงานในระบบสมดุล")

fig2, ax2 = plt.subplots(figsize=(6, 3))
ax2.bar(["Transformer Input", "Total Measured"], [transformer_input, measured_load], color=['#ff4b4b', '#00cc96'])
ax2.set_ylabel("kW")
st.pyplot(fig2)

st.markdown("---")
st.caption("Prototype by Smart Grid Detection System - 2026 Edition")