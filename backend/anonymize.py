import os
import pickle
import uuid
from copyreg import pickle
from functools import partial
from pathlib import Path

import cv2
import numpy as np
import openvino.runtime as ov
from cachetools import LRUCache, cachedmethod
from cachetools.keys import hashkey

import backend.utils as utils


class Anonymizer:

    def __init__(self, use_cache=True) -> None:

        self.use_cache = use_cache
        if self.use_cache:
            if os.path.exists('backend/cache/cache.pkl'):
                with open('backend/cache/cache.pkl', 'rb') as cache:
                    self.cache = pickle.load(cache)
            else:
                self.cache = LRUCache(maxsize=100)

        self.ov_core = ov.Core()
        self.model = self.ov_core.compile_model(Path('backend/models/anonymizer/1/anonymizer').with_suffix(".xml").as_posix(), 'CPU')
        self.infer_request = self.model.create_infer_request()

    @cachedmethod(lambda self: self.cache, key=partial(lambda  id, _, *args, **kwargs: hashkey(id, *args, **kwargs), '_anonymize'))
    def _anonymize(self, data):

        img_np = np.frombuffer(data, np.uint8)
        img0 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        img = utils.letterbox(img0, (640, 640), auto=False)[0]

        # Convert
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)
        img = img.astype(np.float32)

        img /= 255
        if len(img) == 3:
            img = img[None]

        b, ch, h, w = img.shape

        self.infer_request.infer(img)
        pred = self.infer_request.get_output_tensor(0).data[0]
        pred = pred[np.newaxis, ...]

        pred = utils.non_max_suppression(pred, conf_thres=.25, iou_thres=.45, max_det=1000)

        pred[0][:, :4] = utils.scale_coords(img.shape[2:], pred[0][:, :4], img0.shape).round()

        frame = np.float64(img0)
        for result in pred[0]:

            box = result[:4].astype(int)
            crop = frame[box[1]:box[3],box[0]:box[2]]
            blur_size = int(crop.shape[1] * .2)
            blur_size = blur_size + 1 if blur_size % 2 == 0 else blur_size

            if result[-1] == 0:
                
                crop = cv2.GaussianBlur(crop, (blur_size, blur_size), 0)
                frame[box[1]:box[3],box[0]:box[2]] = crop
            else:
                center = (crop.shape[1] // 2, crop.shape[0] // 2)
                axes = ((box[2] - box[0]) // 2, (box[3] - box[1]) // 2)  
                mask = np.zeros(crop.shape, dtype='uint8')
                cv2.ellipse(mask, center, axes, 0, 0, 360, color=(255, 255, 255), thickness=-1)
                blur = cv2.GaussianBlur(crop, (blur_size, blur_size), 0)
                crop = np.where(mask > 0, blur, crop)
                frame[box[1]:box[3],box[0]:box[2]] = crop

        id = uuid.uuid4().hex
        cv2.imwrite(f'backend/results/{id}.jpg', frame)
        return f'{id}'

    def anonymize(self, data):

        if self.use_cache:
            return self._anonymize(data)
        else:
            return self._anonymize.__wrapped__(self, data)

    def save_cache(self):

        if self.use_cache:
            with open('backend/cache/cache.pkl', 'wb') as cache:
                pickle.dump(self.cache, cache)
