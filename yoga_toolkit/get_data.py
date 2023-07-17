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
    

if __name__ == "__main__":
    print(ser)
    data = np.arange(6).reshape((3, 2))
    get_yoga_mat_data()
