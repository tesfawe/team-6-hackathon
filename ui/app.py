import atexit
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import cv2
from PIL import Image
import io
import base64

st.set_page_config(
    page_title="Aptar WareSight",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"  # Ensures sidebar remains open
)


# Custom CSS to style the app similar to the original design
st.markdown("""
<style>
    /* Main color variables */
    :root {
        --primary: #3f51b5;
        --secondary: #f50057;
        --success: #4caf50;
        --danger: #f44336;
        --light: #f5f5f5;
        --dark: #212121;
        --gray: #9e9e9e;
    }
    
    /* Header styling */
    .main-header {
        background-color: #3f51b5;
        color: white;
        padding: 4rem 2rem 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: -16px -16px 0px -16px;
    }
    
    .logo {
        font-size: 1.5rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Container styling */
    .container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #eee;
    }
    
    /* Results styling */
    .result-item {
        padding: 0.8rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        background-color: #f5f5f5;
    }
    
    .result-item.accepted {
        border-left: 4px solid #4caf50;
    }
    
    .result-item.rejected {
        border-left: 4px solid #f44336;
    }
    
    .result-timestamp {
        font-size: 0.8rem;
        color: #9e9e9e;
    }
    
    .result-details {
        display: flex;
        justify-content: space-between;
        margin-top: 0.5rem;
    }
    
    .result-count {
        font-weight: bold;
    }
    
    .accepted-status {
        font-weight: bold;
        color: #4caf50;
    }
    
    .rejected-status {
        font-weight: bold;
        color: #f44336;
    }
    
    /* Metrics styling */
    .metrics-container {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }
    
    .metric-card {
        flex: 1;
        padding: 1rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin: 0 0.5rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #9e9e9e;
        font-size: 0.9rem;
    }
    
    /* Feed display styling */
    .feed-overlay {
        position: relative;
        margin-bottom: 1rem;
    }
    
    .feed-info {
        position: absolute;
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 0.5rem;
        font-size: 0.8rem;
        width: 100%;
    }
    
    .feed-info-top {
        top: 0;
        display: flex;
        justify-content: space-between;
    }
    
    .feed-info-bottom {
        bottom: 0;
        display: flex;
        justify-content: space-between;
    }
    
    /* Streamlit specific overrides */
    .stButton button {
        background-color: #3f51b5;
        color: white;
        font-weight: bold;
    }
    
    .stButton button:hover {
        background-color: #303f9f;
    }
    
    div.block-container {
        padding-top: 0;
    }
    
    /* Make the slider thumbs match the design */
    .stSlider div[data-baseweb="slider"] div[role="slider"] {
        background-color: #3f51b5;
    }
    
    /* File uploader */
    .file-upload-container {
        border: 2px dashed #ddd;
        padding: 1.5rem;
        text-align: center;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    /* Custom toggle switch similar to original design */
    .toggle-container {
        display: flex;
        align-items: center;
    }
    
    .toggle-label {
        margin-right: 0.5rem;
        font-weight: bold;
    }
            
    
</style>
""", unsafe_allow_html=True)

# Custom header
st.markdown("""
<div class="main-header">
    <div class="logo">
        <i class="fas fa-cubes"></i> Aptar WareSight
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = [
        {"timestamp": "27 Feb 2025, 14:32:45", "count": 5, "status": "Accepted"},
        {"timestamp": "27 Feb 2025, 14:31:22", "count": 3, "status": "Accepted"},
        {"timestamp": "27 Feb 2025, 14:29:57", "count": 2, "status": "Rejected"},
        {"timestamp": "27 Feb 2025, 14:28:03", "count": 6, "status": "Accepted"},
        {"timestamp": "27 Feb 2025, 14:27:11", "count": 4, "status": "Accepted"},
        {"timestamp": "27 Feb 2025, 14:26:39", "count": 1, "status": "Rejected"},
        {"timestamp": "27 Feb 2025, 14:25:22", "count": 3, "status": "Accepted"},
        {"timestamp": "27 Feb 2025, 14:24:05", "count": 5, "status": "Accepted"}
    ]

if 'cameras' not in st.session_state:
    st.session_state.cameras = [
        # Added webcam as the first option with device id 0
        {"name": "Webcam", "ip": "0"},
        {"name": "Camera 1 - Warehouse Entrance", "ip": "192.168.1.101"},
        {"name": "Camera 2 - Loading Bay", "ip": "192.168.1.102"},
        {"name": "Camera 3 - Sorting Area", "ip": "192.168.1.103"}
    ]

if 'active_camera' not in st.session_state:
    st.session_state.active_camera = "Webcam"  # Set webcam as default active camera

if 'live_mode' not in st.session_state:
    st.session_state.live_mode = True

if 'admin_modal' not in st.session_state:
    st.session_state.admin_modal = False

# For webcam capture
if 'cap' not in st.session_state:
    st.session_state.cap = None

# Initialize webcam for the first time
if st.session_state.active_camera == "Webcam" and st.session_state.cap is None:
    try:
        st.session_state.cap = cv2.VideoCapture(
            0)  # 0 is usually the default webcam
        if not st.session_state.cap.isOpened():
            st.warning("Could not open webcam. Using mock data instead.")
            st.session_state.cap = None
    except Exception as e:
        st.error(f"Error opening webcam: {e}")
        st.session_state.cap = None

# Sample metrics data
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        "total_detections": 1247,
        "acceptance_rate": 87.3,
        "avg_stack_height": 4.2,
        "active_time": "6:42"
    }

# Create 3-column layout
col1, col2, col3 = st.columns([1, 3, 1])

# Column 1: Input Section
with col1:
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Input Source</div>',
                unsafe_allow_html=True)

    # Live detection toggle
    st.markdown('<div class="toggle-container">', unsafe_allow_html=True)
    st.markdown('<span class="toggle-label">Live Detection</span>',
                unsafe_allow_html=True)
    live_mode = st.checkbox(
        "", value=st.session_state.live_mode, key="live_toggle")
    st.session_state.live_mode = live_mode
    st.markdown('</div>', unsafe_allow_html=True)

    # Camera selection
    st.markdown('<label class="input-label">Select Camera</label>',
                unsafe_allow_html=True)
    camera_options = [cam["name"] for cam in st.session_state.cameras]
    camera_options.insert(0, "-- Select Camera --")
    selected_camera = st.selectbox(
        "",
        options=camera_options,
        index=camera_options.index(
            st.session_state.active_camera) if st.session_state.active_camera in camera_options else 0,
        key="camera_select"
    )

    # Handle camera change
    if selected_camera != "-- Select Camera --" and selected_camera != st.session_state.active_camera:
        # Release previous camera if it was active
        if st.session_state.cap is not None:
            st.session_state.cap.release()
            st.session_state.cap = None

        st.session_state.active_camera = selected_camera

        # If webcam is selected, initialize capture
        if selected_camera == "Webcam":
            try:
                st.session_state.cap = cv2.VideoCapture(0)
                if not st.session_state.cap.isOpened():
                    st.warning(
                        "Could not open webcam. Using mock data instead.")
                    st.session_state.cap = None
            except Exception as e:
                st.error(f"Error opening webcam: {e}")
                st.session_state.cap = None

    # File upload
    st.markdown('<label class="input-label">Upload Image/Video</label>',
                unsafe_allow_html=True)

    # Custom file uploader styling
    st.markdown("""
    <div class="file-upload-container">
        <div style="font-size: 2rem; color: #9e9e9e;">
            <i class="fas fa-cloud-upload-alt"></i>
        </div>
        <div>Drag & drop or click to upload</div>
        <div style="font-size: 0.8rem; margin-top: 0.5rem; color: #9e9e9e;">
            Supported formats: JPG, PNG, MP4
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "", type=["jpg", "png", "mp4"], label_visibility="collapsed")

    # Start detection button
    start_btn = st.button("Start Detection", use_container_width=True)

    # Detection settings
    st.markdown('<div class="detection-settings">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Detection Settings</div>',
                unsafe_allow_html=True)

    confidence = st.slider("Confidence Threshold", 0, 100, 75, format="%d%%")
    st.markdown('<div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: -15px;">'
                '<span>0%</span><span>75%</span><span>100%</span></div>',
                unsafe_allow_html=True)

    min_stack = st.slider("Min Stack Height", 1, 10, 3)
    st.markdown('<div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-top: -15px;">'
                '<span>1</span><span>3</span><span>10</span></div>',
                unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close container

# Column 2: Video Section
with col2:

    def generate_mock_frame():
        # Create a black frame
        frame = np.zeros((450, 800, 3), dtype=np.uint8)

        # Add some background (gray)
        cv2.rectangle(frame, (0, 0), (800, 450), (100, 100, 100), -1)

        # Add mock boxes in the scene
        box_positions = [
            ((250, 120), (330, 180)),  # (x,y, width, height)
            ((250, 180), (330, 240)),
            ((250, 240), (330, 300)),
            ((400, 150), (470, 200)),
            ((400, 200), (470, 250))
        ]

        for start, end in box_positions:
            cv2.rectangle(frame, start, end, (0, 255, 0), 2)

        return frame

    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Live Feed</div>',
                unsafe_allow_html=True)

    # Create a placeholder for the video feed
    feed_placeholder = st.empty()

    # Create stop/start controls
    if 'feed_active' not in st.session_state:
        st.session_state.feed_active = False

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("Start", use_container_width=True, disabled=st.session_state.feed_active):
            st.session_state.feed_active = True

    with col_stop:
        if st.button("Stop", use_container_width=True, disabled=not st.session_state.feed_active):
            st.session_state.feed_active = False

    # Update single frame if feed is active
    if st.session_state.feed_active:
        current_time = datetime.now()
        if st.session_state.cap is not None and st.session_state.cap.isOpened():
            ret, frame = st.session_state.cap.read()
            if ret:
                frame = cv2.resize(frame, (800, 450))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame = generate_mock_frame()
        else:
            frame = generate_mock_frame()

        # Convert to PIL Image
        image = Image.fromarray(frame)

        # Update the feed in the placeholder
        with feed_placeholder.container():
            st.markdown('<div class="feed-overlay">', unsafe_allow_html=True)
            st.image(image, use_container_width=True)

            time_str = current_time.strftime("%d %b %Y, %H:%M:%S")
            st.markdown(f"""
            <div class="feed-info feed-info-top">
                <div>{st.session_state.active_camera}</div>
                <div>{time_str}</div>
            </div>
            <div class="feed-info feed-info-bottom">
                <div>Processing: 24 FPS</div>
                <div>Status: Active</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Rerun the app to update the feed
        time.sleep(0.04)  # Control frame rate
        st.rerun()
    else:
        # Show placeholder image when feed is not active
        frame = generate_mock_frame()
        image = Image.fromarray(frame)
        with feed_placeholder.container():
            st.markdown('<div class="feed-overlay">', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown("""
            <div class="feed-info feed-info-bottom">
                <div>Status: Inactive</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Custom CSS for styling the metric boxes
    st.markdown("""
        <style>
            .metrics-container {
                display: flex;
                justify-content: space-around;
                gap: 10px;
                margin-top: 20px;
            }

            .metric-card {
                flex: 1;
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
                padding: 20px;
                text-align: center;
                min-width: 150px;
            }

            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #212121;
                margin: 5px 0;
            }

            .metric-label {
                color: #757575;
                font-size: 0.9rem;
            }

            .metric-subtext {
                color: #9e9e9e;
                font-size: 0.8rem;
                margin-top: 5px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Dummy data for metrics
    metrics = {
        "total_detections": 1247,
        "acceptance_rate": 87.3,
        "avg_stack_height": 4.2,
        "active_time": "6:42"
    }

    # Metric Display
    st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-card">
                <div class="metric-label">Total Detections</div>
                <div class="metric-value">{metrics["total_detections"]}</div>
                <div class="metric-subtext">Today</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Acceptance Rate</div>
                <div class="metric-value">{metrics["acceptance_rate"]}</div>
                <div class="metric-subtext">Today</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Avg. Stack Height</div>
                <div class="metric-value">{metrics["avg_stack_height"]}</div>
                <div class="metric-subtext">Today</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Active Time</div>
                <div class="metric-value">{metrics["active_time"]}</div>
                <div class="metric-subtext">Hours:Minutes</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# Column 3: Results Section
with col3:
    st.markdown('<div class="container">', unsafe_allow_html=True)

    # Detection results header with export button
    col3a, col3b = st.columns([3, 1])
    with col3a:
        st.markdown(
            '<div class="section-title">Detection Results</div>', unsafe_allow_html=True)
    with col3b:
        export_btn = st.button("📥 Export")

    # Results list
    for result in st.session_state.detection_results:
        status_class = "accepted" if result["status"] == "Accepted" else "rejected"
        status_style_class = "accepted-status" if result["status"] == "Accepted" else "rejected-status"

        st.markdown(f"""
        <div class="result-item {status_class}">
            <div class="result-timestamp">{result["timestamp"]}</div>
            <div class="result-details">
                <div class="result-count">{result["count"]} Boxes</div>
                <div class="{status_style_class}">{result["status"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # Close container

# Add settings button to sidebar and create admin modal
st.sidebar.title("Administration")

if st.sidebar.button("Camera Management", use_container_width=True):
    st.session_state.admin_modal = True

# Admin modal (camera management)
if st.session_state.admin_modal:
    with st.sidebar.expander("Camera Management", expanded=True):
        tabs = st.tabs(["Cameras", "System Settings", "Alerts"])

        with tabs[0]:
            st.subheader("Connected Cameras")

            for i, camera in enumerate(st.session_state.cameras):
                col_cam, col_edit, col_delete = st.columns([3, 1, 1])
                with col_cam:
                    st.markdown(f"""
                    <div style="font-weight: bold;">{camera['name']}</div>
                    <div style="font-size: 0.8rem; color: #9e9e9e;">IP: {camera['ip']}</div>
                    """, unsafe_allow_html=True)
                with col_edit:
                    st.button("✏️", key=f"edit_{i}")
                with col_delete:
                    st.button("🗑️", key=f"delete_{i}")

            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Add New Camera")

            new_cam_name = st.text_input(
                "Camera Name", placeholder="e.g. Warehouse Exit")
            new_cam_ip = st.text_input(
                "IP Address / RTSP URL", placeholder="e.g. rtsp://192.168.1.104:554/stream")

            col_username, col_password = st.columns(2)
            with col_username:
                cam_username = st.text_input(
                    "Username (Optional)", placeholder="Camera username")
            with col_password:
                cam_password = st.text_input(
                    "Password (Optional)", placeholder="Camera password", type="password")

            if st.button("Add Camera", use_container_width=True):
                if new_cam_name and new_cam_ip:
                    st.session_state.cameras.append({
                        "name": new_cam_name,
                        "ip": new_cam_ip
                    })
                    st.success(f"Camera '{new_cam_name}' added successfully!")
                    st.rerun()
                else:
                    st.error("Camera name and IP address are required")

        with tabs[1]:
            st.subheader("System Settings")
            st.slider("Detection Frequency (fps)", 1, 30, 24)
            st.slider("Storage Retention (days)", 1, 30, 7)
            save_settings = st.button(
                "Save Settings", use_container_width=True)

        with tabs[2]:
            st.subheader("Alert Configuration")
            st.checkbox("Email Alerts", value=True)
            st.checkbox("SMS Alerts", value=False)
            alert_threshold = st.number_input(
                "Alert Threshold (% rejected)", value=20, min_value=0, max_value=100)
            contact_email = st.text_input(
                "Contact Email", value="admin@example.com")
            save_alerts = st.button(
                "Save Alert Settings", use_container_width=True)


def update_data():
    # Update timestamp
    current_time = datetime.now()
    time_str = current_time.strftime("%d %b %Y, %H:%M:%S")

    # Add new detection results occasionally (simulation)
    if np.random.random() < 0.2:  # 20% chance of new detection
        new_count = np.random.randint(1, 7)
        new_status = "Accepted" if new_count >= 3 else "Rejected"

        st.session_state.detection_results.insert(0, {
            "timestamp": time_str,
            "count": new_count,
            "status": new_status
        })

        # Keep only the recent 8 results
        st.session_state.detection_results = st.session_state.detection_results[:8]

        # Update metrics
        st.session_state.metrics["total_detections"] += 1

        # Update acceptance rate
        accepted_count = sum(
            1 for item in st.session_state.detection_results if item["status"] == "Accepted")
        st.session_state.metrics["acceptance_rate"] = round(
            accepted_count / len(st.session_state.detection_results) * 100, 1)

        # Update average stack height
        st.session_state.metrics["avg_stack_height"] = round(sum(
            item["count"] for item in st.session_state.detection_results) / len(st.session_state.detection_results), 1)


# Add a footer
st.markdown("""
<div style="text-align: center; margin-top: 20px; padding: 10px; color: #9e9e9e; font-size: 0.8rem;">
    Box Stack Detection System © 2025 | Version 1.0.0
</div>
""", unsafe_allow_html=True)


def cleanup():
    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None


# Register the cleanup function
atexit.register(cleanup)

# For demo purposes, we could add a rerun callback to update the UI
# In a real application, you would use WebRTC or other streaming methods
if st.session_state.live_mode:
    update_data()
    # Uncomment for a more dynamic demo (but be careful with rate limits)
    # time.sleep(1)
    st.rerun()
