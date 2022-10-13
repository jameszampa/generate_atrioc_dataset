import cv2
from numpy import tile
import pytesseract

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    title = frame[415:440, 5:400]
    # title = cv2.resize(title, (430, 30))
    print(pytesseract.image_to_string(title))
    cv2.imshow("test", title)
    key = cv2.waitKey(5)
    if key == 27:
        break

cap.release()