import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import io

st.set_page_config(page_title="YOLO Custom Model UI", layout="wide")

st.title("Automatic Crater and boulder Detection Project")
st.markdown("Upload images, choose confidence threshold and image size. Uses your custom weights (CPU-friendly).")

# ---- USER CONFIG ----
# Change this path to your custom weights (e.g. 'runs/train/exp/weights/best.pt' or 'best.pt')
WEIGHTS_PATH = r"D:\MAJOR PROJECT\best.pt"

# Device: 'cpu' (your machine is CPU-only). If you ever have GPU, set 'cuda:0'
DEVICE = "cpu"

# Try to load model (wrap in try/except so UI shows helpful error)
@st.cache_resource(show_spinner=False)
def load_model(weights_path: str, device: str):
    try:
        model = YOLO(weights_path)
        # set device explicitly when calling predict; we still return model object
        return model
    except Exception as e:
        st.error(f"Error loading model from '{weights_path}': {e}")
        return None

model = load_model(WEIGHTS_PATH, DEVICE)

if model is None:
    st.stop()

# Sidebar controls
st.sidebar.header("Inference settings")
conf_thres = st.sidebar.slider("Confidence threshold", 0.0, 1.0, 0.25, 0.01)
iou_thres = st.sidebar.slider("NMS IoU threshold", 0.0, 1.0, 0.45, 0.01)
img_size = st.sidebar.selectbox("Inference image size (pixels)", [320, 416, 512, 640, 768], index=3)
show_raw = st.sidebar.checkbox("Show raw prediction table", value=False)
max_images = st.sidebar.number_input("Max images to run at once", min_value=1, max_value=8, value=3)

st.sidebar.markdown("---")
st.sidebar.write("Weights:")
st.sidebar.code(WEIGHTS_PATH)

# File uploader (allow multiple)
uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Run button
run_button = st.button("Run Detection")

# Helper to convert result to displayable PIL image
def plot_result_image(result):
    # results[0].plot() returns numpy array (BGR->RGB handled by PIL conversion)
    arr = result.plot()
    if isinstance(arr, np.ndarray):
        return Image.fromarray(arr)
    else:
        # fallback: if ultralytics returns PIL already
        return arr

# Show predictions area
if uploaded_files:
    # Limit images shown to max_images
    files = uploaded_files[:max_images]
    cols = st.columns(len(files))
    if run_button:
        for i, file in enumerate(files):
            with cols[i]:
                img = Image.open(file).convert("RGB")
                st.image(img, caption=f"Input #{i+1}", use_column_width=True)
                st.write("Running inference...")

                # Run inference on CPU with given settings
                # note: save=False prevents writing to runs/detect/...
                try:
                    results = model.predict(
                        source=img,
                        imgsz=img_size,
                        conf=conf_thres,
                        iou=iou_thres,
                        device=DEVICE,
                        save=False,     # do not save to disk
                        verbose=False
                    )
                except Exception as e:
                    st.error(f"Inference error: {e}")
                    continue

                if len(results) == 0 or results[0].boxes.shape[0] == 0:
                    st.warning("No detections.")
                else:
                    # Visualize predicted image with boxes
                    out_img = plot_result_image(results[0])
                    st.image(out_img, caption="Detections", use_column_width=True)

                    # Optionally show raw predictions in a table
                    if show_raw:
                        # Build a small table: class, conf, x1,y1,x2,y2
                        rows = []
                        boxes = results[0].boxes  # Boxes object
                        # boxes.data: (N,6) -> [x1,y1,x2,y2,conf,class]
                        if hasattr(boxes, "data"):
                            for b in boxes.data.tolist():
                                x1, y1, x2, y2, conf, cls = b
                                cls = int(cls)
                                name = model.model.names[cls] if hasattr(model, "model") and hasattr(model.model, "names") else str(cls)
                                rows.append({"class": name, "conf": float(conf), "x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)})
                        else:
                            # Fallback: use boxes.xyxy and boxes.conf/boxes.cls if available
                            xyxy = boxes.xyxy.tolist() if hasattr(boxes, "xyxy") else []
                            confs = boxes.conf.tolist() if hasattr(boxes, "conf") else []
                            clss = boxes.cls.tolist() if hasattr(boxes, "cls") else []
                            for j in range(len(xyxy)):
                                x1, y1, x2, y2 = xyxy[j]
                                conf = confs[j] if j < len(confs) else None
                                cls = int(clss[j]) if j < len(clss) else None
                                name = model.model.names[cls] if hasattr(model, "model") and hasattr(model.model, "names") else str(cls)
                                rows.append({"class": name, "conf": float(conf) if conf is not None else None, "x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)})

                        st.write("Detections table:")
                        st.table(rows)
else:
    st.info("Upload 1 or more images and press 'Run Detection'.")

# Footer: small tips
st.markdown("---")
st.write("Tips:")
st.markdown("""
- If you get memory/slow inference on CPU, reduce `img size` or `max images`.  
- To use a GPU later, change `DEVICE = 'cuda:0'` and run on a machine with CUDA.  
- Ensure `WEIGHTS_PATH` points to your custom `.pt` file (trained weights).
""")
