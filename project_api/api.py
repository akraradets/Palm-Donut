from typing import Union

from fastapi import FastAPI, UploadFile, Depends, File, Form
from pydantic import BaseModel
from donut import calculate_donut_buffer_multi_thread, gen_buffer_dict
from histrogram import predict_health
from starlette.responses import FileResponse 
from fastapi.staticfiles import StaticFiles

from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

cookie_params = CookieParameters()

# Uses UUID
cookie = SessionCookie(
    cookie_name="cookie",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

import os

app = FastAPI()
# create public folder
public_path = "/root/public"
if(os.path.exists(public_path) == False):
    os.makedirs(public_path)
app.mount("/public", StaticFiles(directory=public_path), name="public")

@app.get("/")
async def get_index():
    response = FileResponse('ui/index.html')
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response

@app.get("/cookie")
def get_cookie():
    cookie = Cookie()
    return {"cookie": cookie}

class TestData(BaseModel):
    data: str

@app.post("/api/test")
def post_test(testdata:TestData):
    return testdata

class Base(BaseModel):
    buffer_distance: float = Form(...)
    ndvi: UploadFile = File(...)
    shape: UploadFile = File(...)

@app.post("/submit")
def submit(base: Base = Depends()):
    import os
    output_path = "/root/data/buffer"
    if(os.path.exists(output_path) == False): 
        os.makedirs(output_path)

    buffer_distance = float(base.buffer_distance)
    ndvi_path = save_file(base.ndvi)
    
    zip_path = save_file(base.shape)
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall('/root/upload')
    from glob import glob
    zip_name = os.path.splitext(base.shape.filename)[0]
    shape_path = glob(pathname=f"/root/upload/{zip_name}/*.shp")[0]
    buffer_dict = gen_buffer_dict(buffer=buffer_distance)

    calculate_donut_buffer_multi_thread(buffer_dict=buffer_dict, shape_path=shape_path, ndvi_path=ndvi_path,
                                        output_path=output_path)
    model_path = "/root/model/RandomForestClassifier"
    result_filename = predict_health(buffer=buffer_distance, shape_path=shape_path, model_path=model_path)
    # return FileResponse(result_filename)
    return {
        "result_csv": result_filename
        # "JSON Payload ": base.model_dump_json(),
        # "Filenames": [file.filename for file in files],
    }

def save_file(upload_file):
    import os
    upload_path:str = "/root/upload"
    if(os.path.exists(upload_path) == False):
        os.makedirs(upload_path)
    
    path = os.path.join(upload_path, upload_file.filename)
    with open(path, "wb+") as f:
        f.write(upload_file.file.read())
    return path



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
