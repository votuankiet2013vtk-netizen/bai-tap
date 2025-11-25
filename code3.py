# app.py
import streamlit as st
from dataclasses import dataclass
from typing import List, Dict
from PIL import Image, ImageStat
import pandas as pd
import io
import time
import random
import json

# Optional imports for sensor reading (commented unless you install pyserial/paho-mqtt)
# import serial
# import paho.mqtt.client as mqtt

st.set_page_config(page_title="AI Khay Cơm - Demo", layout="wide")

# ---------------------------
# Helpers & Nutrition logic
# ---------------------------
@dataclass
class Person:
    age:int
    sex:str
    weight_kg:float
    height_cm:float
    activity:str  # sedentary/light/moderate/active

def calculate_bmr(person: Person) -> float:
    s = 5 if person.sex.lower() == 'male' else -161
    return 10 * person.weight_kg + 6.25 * person.height_cm - 5 * person.age + s

ACTIVITY_FACTORS = {
    'ít vận động': 1.2, 'vận động nhẹ': 1.375, 'vận động trung bình': 1.55, 'vận động nặng': 1.725
}
def calculate_tdee(person: Person) -> float:
    bmr = calculate_bmr(person)
    return bmr * ACTIVITY_FACTORS.get(person.activity, 1.2)

# Mock nutrient database (in real app replace with full DB)
FOOD_DB = {
    "cơm": {"kcal":200, "protein":4, "fat":1, "carbs":44},
    "gà chiên": {"kcal":260, "protein":18, "fat":18, "carbs":6},
    "rau xào": {"kcal":70, "protein":2, "fat":4, "carbs":8},
    "trái cây": {"kcal":60, "protein":0.5, "fat":0.2, "carbs":15},
    "canh": {"kcal":40, "protein":1.5, "fat":1.0, "carbs":4}
}

@dataclass
class FoodItem:
    name:str
    kcal:float
    protein:float
    fat:float
    carbs:float
    portion_label:str = ""

def lookup_food(name:str, portion_label="1 phần") -> FoodItem:
    key = name.lower()
    if key in FOOD_DB:
        d = FOOD_DB[key]
        return FoodItem(name=name, kcal=d["kcal"], protein=d["protein"], fat=d["fat"], carbs=d["carbs"], portion_label=portion_label)
    # fallback: unknown food
    return FoodItem(name=name, kcal=80, protein=2.0, fat=2.0, carbs=10.0, portion_label=portion_label)

def evaluate_meal_items(person: Person, items: List[FoodItem]) -> Dict:
    tdee = round(calculate_tdee(person),1)
    total_kcal = sum(i.kcal for i in items)
    total_protein = sum(i.protein for i in items)
    total_fat = sum(i.fat for i in items)
    total_carbs = sum(i.carbs for i in items)
    # simple targets
    protein_target = max(1.0 * person.weight_kg, 0.8*person.weight_kg)
    fat_target = 0.25 * tdee / 9  # grams? we use cal -> g: (0.25*tdee)/9 -> g
    carbs_target = (tdee - (protein_target*4 + 0.25*tdee)) / 4 if tdee>0 else 0
    report = {
        "tdee_kcal": tdee,
        "total_kcal": total_kcal,
        "total_protein_g": round(total_protein,1),
        "total_fat_g": round(total_fat,1),
        "total_carbs_g": round(total_carbs,1),
        "perc_kcal": round(100*total_kcal/tdee,1) if tdee>0 else 0,
        "protein_target_g": round(protein_target,1),
        "fat_target_g": round(fat_target,1),
        "carbs_target_g": round(carbs_target,1),
        "notes": [],
        "suggestions": []
    }
    # notes heuristics
    if report["perc_kcal"] < 25:
        report["notes"].append("Khẩu phần ít năng lượng — cân nhắc bữa phụ.")
        report["suggestions"].append("Thêm sữa hoặc chuối/ngũ cốc nhỏ.")
    if report["total_protein_g"] < 0.6 * protein_target:
        report["notes"].append("Protein chưa đủ.")
        report["suggestions"].append("Bổ sung trứng hoặc ức gà nhỏ.")
    if "rau" not in " ".join([i.name.lower() for i in items]):
        report["notes"].append("Ít rau/rau không có trên khay.")
        report["suggestions"].append("Thêm 1 phần rau luộc hoặc canh.")
    if report["total_fat_g"] > 1.2 * report["fat_target_g"]:
        report["notes"].append("Nhiều chất béo — giảm đồ chiên.")
    return report

# ---------------------------
# Mock image recognizer
# ---------------------------
def mock_recognize_food_from_image(img: Image.Image) -> List[FoodItem]:
    """
    Demo placeholder: try detect 'rice' by checking light pixels,
    'green' for vegetables, 'brown' for fried meat.
    Replace this with your ML model inference (YOLO/TFLite).
    """
    stat = ImageStat.Stat(img.convert("RGB"))
    r_mean, g_mean, b_mean = stat.mean
    results = []
    # heuristics
    if r_mean>100 and g_mean>100 and b_mean>100:
        # bright -> likely rice + fruit
        results.append(lookup_food("cơm"))
        results.append(lookup_food("trái cây"))
    else:
        if g_mean > r_mean and g_mean > b_mean:
            results.append(lookup_food("rau xào"))
            results.append(lookup_food("cơm"))
        else:
            # meat-ish
            results.append(lookup_food("gà chiên"))
            results.append(lookup_food("cơm"))
            results.append(lookup_food("rau xào"))
    # randomly vary portions to simulate different sizes
    for it in results:
        mult = random.choice([0.5, 1.0, 1.5])
        it.kcal *= mult
        it.protein *= mult
        it.fat *= mult
        it.carbs *= mult
        it.portion_label = f"{mult}x"
    return results

# ---------------------------
# UI: Sidebar (person info + mode)
# ---------------------------
st.sidebar.title("Thông tin học sinh & cài đặt")
mode = st.sidebar.radio("Chọn chế độ", ["Manual input (nhập tay)", "Camera + Sensor (ảnh & cảm biến)"])
st.sidebar.markdown("---")
with st.sidebar.form("person_form", clear_on_submit=False):
    age = st.number_input("Tuổi", value=12, min_value=3, max_value=18, step=1)
    sex = st.selectbox("Giới tính", ["Nam", "Nữ"])
    weight = st.number_input("Cân nặng (kg)", value=40.0, min_value=10.0, max_value=150.0, step=0.5)
    height = st.number_input("Chiều cao (cm)", value=140.0, min_value=80.0, max_value=220.0, step=0.5)
    activity = st.selectbox("Mức hoạt động", ["Ít vận động","Vận động nhẹ","Vận động trung bình","Vận động mạnh"])
    submitted = st.form_submit_button("Lưu thông tin")
person = Person(age=age, sex=sex, weight_kg=weight, height_cm=height, activity=activity)

# ---------------------------
# Main: Manual input mode
# ---------------------------
if mode == "Manual input (nhập tay)":
    st.title("Nhập tay - Ghi nhận khay cơm")
    # create 5 columns like ảnh
    col1, col2, col3, col4, col5 = st.columns(5)
    # list of sample choices
    sample_foods = ["Cơm", "Gà chiên", "Rau xào", "Trái cây", "Canh", "Cá kho", "Đậu hũ"]
    # in each column show buttons for quick add
    with col1:
        st.markdown("### Món 1")
        f1 = st.selectbox("Chọn món", sample_foods, key="m1")
        p1 = st.selectbox("Khẩu phần", ["0.5 phần", "1 phần", "1.5 phần"], key="p1")
    with col2:
        st.markdown("### Món 2")
        f2 = st.selectbox("Chọn món", sample_foods, key="m2")
        p2 = st.selectbox("Khẩu phần", ["0.5 phần", "1 phần", "1.5 phần"], key="p2")
    with col3:
        st.markdown("### Món 3")
        f3 = st.selectbox("Chọn món", sample_foods, key="m3")
        p3 = st.selectbox("Khẩu phần", ["0.5 phần", "1 phần", "1.5 phần"], key="p3")
    with col4:
        st.markdown("### Món 4")
        f4 = st.selectbox("Chọn món", sample_foods, key="m4")
        p4 = st.selectbox("Khẩu phần", ["0.5 phần", "1 phần", "1.5 phần"], key="p4")
    with col5:
        st.markdown("### Món 5")
        f5 = st.selectbox("Chọn món", sample_foods, key="m5")
        p5 = st.selectbox("Khẩu phần", ["0.5 phần", "1 phần", "1.5 phần"], key="p5")

    if st.button("Đánh giá khay cơm"):
        # build list of FoodItem
        selections = [(f1,p1),(f2,p2),(f3,p3),(f4,p4),(f5,p5)]
        items = []
        for name,portion in selections:
            item = lookup_food(name)
            # scale by portion
            mult = 1.0
            if "0.5" in portion: mult = 0.5
            if "1.5" in portion: mult = 1.5
            item.kcal *= mult
            item.protein *= mult
            item.fat *= mult
            item.carbs *= mult
            item.portion_label = portion
            items.append(item)
        report = evaluate_meal_items(person, items)
        st.subheader("Báo cáo nhanh")
        st.write(f"TDEE ước tính: {report['tdee_kcal']} kcal")
        st.metric("Tổng năng lượng khay", f"{report['total_kcal']} kcal", delta=f"{report['perc_kcal']}% của TDEE")
        df = pd.DataFrame([vars(i) for i in items])
        st.dataframe(df)
        st.session_state['before_items'] = items
        st.write("Ghi chú:")
        for n in report["notes"]:
            st.write("- " + n)
        st.write("Gợi ý:")
        for g in report["suggestions"]:
            st.write("- " + g)
        before_items = items  # lưu khẩu phần lúc trước ăn
    # ---------------------------
    # ĐÁNH GIÁ KHAY CƠM SAU ĂN
    # ---------------------------

    st.markdown("## 🍽 Đánh giá khay cơm sau ăn")

    # Lấy dữ liệu trước ăn từ session_state (nếu có)
    before_items = st.session_state.get('before_items', None)
    if before_items is None:
        st.warning("Chưa có dữ liệu khay trước ăn. Vui lòng bấm 'Đánh giá khay cơm' trước để lưu khẩu phần rồi mới dùng chức năng 'sau ăn'.")
    else:
        st.write("Nhập lượng thức ăn còn lại sau khi ăn:")

        left_cols = st.columns(5)
        portion_left_inputs = []

        with left_cols[0]:
            pl1 = st.selectbox("Còn lại món 1", ["0.0 phần", "0.25 phần", "0.5 phần", "1 phần"], key="pl1")
            portion_left_inputs.append(pl1)
        with left_cols[1]:
            pl2 = st.selectbox("Còn lại món 2", ["0.0 phần", "0.25 phần", "0.5 phần", "1 phần"], key="pl2")
            portion_left_inputs.append(pl2)
        with left_cols[2]:
            pl3 = st.selectbox("Còn lại món 3", ["0.0 phần", "0.25 phần", "0.5 phần", "1 phần"], key="pl3")
            portion_left_inputs.append(pl3)
        with left_cols[3]:
            pl4 = st.selectbox("Còn lại món 4", ["0.0 phần", "0.25 phần", "0.5 phần", "1 phần"], key="pl4")
            portion_left_inputs.append(pl4)
        with left_cols[4]:
            pl5 = st.selectbox("Còn lại món 5", ["0.0 phần", "0.25 phần", "0.5 phần", "1 phần"], key="pl5")
            portion_left_inputs.append(pl5)

        if st.button("📊 Tính đánh giá sau ăn"):

            def convert_portion(p):
                if "0.0" in p: return 0.0
                if "0.25" in p: return 0.25
                if "0.5" in p: return 0.5
                if "1" in p: return 1.0
                return 1.0

            eaten_items = []

            for idx, before in enumerate(before_items):
                # phần được chọn lúc trước ăn (chú ý portion_label có dạng "0.5 phần" hoặc "1.5x" tùy code của bạn)
                before_p = 1.0
                if "0.5" in str(before.portion_label): before_p = 0.5
                if "1.5" in str(before.portion_label): before_p = 1.5

                # phần còn lại do người dùng nhập
                left_p = convert_portion(portion_left_inputs[idx])

                # tỉ lệ đã ăn
                eaten_ratio = max(before_p - left_p, 0) / before_p if before_p > 0 else 0.0

                eaten_items.append(
                    FoodItem(
                        name=before.name,
                        kcal=before.kcal * eaten_ratio,
                        protein=before.protein * eaten_ratio,
                        fat=before.fat * eaten_ratio,
                        carbs=before.carbs * eaten_ratio,
                        portion_label=f"Ăn {round(eaten_ratio*100)}%"
                    )
                )

            after_report = evaluate_meal_items(person, eaten_items)

            st.subheader("📌 Kết quả sau ăn")
            st.metric("Năng lượng nạp thực tế", f"{after_report['total_kcal']} kcal")

            st.metric(
                "Tỉ lệ khẩu phần đã ăn",
                f"{round(sum([1 - convert_portion(x) for x in portion_left_inputs]) / 5 * 100, 1)}%"
            )

            st.write("### Chi tiết các món đã ăn")
            st.dataframe(pd.DataFrame([vars(x) for x in eaten_items]))

            st.write("### Nhận xét & Gợi ý sau ăn")
            for n in after_report["notes"]:
                st.write("✔ " + n)
            for g in after_report["suggestions"]:
                st.write("💡 " + g)



# ---------------------------
# Camera + Sensor mode
# ---------------------------
else:
    st.title("Camera + Sensor - Tự động (Demo)")
    st.markdown("Chụp ảnh khay cơm bằng camera hoặc upload ảnh. Bạn có thể mô phỏng dữ liệu cân (sensor) bằng slider hoặc kết nối thực tế qua serial/MQTT.")
    # left: camera, right: sensor
    c1, c2 = st.columns([2,1])
    with c1:
        st.markdown("#### Ảnh từ camera")
        img_file = st.camera_input("Chụp khay cơm", key="cam1")
        st.markdown("Hoặc upload ảnh:")
        uploaded = st.file_uploader("Upload ảnh khay", type=["png","jpg","jpeg"], key="up1")
        image_to_use = None
        if img_file is not None:
            image_to_use = Image.open(img_file)
        elif uploaded is not None:
            image_to_use = Image.open(uploaded)

        if image_to_use is not None:
            st.image(image_to_use, caption="Ảnh khay (demo nhận diện)", use_column_width=True)
            if st.button("Phân tích ảnh"):
                with st.spinner("Nhận diện... (placeholder demo)"):
                    time.sleep(1.0)
                    detected_items = mock_recognize_food_from_image(image_to_use)
                    report = evaluate_meal_items(person, detected_items)
                    st.success("Xong — kết quả tóm tắt:")
                    st.metric("Tổng kcal (ước tính)", f"{report['total_kcal']} kcal", delta=f"{report['perc_kcal']}% của TDEE")
                    st.write("Món được nhận diện (demo):")
                    df_detect = pd.DataFrame([vars(i) for i in detected_items])
                    st.dataframe(df_detect)
                    st.write("Ghi chú:")
                    for n in report["notes"]:
                        st.write("- " + n)
                    st.write("Gợi ý:")
                    for g in report["suggestions"]:
                        st.write("- " + g)
        else:
            st.info("Chưa có ảnh. Hãy chụp 1 tấm.")

    with c2:
        st.markdown("#### Dữ liệu cảm biến (demo)")
        st.markdown("Bạn có thể mô phỏng cảm biến cân hoặc kết nối thực tế.")
        sensor_mode = st.radio("Sensor mode", ["Simulate (slider)", "Serial (pyserial)", "MQTT (paho-mqtt)"])
        sensor_data = {}
        if sensor_mode == "Simulate (slider)":
            weight_sensor = st.slider("Cân (sensor) - trọng lượng phần ăn (gram)", 50, 1000, 250, step=10)
            temp_sensor = st.number_input("Nhiệt độ thực phẩm (°C)", value=40)
            sensor_data = {"sensor_weight_g": weight_sensor, "temp_c": temp_sensor}
            st.write(sensor_data)
        elif sensor_mode == "Serial (pyserial)":
            st.write("Kết nối Serial demo — đoạn code cần pyserial. (Không bật ở demo unless you install pyserial)")
            com_port = st.text_input("COM port (ví dụ: COM3 hoặc /dev/ttyUSB0)", value="/dev/ttyUSB0")
            baud = st.number_input("Baudrate", value=9600)
            if st.button("Đọc 1 lần từ Serial"):
                st.warning("Tính năng serial cần cài pyserial và chạy trên môi trường có cổng serial.")
                # Example (commented):
                # ser = serial.Serial(com_port, baud, timeout=2)
                # line = ser.readline().decode().strip()
                # st.write("Raw:", line)
                # try: sensor_data = json.loads(line)
                # except: sensor_data = {"raw": line}
        else:
            st.write("MQTT demo: đăng ký topic, cần paho-mqtt.")
            broker = st.text_input("Broker (host)", value="test.mosquitto.org")
            topic = st.text_input("Topic", value="demo/foodscale")
            if st.button("Kết nối MQTT (demo)"):
                st.warning("MQTT đọc cần paho-mqtt và broker; phần này là ví dụ.")
                # Example (not executed here)
                # def on_connect(client, userdata, flags, rc): ...
                # client = mqtt.Client(); client.connect(broker)
                # client.loop_start(); client.subscribe(topic)
                # implement callback to update sensor_data

        st.markdown("---")
        st.markdown("#### Kết quả phân tích cộng cảm biến")
        if sensor_data:
            st.write("Dữ liệu cảm biến (mô phỏng):", sensor_data)
            # If we have image + weight, adjust kcal estimate by portion
            if 'sensor_weight_g' in sensor_data and image_to_use is not None:
                # naive adjustment: scale detected kcal by ratio of measured weight (assume model used standard portion 250g)
                measured = sensor_data['sensor_weight_g']
                scale = measured / 250.0
                st.write(f"Điều chỉnh khẩu phần theo cân: nhân hệ số {scale:.2f}")
                # use previous detected_items if exist
                try:
                    detected_items
                except NameError:
                    detected_items = mock_recognize_food_from_image(image_to_use)
                for it in detected_items:
                    it.kcal *= scale
                    it.protein *= scale
                    it.fat *= scale
                    it.carbs *= scale
                report2 = evaluate_meal_items(person, detected_items)
                st.metric("Tổng kcal (cân điều chỉnh)", f"{report2['total_kcal']} kcal", delta=f"{report2['perc_kcal']}% của TDEE")
                st.dataframe(pd.DataFrame([vars(i) for i in detected_items]))
                st.write("Gợi ý:")
                for g in report2["suggestions"]:
                    st.write("- " + g)
        else:
            st.info("Chưa có dữ liệu cảm biến (hoặc bạn chưa simulate).")