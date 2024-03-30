import cv2
import time
import glob
import os
from emailing import send_email
from threading import Thread

# Activation of camera, int will represent which camera will be use
video = cv2.VideoCapture(0)
time.sleep(1)

# Storage of the first frame
first_frame = None

# List to trigger the emailing function
status_list = []

# Counter to write the frames
count = 1


# Function to clean up the images directory from old files
def clean_folder():
    images =glob.glob("images/*png")
    for image in images:
        os.remove(image)


while True:
    status = 0
    # Write the frame
    check, frame = video.read()
    # Processing of the frame to gray scale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)
    # Processing of the frame to gau scale
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # Write the first frame into the storage
    if first_frame is None:
        first_frame = gray_frame_gau

    # Get the pixels differences between the first frame and the next frames
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    # Processing to clear the frame, the differences will be white
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    # Reduction of noise
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # Finding the corners to write the contour of the differences between
    # first frame and next frames
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Reducing the fake differences and write the rectangle
    for contour in contours:
        if cv2.contourArea(contour) < 5_000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        # When the trigger is active use the function to send email
        if rectangle.any():
            status = 1
            # Store the frame
            cv2.imwrite (f"images/{count}.png", frame)
            count = count + 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    # If the new object will appear the status will change to 1
    status_list.append(status)
    status_list = status_list[-2:]
    # If the object will be no longer in the frame, the status will change
    # from 1 to 0, and the emailing function will be called
    if status_list[0] == 1 and status_list[1] == 0:
        # Using threading to avoid freezing the program
        email_thread = Thread(target=send_email, args=(image_with_object, ))
        email_thread.daemon = True
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True

        email_thread.start()
        clean_thread.start()

    cv2.imshow("My video", frame)

    # Creating exit key
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

video.release()
