from http.client import responses
from unittest import result
from fastapi import FastAPI, UploadFile, Request, Body, File, Form, Depends
import fastapi.responses as responses
import uvicorn
from typing import List
from ast import For, literal_eval
from fastapi.staticfiles import StaticFiles
from backend.anonymize import Anonymizer 
from glob import glob


class UploadInfo:

    def __init__(
        self,
        initialPreview: str = Form(),
        initialPreviewConfig: str = Form(),
        initialPreviewThumbTags: str = Form(),
        fileId: str = Form(''),

    ) -> None:
        self.initialPreview = literal_eval(initialPreview)
        try:
            initialPreviewConfig = literal_eval(initialPreviewConfig)
        except Exception as e:
            pass
        self.initialPreviewConfig = initialPreviewConfig
        self.initialPreviewThumbTags = literal_eval(initialPreviewThumbTags)
        self.fileId = fileId

app = FastAPI()
# app.mount("/img", StaticFiles(directory=r"C:\Users\trpakov\Desktop"), name="assets")
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")


@app.on_event("startup")
async def init():
    global anonymizer
    anonymizer  = Anonymizer(use_cache=True)


@app.on_event("shutdown")
async def shutdown():
    anonymizer.save_cache()


@app.get('/')
def root():
    return responses.FileResponse('frontend/index.html')

@app.get('/2')
def root():
    return responses.FileResponse('frontend/index2.html')


@app.post('/anonymize')
async def anonymize(req: Request, file_data: UploadFile, file_info: UploadInfo = Depends()): # a = Body()

    data = await file_data.read()
    result_id = anonymizer.anonymize(data)

    response = {}
    response['initialPreview'] = [f"<img src='/img?key={result_id}' class='file-preview-image' alt='{file_data.filename}' title='{file_data.filename}'>"]
    response['initialPreviewConfig'] = [{"previewAsData": False, "caption": file_data.filename, "key": result_id, "size": len(data)}]
    return response


@app.get("/img")
async def get_img(key: str):
    
    path = glob(f'backend/results/{key}.*')

    if len(path) == 1:
        return responses.FileResponse(path[0])
    else:
        raise responses.HTTPException(status_code=404, detail="Image not found")

@app.post("/img")
async def del_img():

    return {}

# @app.get("/{id}")
# async def get_img(id: str):
    
#     path = glob(f'backend/results/{id}.*')

#     if len(path) == 1:
#         return responses.FileResponse(path[0])
#     else:
#         raise responses.HTTPException(status_code=404, detail="Image not found")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=9999)