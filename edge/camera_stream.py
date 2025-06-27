from flask import Flask, Response
import cv2
import time
import os

VIDEO_DEVICE = '/dev/video42'

app = Flask(__name__)

def generate_frames():
    print(f"Opening video device: {VIDEO_DEVICE}")
    cap = cv2.VideoCapture(VIDEO_DEVICE)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {VIDEO_DEVICE}")

    while True:
        success, frame = cap.read()
        if not success:
            print("⚠️ Failed to read frame")
            time.sleep(0.1)
            continue

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print(f"Starting Flask MJPEG stream on http://<EDGE_IP>:8081/video")
    app.run(host='0.0.0.0', port=8081, debug=False, threaded=True)
