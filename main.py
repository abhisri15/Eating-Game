import os
import random
import cv2
from cvzone.FaceMeshModule import FaceMeshDetector
import cvzone

cap = cv2.VideoCapture(0)
# cap.set(3, 1280) # 3 = WIDTH
# cap.set(4, 720)  # 4 = HEIGHT

windowName = "Image"
cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
cv2.resizeWindow(windowName, 1920, 1080)

detector = FaceMeshDetector(maxFaces=1)

idList = [0,17,78,292]

# import images
folderEatable = 'Objects/eatable'
listEatable = os.listdir(folderEatable)
print(listEatable)
eatables = []
for object in listEatable:
    eatables.append(cv2.imread(f'{folderEatable}/{object}', cv2.IMREAD_UNCHANGED))


folderNonEatable = 'Objects/noneatable'
listNonEatable = os.listdir(folderNonEatable)
print(listNonEatable)
nonEatables = []
for object in listNonEatable:
    nonEatables.append(cv2.imread(f'{folderNonEatable}/{object}', cv2.IMREAD_UNCHANGED))


currentObject = eatables[0]
pos = [300, 0]
speed = 5
count = 0
global isEatable
isEatable = True
gameOver = False


def resetObject():
    global isEatable

    pos[0] = random.randint(50,600)
    pos[1] = 0
    randNo = random.randint(0,1) # if you put (0,1) chances of eatable and non-eatable is 50:50
    # here since (0,2) is mentioned hence chance of eatable is twice of non-eatable

    if randNo == 0:
        currentObject = nonEatables[random.randint(0,3)]
        isEatable = False
    else:
        currentObject = eatables[random.randint(0,3)]
        isEatable = True

    return currentObject



while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # Flip the image horizontally
    if gameOver is False:
        img, faces = detector.findFaceMesh(img, draw=False)

        # Calculate the available space for overlay image
        availableWidth = img.shape[1] - pos[0]
        availableHeight = img.shape[0] - pos[1]

        # Resize the image in currentObject to fit the available space
        newWidth = max(min(availableWidth, 50), 1)  # Specify the desired width (limited to 85 pixels or available width, whichever is smaller)
        newHeight = max(min(availableHeight, 50), 1)  # Specify the desired height (limited to 85 pixels or available height, whichever is smaller)

        currentObject = cv2.resize(currentObject, (newWidth, newHeight))


        img = cvzone.overlayPNG(img, currentObject, pos)
        pos[1] += speed

        if pos[1]>520: # resolution size - size of object - extra margin size (anything you want)
            currentObject = resetObject()

        if faces:
            face = faces[0]
            # for idNo, point in enumerate(face):
            #     cv2.putText(img, str(idNo), point, cv2.FONT_HERSHEY_PLAIN, 0.7, (255,0, 255), 1)
            # for id in idList:
            #     cv2.circle(img, face[id], 5,(255,0,255),5)
            # cv2.line(img, face[idList[0]], face[idList[1]], (0,255,0), 3)
            # cv2.line(img, face[idList[2]], face[idList[3]], (0,255,0), 3)

            up = face[idList[0]]
            down = face[idList[1]]
            left = face[idList[2]]
            right = face[idList[3]]

            upDown, _ = detector.findDistance(face[idList[0]],face[idList[1]])
            leftRight, _ = detector.findDistance(face[idList[2]],face[idList[3]])

            imgPos = (pos[0]+20, pos[1]+20)
            cx, cy = (up[0] + down[0]) // 2, (up[1] + down[1]) // 2
            cv2.line(img, (cx, cy), imgPos, (0, 255, 0), 1)

            distMouthObject, _ = detector.findDistance((cx, cy),((pos[0]+20, pos[1]+20)))
            print(distMouthObject)

            # Lip opened or closed

            ratio = int(+(upDown/leftRight)*100)
            # print(ratio)
            if ratio>50:
                mouthStatus='Open'
            else:
                mouthStatus='Closed'

            cv2.putText(img, mouthStatus, (10, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

            if distMouthObject<50 and ratio>60: # distMouthObject to check if mouth eat object and ratio to check if mouth open
                if isEatable:
                    currentObject = resetObject()
                    count +=1
                else:
                    gameOver = True
        cv2.putText(img, str(count), (570, 50), cv2.FONT_HERSHEY_PLAIN, 2.5, (255, 0, 255), 2)

    else:
        cv2.putText(img, "Game Over", (10, 250), cv2.FONT_HERSHEY_PLAIN, 7, (255, 0, 255), 10)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord(' '):
        resetObject()
        gameOver = False
        count = 0
        currentObject = eatables[0]
        isEatable = True