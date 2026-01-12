import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import tempfile

# Page settings
st.set_page_config(page_title="Crater & Boulder Detection", layout="centered")

st.title("🌕 Lunar Crater & Boulder Detection")
st.write("Upload an image to detect craters and boulders using YOLOv8.")

# Load YOLOv8 Model
@st.cache_resource
   # Make sure best.pt is in same folder
def load_model():
    model = YOLO("best.pt")
    return model
WEIGHTS_PATH = r"/content/runs/detect/train3/weights"
DEVICE = "cpu"

uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Save temp image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name

    model = load_model(WEIGHTS_PATH, DEVICE)
    if st.button("🔍 Detect Craters & Boulders"):
        with st.spinner("Detecting..."):
            results = model(temp_path)

            # Display result
            result_img = results[0].plot()
            st.image(result_img, caption="Detection Result", use_column_width=True)

            st.success("✅ Detection Completed!")
