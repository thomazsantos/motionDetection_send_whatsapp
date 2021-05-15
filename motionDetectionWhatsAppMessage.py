from twilio.rest import Client
import pyimgur
from datetime import datetime
import cv2
import time
import imutils


def takePicture(frame):
	file_name = datetime.now().strftime("%d-%m-%Y--%H:%M:%S") + ".jpg"
	cv2.imwrite(file_name , frame)
	print(file_name)
	time.sleep(1.00)
	return file_name

def uploadImage(frame):
	CLIENT_ID = "XXXXXXXXXXXXX"
	im = pyimgur.Imgur(CLIENT_ID)
	uploaded_image = im.upload_image(takePicture(frame), title="imagem")
	time.sleep(1.00)
	return uploaded_image.link


def sendMessageWhatsApp(frame):
	# Find your Account SID and Auth Token at twilio.com/console
	# and set the environment variables. See http://twil.io/secure
	account_sid = "XXXXXXXXXXXXX"
	auth_token =  "XXXXXXXXXXXXX"
	client = Client(account_sid, auth_token)

	message = client.messages.create(
                              body="System detected something " +  datetime.now().strftime("%D-%M-%Y %HH%SS"),
                              from_="whatsapp:+XXXXXXXXXXXXX",
                              to="whatsapp:+XXXXXXXXXXXXX",
                              media_url=uploadImage(frame)
                          )

	print(message.sid)
	time.sleep(2.00)


def motionDetection():
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)

    firstFrame = None

    while True:

        (grabbed, frame) = camera.read()
        text = "Sem Movimento"

        if not grabbed:
            break

        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if firstFrame is None:
            firstFrame = gray
            continue


        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]



        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)


        for c in cnts:

            if cv2.contourArea(c) > 2500:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Movimento Detectado!"
            sendMessageWhatsApp(frame)


        cv2.putText(frame, "Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.now().strftime("%D %M %Y %H:%M:%S" + " -- To exit press ""q"""),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)


        #cv2.imshow("Security Feed", frame)
        #cv2.imshow("Thresh", thresh)
        #cv2.imshow("Frame Delta", frameDelta)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()
    return;



motionDetection()
