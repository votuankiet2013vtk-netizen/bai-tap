# =========================
# code8.py (phiên bản tích hợp: Manual + 5 ngày + Face ID)
# Yêu cầu: streamlit, pandas, numpy, pillow, face_recognition
# Chạy: python -m streamlit run code8.py
# =========================

import os
import csv
import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

import face_recognition

st.set_page_config(page_title="AI Khay Cơm (5 ngày + Face ID)", layout="wide")

# =========================
# 1) DỮ LIỆU & TÍNH NĂNG DINH DƯỠNG
# =========================

@dataclass
class Person:
    age: int
    sex: str
    weight_kg: float
    height_cm: float
    activity: str  # sedentary/light/moderate/active

@dataclass
class FoodItem:
    name: str
    kcal: float
    protein: float
    fat: float
    carbs: float
    portion_label: str = ""  # ví dụ: "1 phần", "0.5 phần", "1.5 phần"

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
}

FOOD_DB: Dict[str, Dict[str, float]] = {
    "Cơm": {"kcal": 200, "protein": 4, "fat": 1, "carbs": 44},
    "Gà chiên": {"kcal": 260, "protein": 18, "fat": 18, "carbs": 6},
    "Rau xào": {"kcal": 70, "protein": 2, "fat": 4, "carbs": 8},
    "Trái cây": {"kcal": 60, "protein": 0.5, "fat": 0.2, "carbs": 15},
    "Canh": {"kcal": 40, "protein": 1.5, "fat": 1.0, "carbs": 4},
}

def calculate_bmr(p: Person) -> float:
    s = 5 if p.sex.lower() == "male" else -161
    return 10 * p.weight_kg + 6.25 * p.height_cm - 5 * p.age + s

def calculate_tdee(p: Person) -> float:
    return calculate_bmr(p) * ACTIVITY_FACTORS.get(p.activity, 1.2)

def lookup_food(name: str, portion_label: str = "1 phần") -> FoodItem:
    base = FOOD_DB.get(name, FOOD_DB["Cơm"])
    return FoodItem(
        name=name,
        kcal=base["kcal"],
        protein=base["protein"],
        fat=base["fat"],
        carbs=base["carbs"],
        portion_label=portion_label,
    )

def portion_multiplier(label: str) -> float:
    if "0.5" in label:
        return 0.5
    if "1.5" in label:
        return 1.5
    return 1.0

def left_to_float(label: str) -> float:
    if "0.0" in label:
        return 0.0
    if "0.25" in label:
        return 0.25
    if "0.5" in label:
        return 0.5
    return 1.0

def evaluate_meal(person: Person, items: List[FoodItem]) -> Dict:
    tdee = calculate_tdee(person)
    total_kcal = sum(i.kcal for i in items)
    ratio_pct = (total_kcal / tdee) * 100 if tdee > 0 else 0.0

    notes = []
    suggestions = []

    if ratio_pct < 50:
        notes.append("Bé ăn quá ít so với nhu cầu năng lượng.")
        suggestions.append("Bổ sung sữa/chuối hoặc món giàu năng lượng cho bữa phụ.")
    elif ratio_pct < 80:
        notes.append("Bữa ăn chưa đủ năng lượng cho nhu cầu trong ngày.")
        suggestions.append("Tăng protein (trứng, gà/đậu) và bổ sung rau + trái cây.")
    else:
        notes.append("Mức ăn tương đối đạt yêu cầu năng lượng.")
        suggestions.append("Tiếp tục giữ thói quen, ưu tiên món ít chiên xào.")

    return {
        "tdee_kcal": round(tdee, 1),
        "total_kcal": round(total_kcal, 1),
        "ratio_pct": round(ratio_pct, 1),
        "notes": notes,
        "suggestions": suggestions,
    }

# =========================
# 2) FACE ID (face_recognition) – tải ảnh trong thư mục faces/
# =========================

FACES_DIR = "faces"  # đặt cùng thư mục app.py

def load_known_faces() -> tuple[list, list]:
    names: list[str] = []
    encs: list[np.ndarray] = []
    if not os.path.isdir(FACES_DIR):
        return names, encs

    for fn in os.listdir(FACES_DIR):
        if not fn.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        path = os.path.join(FACES_DIR, fn)
        try:
            img = face_recognition.load_image_file(path)
            face_encs = face_recognition.face_encodings(img)
            if face_encs:
                names.append(os.path.splitext(fn)[0])
                encs.append(face_encs[0])
        except Exception:
            continue
    return names, encs

KNOWN_FACE_NAMES, KNOWN_FACE_ENCODINGS = load_known_faces()

def recognize_face_from_pil(pil_img: Image.Image, tolerance: float = 0.55) -> Optional[str]:
    if pil_img is None or len(KNOWN_FACE_ENCODINGS) == 0:
        return None
    rgb = np.array(pil_img.convert("RGB"))
    face_locations = face_recognition.face_locations(rgb)
    if not face_locations:
        return None
    encs = face_recognition.face_encodings(rgb, face_locations)
    if not encs:
        return None
    matches = face_recognition.compare_faces(KNOWN_FACE_ENCODINGS, encs[0], tolerance=tolerance)
    if True in matches:
        idx = matches.index(True)
        return KNOWN_FACE_NAMES[idx]
    return None

# =========================
# 3) SESSION STATE (5 ngày)
# =========================

if "meal_history" not in st.session_state:
    # mỗi phần tử là dict: {day, total_kcal, ratio_pct, tdee_kcal, avg_eaten_pct, notes, suggestions}
    st.session_state["meal_history"] = []

if "current_student" not in st.session_state:
    st.session_state["current_student"] = ""

# =========================
# 4) GIAO DIỆN CHÍNH
# =========================

st.title("🍱 AI Khay Cơm — Nhập tay + 5 ngày trung bình + Face ID")

# -------- Sidebar: thông tin học sinh (dùng cho tính TDEE) --------
st.sidebar.header("Thông tin học sinh (để tính nhu cầu năng lượng)")
age = st.sidebar.number_input("Tuổi", 6, 18, 12)
sex = st.sidebar.selectbox("Giới tính", ["Nam", "Nữ"])
weight = st.sidebar.number_input("Cân nặng (kg)", 10.0, 90.0, 40.0)
height = st.sidebar.number_input("Chiều cao (cm)", 90.0, 200.0, 145.0)
activity = st.sidebar.selectbox("Mức hoạt động", ["Ít vận động", "Vận động nhẹ", "Vận động trung bình", "Vận động mạnh"])
person = Person(age=age, sex=sex, weight_kg=weight, height_cm=height, activity=activity)

# -------- Chọn chế độ --------
mode = st.radio("Chọn chế độ", ["Manual input (nhập tay)", "Camera (Face ID)"], horizontal=True)

# ============================================================
# 5) CHẾ ĐỘ 1: MANUAL INPUT (NHẬP TRƯỚC ĂN + SAU ĂN) + LƯU 5 NGÀY
# ============================================================

if mode == "Manual input (nhập tay)":
    st.subheader("1) Nhập khẩu phần trước ăn (5 món)")

    food_choices = list(FOOD_DB.keys())
    portion_choices = ["0.5 phần", "1 phần", "1.5 phần"]

    cols = st.columns(5)
    before_items: List[FoodItem] = []

    for i in range(5):
        with cols[i]:
            f = st.selectbox(f"Món {i+1}", food_choices, key=f"food_{i}")
            p = st.selectbox("Phần", portion_choices, key=f"portion_{i}")
            item = lookup_food(f, p)
            mult = portion_multiplier(p)
            item.kcal *= mult
            item.protein *= mult
            item.fat *= mult
            item.carbs *= mult
            before_items.append(item)

    st.markdown("---")
    st.subheader("2) Đánh giá khay cơm (trước khi ăn)")

    if st.button("📌 Đánh giá khay cơm (trước ăn)"):
        before_report = evaluate_meal(person, before_items)
        st.session_state["before_items"] = before_items  # lưu để dùng cho “sau ăn”

        st.metric("TDEE (ước tính)", f"{before_report['tdee_kcal']} kcal")
        st.metric("Tổng kcal khay", f"{before_report['total_kcal']} kcal")
        st.metric("% TDEE", f"{before_report['ratio_pct']}%")

        st.write("Nhận xét:")
        for n in before_report["notes"]:
            st.write(f"- {n}")
        st.write("Gợi ý:")
        for g in before_report["suggestions"]:
            st.write(f"- {g}")

    # ------------------------------------------------------------
    # CÁCH 1: ĐẶT “SAU ĂN” NGAY SAU PHẦN ĐÁNH GIÁ (đúng yêu cầu bạn)
    # ------------------------------------------------------------
    st.markdown("---")
    st.subheader("3) Nhập lượng còn lại sau ăn (để tính phần đã ăn)")

    if "before_items" not in st.session_state:
        st.info("Hãy bấm 'Đánh giá khay cơm (trước ăn)' trước, rồi quay lại phần sau ăn.")
    else:
        left_choices = ["0.0 phần", "0.25 phần", "0.5 phần", "1 phần"]
        left_cols = st.columns(5)
        left_labels: List[str] = []

        for i in range(5):
            with left_cols[i]:
                v = st.selectbox(f"Còn lại món {i+1}", left_choices, key=f"left_{i}")
                left_labels.append(v)

        if st.button("📊 Tính sau ăn và lưu 1 ngày"):
            # tính món đã ăn
            eaten_items: List[FoodItem] = []
            ratios: List[float] = []
            before_items = st.session_state["before_items"]

            for idx, before in enumerate(before_items):
                before_p = portion_multiplier(before.portion_label)
                left_p = left_to_float(left_labels[idx])
                eaten_ratio = max(before_p - left_p, 0.0) / before_p if before_p > 0 else 0.0
                ratios.append(eaten_ratio)

                eaten_items.append(
                    FoodItem(
                        name=before.name,
                        kcal=before.kcal * eaten_ratio,
                        protein=before.protein * eaten_ratio,
                        fat=before.fat * eaten_ratio,
                        carbs=before.carbs * eaten_ratio,
                        portion_label=f"Đã ăn {round(eaten_ratio*100)}%",
                    )
                )

            day_report = evaluate_meal(person, eaten_items)
            avg_eaten_pct = (sum(ratios) / len(ratios)) * 100 if ratios else 0.0

            # lưu lịch sử 5 ngày (giữ tối đa 5 dòng gần nhất)
            st.session_state["meal_history"].append(
                {
                    "day": datetime.date.today().isoformat(),
                    "total_kcal": day_report["total_kcal"],
                    "ratio_pct": day_report["ratio_pct"],
                    "tdee_kcal": day_report["tdee_kcal"],
                    "avg_eaten_pct": round(avg_eaten_pct, 1),
                    "notes": " | ".join(day_report["notes"]),
                    "suggestions": " | ".join(day_report["suggestions"]),
                }
            )
            if len(st.session_state["meal_history"]) > 5:
                st.session_state["meal_history"] = st.session_state["meal_history"][-5:]

            st.success("✅ Đã lưu dữ liệu ngày ăn (1/5 ngày).")
            st.subheader("Kết quả ngày vừa lưu")
            st.metric("Năng lượng nạp", f"{day_report['total_kcal']} kcal")
            st.metric("% TDEE", f"{day_report['ratio_pct']}%")
            st.metric("Tỉ lệ ăn hết (trung bình 5 món)", f"{round(avg_eaten_pct,1)}%")

            st.write("Chi tiết món đã ăn:")
            st.dataframe(pd.DataFrame([vars(x) for x in eaten_items]))

    # ------------------------------------------------------------
    # BÁO CÁO 5 NGÀY (tự động khi đủ)
    # ------------------------------------------------------------
    st.markdown("---")
    st.subheader("4) Báo cáo 5 ngày (trung bình + xuất CSV)")

    history = st.session_state.get("meal_history", [])
    if len(history) < 5:
        st.info(f"Bạn mới có {len(history)}/5 ngày. Hãy tiếp tục lưu thêm cho đủ 5 ngày để tạo báo cáo.")
    else:
        last5 = history[-5:]
        avg_kcal = sum(d["total_kcal"] for d in last5) / 5
        avg_ratio = sum(d["ratio_pct"] for d in last5) / 5
        avg_eaten = sum(d["avg_eaten_pct"] for d in last5) / 5

        st.metric("Trung bình kcal/ngày (5 ngày)", f"{round(avg_kcal,1)} kcal")
        st.metric("Trung bình % TDEE (5 ngày)", f"{round(avg_ratio,1)}%")
        st.metric("Trung bình % ăn hết (5 ngày)", f"{round(avg_eaten,1)}%")

        if avg_ratio < 50:
            st.warning("Nhận xét: Ăn quá ít trong 5 ngày gần nhất.")
        elif avg_ratio < 80:
            st.info("Nhận xét: Ăn chưa đủ đều; cần tăng năng lượng và protein.")
        else:
            st.success("Nhận xét: Chế độ ăn 5 ngày gần nhất khá đạt.")

        # ----------------------------
        # FIX CSV TIẾNG VIỆT + KHÔNG CHÈN "bé" + ĐẦU CÂU CHÍNH TẢ
        # ----------------------------

        def clean_sentence(s: str) -> str:
            """Không thêm chữ bé, chỉ chuẩn hoá câu tiếng Việt."""
            if not s:
                return s
            s = s.strip()

            # Không tự động thêm chữ "bé", chỉ sửa chính tả đầu câu
            s = s[0].upper() + s[1:]

            # Thêm dấu chấm cuối câu nếu chưa có
            if not s.endswith("."):
                s += "."

            return s

        # Áp dụng cho dữ liệu 5 ngày
        df = pd.DataFrame(last5)

        # Đổi tên tiếng Việt cho cột
        df = df.rename(columns={
            "day": "Ngày",
            "total_kcal": "Tổng kcal",
            "ratio_pct": "Tỉ lệ % TDEE",
            "tdee_kcal": "TDEE (kcal)",
            "avg_eaten": "Trung bình ăn (%)",
            "notes": "Ghi chú",
            "suggestions": "Gợi ý"
        })

        # Chuẩn hoá tiếng Việt cho 2 cột dạng câu
        df["Ghi chú"] = df["Ghi chú"].apply(clean_sentence)
        df["Gợi ý"] = df["Gợi ý"].apply(clean_sentence)

        # Xuất với UTF-8-SIG để Excel không lỗi font
        csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

        st.download_button(
            label="⬇️ Tải báo cáo 5 ngày (CSV)",
            data=csv_bytes,
            file_name="bao_cao_5_ngay.csv",
            mime="text/csv"
        )



# ============================================================
# 6) CHẾ ĐỘ 2: CAMERA (Face ID + ảnh khay) – phần tối giản để bạn mở rộng sau
# ============================================================

else:
    st.subheader("Camera (Face ID + ảnh khay)")

    st.markdown("👉 Yêu cầu: trong thư mục dự án tạo thư mục `faces/` và đặt ảnh khuôn mặt (tên file = tên học sinh).")
    st.markdown("Ví dụ: `faces/Kiet.jpg`, `faces/Minh.png` ...")

    cam = st.camera_input("Chụp ảnh (để nhận diện học sinh + có thể dùng cho phân tích khay)")
    uploaded = st.file_uploader("Hoặc upload ảnh", type=["jpg", "jpeg", "png"])

    image_to_use = None
    if cam is not None:
        image_to_use = Image.open(cam).convert("RGB")
    elif uploaded is not None:
        image_to_use = Image.open(uploaded).convert("RGB")

    if image_to_use is not None:
        st.image(image_to_use, caption="Ảnh đã nhận", use_column_width=True)

        # Face ID
        student = recognize_face_from_pil(image_to_use, tolerance=0.55)
        if student:
            st.success(f"✅ Nhận diện học sinh: {student}")
            st.session_state["current_student"] = student
        else:
            st.warning("Không khớp khuôn mặt với thư viện faces/ (hoặc ảnh chưa đủ rõ).")

        # (Bạn có thể nối phần nhận diện món ăn ở đây sau này)
        st.info("Phần phân tích khay (AI nhận diện món) có thể gắn tiếp tại đây.")

    else:
        st.info("Hãy chụp hoặc tải ảnh lên để chạy Face ID.")

# =========================
# KẾT THÚC
# =========================
st.caption("Ghi chú: để Face ID hoạt động, cần thư mục `faces/` trong cùng thư mục app và có ảnh khuôn mặt theo tên học sinh.")
