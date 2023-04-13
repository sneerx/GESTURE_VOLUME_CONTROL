import cv2
import mediapipe as mp
import time
import numpy as np
import HandTrackModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#############################
# wCam, hCam = 640, 480 # kameranın ayarlarını söyledik spec
#############################

cap = cv2.VideoCapture(0)
# cap.set(3, wCam)
# cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.85,trackCon=0.75)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVolume = volRange[0]
maxVolume = volRange[1]

volBar = 400
volPercentage = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img) # img'e eşitledik çünkü bize findHands fonksiyonu bir return img sorgusu gönderiyor bu img sorgusunu işlememiz lazım o yüzden yaptık.
    lmList = detector.findPosition(img,draw=False)

    if len(lmList) !=0:
        #print(lmList[4],lmList[8])

        x1, y1 = lmList[4][1],lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2) // 2, (y1+y2) // 2

        cv2.circle(img, (x1,y1), 10,(255,0,255),cv2.FILLED) # BAS PARMAK NOKTASI
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED) # İŞARET PARMAK NOKTASI
        cv2.line(img, (x1,y1),(x2,y2),(255,0,255),3) # BİR UCUNDAN DİGERİNE CİZGİYİ ÇİZDİK
        cv2.circle(img, (cx, cy), 2, (255, 0, 255), cv2.FILLED) # ORTAYA BİR NOKTA KOYDUK

        length = math.hypot(x2-x1,y2-y1) # İKİSİ ARASINDAKİ MESAFEYİ BULAN FONKSİYON (ÖNEMLİ)

        #print(length)
        # hand range 20 - 210
        # volume range -65 - 0

        vol = np.interp(length,[20,210],[minVolume,maxVolume]) # interp fonksiyonu iki degeri birbirine dönüştürmeye yarıyor önemli bir fonksiyon
        volBar = np.interp(length, [20, 210], [400, 150])
        volPercentage = np.interp(length, [20, 210], [0, 100])
        print(int(length),vol)
        volume.SetMasterVolumeLevel(vol, None)


        if length < 50: # EGER 50 DEN KÜCÜK BİR DEGERE GİRERSE BUTON GÖREVİ GÖREREK CALISIYOR MESAFEYE GÖRE ETKİNLEŞTİRME SAYILABİLİR.
            cv2.circle(img, (cx, cy), 10, (255, 255, 0), cv2.FILLED)


    cv2.rectangle(img, (50,150), (85, 400),(0, 255 ,0), 3)  # SES KONTROL BARI - dıs cizgi
    cv2.rectangle(img, (50,int(volBar)),(84,400),(0,255,0),cv2.FILLED) # iç dolgusu
    cv2.putText(img, f'{int(volPercentage)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (12, 0, 75), 3)



    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, f'fps: {int(fps)}', (40, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (12, 115, 75), 3)

    cv2.imshow("Scene1", img)
    cv2.waitKey(1)