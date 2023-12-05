import geopandas as gpd
from glob import glob
import pandas as pd
import rasterio
import numpy as np
import pickle
from sklearn.base import ClassifierMixin

import os 

def load_model(model_path:str) -> ClassifierMixin:
    model:ClassifierMixin
    with open(model_path, 'rb') as handle:
        model = pickle.load(handle)
    return model

def get_histogram(path:str) -> list[float]:
    src = rasterio.open(path)
    arr = src.read()
    arr = np.array(arr)
    arr.flatten()
    arr = arr[(arr > -3.4028235e+38)]
    arr = arr[(arr > arr.min())]
    total = len(arr)

    hists = []

    hists.append(arr[(arr < 0)])
    hists.append(arr[(arr >= 0) & (arr <= 0.1)])
    hists.append(arr[(arr > 0.1) & (arr <= 0.2)])
    hists.append(arr[(arr > 0.2) & (arr <= 0.3)])
    hists.append(arr[(arr > 0.3) & (arr <= 0.4)])
    hists.append(arr[(arr > 0.4) & (arr <= 0.5)])
    hists.append(arr[(arr > 0.5) & (arr <= 0.6)])
    hists.append(arr[(arr > 0.6) & (arr <= 0.7)])
    hists.append(arr[(arr > 0.7) & (arr <= 0.8)])
    hists.append(arr[(arr > 0.8) & (arr <= 0.9)])
    hists.append(arr[(arr > 0.9)])

    for idx, hist in enumerate(hists):
        hists[idx] = round( 100*len(hist)/total , 2)

    return hists

def gen_buffer_dict(buffer:float) -> dict:
    import warnings
    lower_threshold = 3
    upper_threshold = 8
    upper_limit = 10
    if(buffer <= lower_threshold):
        raise ValueError(f"Buffer can not be less than {lower_threshold}. {buffer=}")
    elif(buffer > upper_threshold):
        raise ValueError(f"Buffer should not be grater or equal than {upper_threshold}. {buffer=}")

    buffer_dict = {
        "circle_s": 2,
        "circle_m": buffer - 2,
        "circle_l": buffer,
        "donut_o": (buffer, buffer - 2),
        "donut_i": (buffer - 2, 2),
    }
    return buffer_dict

def get_X(index:str, buffer_names:list, buffer_path:str) -> pd.DataFrame:
    hists = []
    columns = []
    temp_names = ['mi', '00', '01', 
                '02', '03', '04', 
                '05', '06', '07', 
                '08', '09']
    
    for buffer_name in buffer_names:
        filename = f"{index}_{buffer_name}.tiff"
        path = os.path.join(buffer_path,filename)
        if(os.path.exists(path) == False):
            raise FileExistsError(f"filename={path} not exist.")
        # print(filename)
        for temp_name in temp_names:
            columns.append(f"{buffer_name}_{temp_name}")
        hists.extend(get_histogram(path))
    
    X = pd.DataFrame(columns=columns,data=np.array(hists).reshape(1,-1))
    return X


def predict_health(buffer:float, shape_path:str, model_path:str, buffer_path:str, output_path:str) -> str:
    buffer_dict = gen_buffer_dict(buffer=buffer)
    geo_shape = gpd.read_file(shape_path)
    geo_shape['health'] = '0'
    geo_shape['x'] = 0.0
    geo_shape['y'] = 0.0
    if('MainID' in geo_shape.keys()):
        geo_shape.set_index('MainID',inplace=True)
    model = load_model(model_path=model_path)

    for index, geo in geo_shape.iterrows():
        buffer_name = list(buffer_dict.items())[0][0]
        X = get_X(index=index, buffer_names=buffer_dict.keys(), buffer_path=buffer_path)
        # Healthy 0
        # Unhealthy 1
        predict = model.predict(X[model.feature_names_in_])
        health = 'Healthy' if predict == 0 else 'Unhealthy'
        geo_shape.loc[index, 'health'] = health
        geo_shape.loc[index, 'x'] = geo.geometry.x
        geo_shape.loc[index, 'y'] = geo.geometry.y

    result_path = os.path.join(output_path,'result.csv')
    if(os.path.exists(output_path) == False):
        os.makedirs(output_path)
    geo_shape.to_csv(result_path)
    return result_path


if __name__ == "__main__":
    buffer = 5.5
    shape_path = "/root/data/SHP/CR11_status.shp"
    model_path = "/root/model/RandomForestClassifier"
    predict_health(buffer=buffer, shape_path=shape_path, model_path=model_path)
    
    
