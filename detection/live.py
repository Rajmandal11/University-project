from ultralytics import YOLO
import cv2


model = YOLO("yolo26n.pt")

cap = cv2.VideoCapture(0)


if not cap.isOpened():

    print("Camera could not be opened")

    exit()


while True:

    success, frame = cap.read()

    if not success:
        break

    results = model(
        frame,
        verbose=False
    )

    annotated = results[0].plot()

    cv2.imshow(
        "YOLO Live Detection",
        annotated
    )

    # Press X to exit
    if cv2.waitKey(1) & 0xFF == ord("x"):
        break


cap.release()

cv2.destroyAllWindows()