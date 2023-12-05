from django.http import HttpResponse
from django.shortcuts import render, redirect

from glob import glob
import os 
import shutil


def index(request, error:str=""):
    # Check session 
    session_key = _session(request)
    print(session_key)
    # Init storage
    _init_storage(session_key)
    
    base = _get_storage_path(request=request)
    ndvi_filename = glob(f"{base}/ndvi/*")
    if(len(ndvi_filename) > 0):
        ndvi_filename = os.path.split(ndvi_filename[0])[1]
    else:
        ndvi_filename = ""

    shape_filename = glob(f"{base}/shape/*.zip")
    if(len(shape_filename) > 0):
        shape_filename = os.path.split(shape_filename[0])[1]
    else:
        shape_filename = ""

    output_filename = glob(f"{base}/output/*.csv")
    if(len(output_filename) > 0):
        output_filename = os.path.split(output_filename[0])[1]
    else:
        output_filename = ""

    return render(request=request, 
                template_name="index.html", 
                context={
                    "ndvi_filename":ndvi_filename,
                    "shape_filename":shape_filename,
                    "output_filename":output_filename,
                    "error":error
                    }
                )

def download_output(request):
    import mimetypes
    base = _get_storage_path(request=request)
    output_filename = glob(f"{base}/output/*.csv")
    if(len(output_filename) > 0):
        output_filename = output_filename[0]
    else:
        return index(request=request, error="output file not found.")

    fl = open(output_filename, 'r')
    mime_type, _ = mimetypes.guess_type(output_filename)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % os.path.split(output_filename)[1]
    return response


def upload_ndvi(request):
    ndvi_file = request.FILES["ndvi"]
    base = _get_storage_path(request=request)
    base = os.path.join(base,"ndvi")

    if(os.path.exists(base)):
        shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)

    path = os.path.join(base, ndvi_file.name)
    with open(path, "wb+") as destination:
        for chunk in ndvi_file.chunks():
            destination.write(chunk)
    return redirect('index')

def upload_shape(request):
    ndvi_file = request.FILES["shape"]
    base = _get_storage_path(request=request)
    base = os.path.join(base,"shape")

    if(os.path.exists(base)):
        shutil.rmtree(base, ignore_errors=True)
    os.makedirs(base)

    path = os.path.join(base, ndvi_file.name)
    with open(path, "wb+") as destination:
        for chunk in ndvi_file.chunks():
            destination.write(chunk)
    return redirect('index')

def calculate_donut(request):
    base = _get_storage_path(request=request)
    try:
        ndvi_file = _get_file_path(request=request, folder='ndvi')
    except:
        return index(request=request, error="Missing NDVI image")

    try:
        shape_file_zip = _get_file_path(request=request, folder='shape')
    except:
        return index(request=request, error="Missing shape file")
    
    # Code from api
    # print(request.POST)
    try:
        buffer_distance:float = float(request.POST['buffer-distance'])
        shape_file = _extract_zip(shape_file_zip, os.path.join(base, "shape"))
        buffer_path = os.path.join(base, "buffer")
        output_path = os.path.join(base, "output")
        result_path = _work(buffer_distance=buffer_distance, 
              shape_path=shape_file, 
              ndvi_path=ndvi_file, 
              buffer_path=buffer_path, 
              output_path=output_path)
    except Exception as e:
        return index(request=request, error=str(e))

    return redirect("index")

def _work(buffer_distance:float, shape_path:str, ndvi_path:str, buffer_path:str, output_path:str) -> str:
    from .processing.donut import gen_buffer_dict, calculate_donut_buffer_multi_thread
    from .processing.histrogram import predict_health
    buffer_dict = gen_buffer_dict(buffer=buffer_distance)

    calculate_donut_buffer_multi_thread(buffer_dict=buffer_dict, 
                                        shape_path=shape_path, 
                                        ndvi_path=ndvi_path,
                                        output_path=buffer_path)
    model_path = "form/processing/model/RandomForestClassifier"
    result_path = predict_health(buffer=buffer_distance, 
                                     shape_path=shape_path, 
                                     model_path=model_path, 
                                     buffer_path=buffer_path,
                                     output_path=output_path)
    return result_path
    # return FileResponse(result_filename)

def _extract_zip(zip_path, destination) -> str:
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(destination)
    from glob import glob
    zip_name = os.path.splitext(os.path.split(zip_path)[1])[0]
    target = os.path.join(destination, zip_name)
    shape_file = glob(pathname=f"{target}/*.shp")[0]
    return shape_file



def _get_file_path(request, folder:str) -> str:
    base = _get_storage_path(request=request)
    if(folder == "ndvi"):
        filename = glob(f"{base}/{folder}/*")[0]
    elif(folder == "shape"):
        filename = glob(f"{base}/{folder}/*.zip")[0]
    else:
        raise ValueError(f"{folder=} is not expected.")
    return filename
    

def _get_storage_path(request) -> str:
    return os.path.join("/root","storage",request.session.session_key)

def _session(request) -> str:
    if('sessionid' not in request.COOKIES.keys()):
        print("Empty session. Create new one.")
        request.session.cycle_key()
    return request.session.session_key

def _init_storage(folder_name):
    path = os.path.join("/root","storage",folder_name)
    if(os.path.exists(path) == False):
        print(f"create folder {path=}")
        os.makedirs(path)