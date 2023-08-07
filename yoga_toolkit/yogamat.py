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
            # diffuse 
            dir = [[0,1],[1,0],[-1,0],[0,-1]]
            for (x, y), value in np.ndenumerate(a):
                if value> 100:
                    for addx,addy in dir:
                        if x+addx>=0 and x+addx<12 and y+addy>=0 and y+addy<18 and a[x+addx][y+addy]<60:
                            a[x+addx][y+addy]=a[x+addx][y+addy]+value/4

            a = (a > 60) * a
            return a
            

def find_center(heatmap_arr):
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
        return np.array([(output_x/acum_w*enlarge)+25,(output_y/acum_w*enlarge)+25]).astype(int)
    else:
        return np.array([])
    
def get_heatmap():
    data = get_yoga_mat_data()
   
    rescaled_array = cv2.resize(data.astype('uint8'), dsize=(18 * enlarge , 12 * enlarge)) 
    rescaled_array = cv2.normalize(rescaled_array, None, 0, 255, norm_type= cv2.NORM_MINMAX, dtype= cv2.CV_8U)
    heatmap = cv2.applyColorMap(rescaled_array, cv2.COLORMAP_JET)
    center = find_center(data)
    rects = find_bounding_box(heatmap)
    print(herotwo_pose_evaluate(center ,rects))
    if len(center)!=0 :
        cv2.circle(heatmap, [center[1], center[0]], 10, (255, 255, 255), 1)
    if  len(rects)> 1:
        for rect in rects:
            x , y , w , h = rect
            cv2.rectangle(heatmap, (x, y), (x + w, y + h), (36,255,12), 2)
    heatmap = cv2.rotate(heatmap, cv2.ROTATE_180)
    return heatmap
        

def find_bounding_box(heatmap):
    #https://stackoverflow.com/questions/58419893/generating-bounding-boxes-from-heatmap-data
    # Grayscale then Otsu's threshold
    gray = cv2.cvtColor(heatmap, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Find contours
    kernel = np.ones((3,3), np.uint8)
    dilation = cv2.dilate(thresh, kernel, iterations = 1)
    cnts = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    rects = []
    for c in cnts:
        x,y,w,h =cv2.boundingRect(c)
        rects.append([x,y,w,h])
    return np.array(rects)

def herotwo_pose_evaluate(center ,rects):
    if len(rects) == 2 and abs( rects[0][2] - rects[1][2])>50:       
        if rects[0][2] > rects[1][2]:
            front_foot = rects[0]
            rear_foot = rects[1]
        else:
            front_foot = rects[1]
            rear_foot = rects[0]
        front2center = abs(front_foot[0]+(front_foot[3]/2)-center[1]) 
        rear2center = abs(rear_foot[0]+(rear_foot[3]/2)-center[1])
        if front2center<rear2center and abs(front2center-rear2center)<100:
            return True
    return False


if __name__ == "__main__":
    

    while True:
        heatmap = get_heatmap()
        cv2.imshow("heatmap",heatmap)
        if cv2.waitKey(1) == ord('q'):
                break
    cv2.destroyAllWindows()
