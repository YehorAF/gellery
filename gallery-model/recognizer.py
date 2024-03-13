import cv2
import numpy as np
import tensorflow_hub as hub
from PIL import Image, ImageOps
import spacy


MODEL = "https://tfhub.dev/tensorflow/efficientdet/d0/1"
CLASS_INDEX = {
    1: 'person', 2: 'bicycle', 3: 'car',
    4: 'motorcycle', 5: 'airplane', 6: 'bus',
    7: 'train', 8: 'truck', 9: 'boat',
    10: 'traffic light', 11: 'fire hydrant', 13: 'stop sign',
    14: 'parking meter', 15: 'bench', 16: 'bird',
    17: 'cat', 18: 'dog', 19: 'horse',
    20: 'sheep', 21: 'cow',22: 'elephant',
    23: 'bear', 24: 'zebra', 25: 'giraffe',
    27: 'backpack', 28: 'umbrella', 31: 'handbag',
    32: 'tie', 33: 'suitcase', 34: 'frisbee',
    35: 'skis', 36: 'snowboard', 37: 'sports ball',
    38: 'kite', 39: 'baseball bat', 40: 'baseball glove',
    41: 'skateboard', 42: 'surfboard', 43: 'tennis racket',
    44: 'bottle', 46: 'wine glass', 47: 'cup',
    48: 'fork', 49: 'knife', 50: 'spoon',
    51: 'bowl', 52: 'banana', 53: 'apple',
    54: 'sandwich', 55: 'orange', 56: 'broccoli',
    57: 'carrot', 58: 'hot dog', 59: 'pizza',
    60: 'donut', 61: 'cake', 62: 'chair',
    63: 'couch', 64: 'potted plant', 65: 'bed',
    67: 'dining table', 70: 'toilet', 72: 'tv',
    73: 'laptop', 74: 'mouse', 75: 'remote',
    76: 'keyboard', 77: 'cell phone', 78: 'microwave',
    79: 'oven', 80: 'toaster', 81: 'sink',
    82: 'refrigerator', 84: 'book', 85: 'clock',
    86: 'vase', 87: 'scissors', 88: 'teddy bear',
    89: 'hair drier', 90: 'toothbrush'
}
R = np.array(np.arange(96, 256, 32))
G = np.roll(R, 1)
B = np.roll(R, 2)
COLOR_IDS = np.array(np.meshgrid(R, G, B)).T.reshape(-1, 3)


class Recognizer:
    def __init__(
        self, model_path = "https://tfhub.dev/tensorflow/efficientdet/d0/1"
    ) -> None:
        self._model = hub.load(model_path)


    def convert_image_to_png(
        self, path: str, new_path: str, width=512, height=512
    ) -> str:
        pil_image = Image.open(path)
        pil_image = ImageOps.fit(pil_image, (width, height), Image.LANCZOS)
        pil_image.save(new_path, format="PNG", quality=90)
    
        return new_path
    

    def load_image(self, path: str):
        image = cv2.imread(path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.expand_dims(image, axis=0)

        return image


    def detect_objects(self, image):
        results = self._model(image)
        results = {k:v.numpy() for k, v in results.items()}

        return image, results


    def idx_to_words(self, results, min_det_thresh = 0.3) -> list[str]:
        scores = results["detection_scores"][0]
        classes = (results["detection_classes"][0]).astype(int)
        det_indices = np.where(scores >= min_det_thresh)[0]
        classes_thresh = classes[det_indices]
        
        return [CLASS_INDEX[class_id] for class_id in classes_thresh]
    

recognizer = Recognizer()
nlp = spacy.load("en_core_web_sm")