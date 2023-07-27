import serial
import cv2
import numpy as np

serial_port = 'COM3'
baud_rate = 115200
enlarge = 50
ser = serial.Serial(serial_port, baud_rate)    
header = r"00fe80b7"
tail = r"ffff68ff"

def get_yoga_mat_data():
    data = ['']
    pre_data = ""
    next_data = ""

    while True:
        data = ser.read(237).hex()
        if header in data:
            arr = data.split(header)
            pre_data = arr[0]
            next_data = arr[1]
            a = next_data + pre_data
            a = a[26:-8]
            a = [int("0x" + a[i:i+2], base=16) for i in range(0, 432, 2)]
            a = np.array(a).reshape((12, 18))
            a = (a > 30) * a
            return a
            #cvheatmap(a)
            # if cv2.waitKey(1) == ord('q'):
            #     break
    #cv2.destroyAllWindows()

def find_center_force(heatmap_arr):
    centers = []
    for (x, y), value in np.ndenumerate(heatmap_arr):
        if value > 100:
            centers.append([x,y,value])
    if centers:
        output_x=0
        output_y=0
        acum_w=0
        for (x,y,w) in centers:
            output_x += w*x
            output_y += w*y
            acum_w+=w
        return np.array([output_x/acum_w,output_y/acum_w]).astype(int)
    else:
        return np.array([])
    
def get_heatmap():
    data = get_yoga_mat_data()
    rescaled_array = cv2.resize(data.astype('uint8'), dsize=(18 * enlarge , 12 * enlarge)) 
    rescaled_array = cv2.normalize(rescaled_array, None, 0, 255, norm_type= cv2.NORM_MINMAX, dtype= cv2.CV_8U)
    heatmap = cv2.applyColorMap(rescaled_array, cv2.COLORMAP_JET)
    center = find_center_force(data)
    if center.size != 0 :
        cv2.circle(heatmap, [(center[1]*enlarge)+25, (center[0]*enlarge)+25], 10, (255, 255, 255), 1)
    heatmap = cv2.rotate(heatmap, cv2.ROTATE_180)
    #cv2.imshow('Heatmap', heatmap)
    return heatmap

def find_bounding_box(heatmap):
    #https://stackoverflow.com/questions/58419893/generating-bounding-boxes-from-heatmap-data
    # Grayscale then Otsu's threshold
    gray = cv2.cvtColor(heatmap, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Find contours
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(heatmap, (x, y), (x + w, y + h), (36,255,12), 2)
    #cv2.imshow('thresh', thresh)
    #cv2.imshow('heatmap', heatmap)
    #cv2.waitKey()

def min_bounding_rect():
    pass

def check_foot_position(Rects):
    foot1 = []
    foot2 = []
    for r in Rects:
        x,y,w,h = cv2.boundingRect(r)
        if x < w/2:
            foot1.append([x,y])
            foot1.append([x+w,y+h])
        else:
            foot2.append([x,y])
            foot2.append([x+w,y+h])



def pose_evaluate():
    #判斷手在壓力墊上還是腳  -> 用數值去判定 -> 框出數值大於特定值
    #判斷兩腳在地或單腳
    #判斷是否雙手在壓力墊上
    pass

if __name__ == "__main__":
    print(ser)
    data = np.arange(6).reshape((3, 2))
    get_yoga_mat_data()
