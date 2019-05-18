import cv2
import itertools, os, time
import numpy as np
from Model import get_Model
from parameter import letters
import argparse
from keras import backend as K
K.set_learning_phase(0)

Region = {"A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F ",
          "G": "G", "H": "H", "I": "I", "J": "J", "K": "K", "L": "L",
          "M": "M", "N": "N", "O": "O", "P": "P"}
hangul = {}

def decode_label(out):
    # out : (1, 32, 42)
    out_best = list(np.argmax(out[0, 2:], axis=1))  # get max index -> len = 32
    out_best = [k for k, g in itertools.groupby(out_best)]  # remove overlap value
    outstr = ''
    for i in out_best:
        if i < len(letters):
            outstr += letters[i]
    return outstr


def label_to_hangul(label):  # eng -> hangul
    region = label[0]
    two_num = label[1:3]
    hangul = label[3:5]
    four_num = label[5:]

    try:
        region = Region[region] if region != 'Z' else ''
    except:
        pass
    try:
        hangul = Hangul[hangul]
    except:
        pass
    return region + two_num + hangul + four_num

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--weight", help="weight file directory",
                    type=str, default="Final_weight.hdf5")
parser.add_argument("-t", "--test_img", help="Test image directory",
                    type=str, default="./DB/test/")
args = parser.parse_args()

# Get CRNN model
model = get_Model(training=False)

try:
    model.load_weights(args.weight)
    print("...Previous weight data...")
except:
    raise Exception("No weight file!")


test_dir =args.test_img
test_imgs = os.listdir(args.test_img)
total = 0
acc = 0
letter_total = 0
letter_acc = 0
start = time.time()
for test_img in test_imgs:
    img = cv2.imread(test_dir + test_img, cv2.IMREAD_GRAYSCALE)

    img_pred = img.astype(np.float32)
    img_pred = cv2.resize(img_pred, (128, 64))
    img_pred = (img_pred / 255.0) * 2.0 - 1.0
    img_pred = img_pred.T
    img_pred = np.expand_dims(img_pred, axis=-1)
    img_pred = np.expand_dims(img_pred, axis=0)

    net_out_value = model.predict(img_pred)

    pred_texts = decode_label(net_out_value)

    for i in range(min(len(pred_texts), len(test_img[0:-4]))):
        if pred_texts[i] == test_img[i]:
            letter_acc += 1
    letter_total += max(len(pred_texts), len(test_img[0:-4]))

    if pred_texts == test_img[0:-4]:
        acc += 1
    total += 1
    print('Predicted: %s  /  True: %s' % (label_to_hangul(pred_texts), label_to_hangul(test_img[0:-4])))
    
    # cv2.rectangle(img, (0,0), (150, 30), (0,0,0), -1)
    # cv2.putText(img, pred_texts, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255),2)

    #cv2.imshow("q", img)
    #if cv2.waitKey(0) == 27:
    #   break
    #cv2.destroyAllWindows()

end = time.time()
total_time = (end - start)
print("Time : ",total_time / total)
print("ACC : ", acc / total)
print("letter ACC : ", letter_acc / letter_total)
