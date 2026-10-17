from ultralytics import YOLO
import cv2
import numpy as np


# =========================================================
# LOAD YOLO MODEL ONCE
# =========================================================

MODEL_PATH = "yolo26n.pt"

model = YOLO(MODEL_PATH)


# =========================================================
# IMAGE DETECTION
# =========================================================

def detect_image(image_path):
    """
    Run YOLO object detection on an image.
    """

    results = model.predict(
        source=image_path,
        conf=0.25,
        verbose=False
    )

    result = results[0]

    detections = []

    for box in result.boxes:

        class_id = int(box.cls[0])

        confidence = float(box.conf[0])

        class_name = result.names[class_id]

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        detections.append({
            "class": class_name,
            "confidence": round(confidence, 2),
            "box": [
                round(x1),
                round(y1),
                round(x2),
                round(y2)
            ]
        })

    return result, detections


# =========================================================
# VIDEO DETECTION
# =========================================================

def detect_video(video_path, output_path):
    """
    Process video frame-by-frame using YOLO.
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError("Could not open video")

    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25

    # MP4 writer
    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    frame_count = 0

    all_detections = []

    while True:

        success, frame = cap.read()

        if not success:
            break

        # YOLO detection
        results = model.predict(
            source=frame,
            conf=0.25,
            verbose=False
        )

        result = results[0]

        # Draw bounding boxes
        annotated_frame = result.plot()

        # Save frame to output video
        writer.write(
            annotated_frame
        )

        # Store detections
        frame_detections = []

        for box in result.boxes:

            class_id = int(box.cls[0])

            confidence = float(box.conf[0])

            class_name = result.names[class_id]

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            frame_detections.append({
                "class": class_name,
                "confidence": round(
                    confidence,
                    2
                ),
                "box": [
                    round(x1),
                    round(y1),
                    round(x2),
                    round(y2)
                ]
            })

        all_detections.append({
            "frame": frame_count,
            "detections": frame_detections
        })

        frame_count += 1

    cap.release()

    writer.release()

    return all_detections


# =========================================================
# LIVE CAMERA
# =========================================================

def generate_camera():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        frame = np.zeros((480, 854, 3), dtype=np.uint8)

        cv2.putText(
            frame,
            "CAMERA UNAVAILABLE",
            (180, 230),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 229, 255),
            2,
            cv2.LINE_AA
        )

        success, buffer = cv2.imencode(
            ".jpg",
            frame
        )

        if success:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )

        return

    while True:

        success, frame = cap.read()

        if not success:
            break

        # YOLO
        results = model.predict(
            source=frame,
            conf=0.25,
            verbose=False
        )

        result = results[0]

        # Draw bounding boxes
        annotated_frame = result.plot()

        # Convert frame to JPEG
        success, buffer = cv2.imencode(
            ".jpg",
            annotated_frame
        )

        if not success:
            continue

        frame_bytes = buffer.tobytes()

        # Django streaming format
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )

    cap.release()