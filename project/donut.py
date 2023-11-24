import geopandas as gpd
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt
import numpy as np
import copy

# from components.logger import init_logger
import os


def calculate_donut_buffer(buffer_item:tuple, ndvi_path:str, shape_path:str, 
                           output_path:str, output_filename_suffix:str="", thread_id:int=0) -> None:
    """Calculate donut buffer with given radius on geo_shape and ndvi_image.

    Parameters
    ----------
    buffer_item : (str, float) ort (str, tuple)
        Radius of the buffer. `str` will be used for naming the output file.
    ndvi_image : rasterio.DatasetReader
        The base of the input to calculate donut buffer.
    geo_shape : GeoDataFrame
        Where row is the center of the donut.
    output_path : str, PathLike object, FilePath
        Where the donut buffer output will be saved.
    output_filename_suffix : str (opt)
        By default, the suffix is "". 
        This help to create a unique output filename so it won't override the other one.
        The file will names f"{output_filename_suffix}{index}.tiff".

    """
    print(thread_id)
    # check path exit
    if(os.path.exists(output_path) == False):
        os.makedirs(output_path)
    
    geo_shape = gpd.read_file(shape_path)
    ndvi_image = rasterio.open(ndvi_path)

    buffer_name, buffer_distance = buffer_item

    # check intersection
    if geo_shape.total_bounds[0] > ndvi_image.transform[2] + ndvi_image.shape[1] * ndvi_image.transform[0] or \
    geo_shape.total_bounds[2] < ndvi_image.transform[2] or \
    geo_shape.total_bounds[1] > ndvi_image.transform[5] or \
    geo_shape.total_bounds[3] < ndvi_image.transform[5] + ndvi_image.shape[0] * ndvi_image.transform[4]:
        raise ValueError(f"The geo_shape and ndvi_image do not intersect.")

    for idx, geo in geo_shape.iterrows():
        index = geo['MainID'] if 'MainID' in geo.keys() else idx
        # Create buffer around point
        # buffer_string = ""
        if(isinstance(buffer_distance, tuple)):
            buffered = geo.geometry.buffer(buffer_distance[0]) - geo.geometry.buffer(buffer_distance[1])
            # buffer_string = f"{buffer_distance[0]}-{buffer_distance[1]}"
        else:
            buffered = geo.geometry.buffer(buffer_distance)
            # buffer_string = f"{buffer_distance}"

        # Mask image with buffer
        out_image, out_transform = mask(dataset=ndvi_image, shapes=[buffered], nodata=-999, crop=True)
        out_image = np.array(out_image, dtype=np.float32)

        # Get output window based on buffer
        out_window = rasterio.windows.from_bounds(*buffered.bounds, transform=out_transform) # type:ignore

        # Update metadata
        meta = copy.deepcopy(ndvi_image.meta)
        meta.update({
            'driver': 'GTiff',
            'height': out_image.shape[1],
            'width': out_image.shape[2],
            'transform': out_transform,
            'nodata': -999,
            'crs': ndvi_image.crs
        })

        # Write masked image  to GeoTIFF
        filename = f"{index}_{buffer_name}.tiff"
        if(output_filename_suffix != ""):
            filename = f"{output_filename_suffix}_{filename}"
        output_file = os.path.join(output_path, filename)
        with rasterio.open(output_file, 'w', **meta) as f:
            f.write(out_image, window=out_window)

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
        "donut_i": (buffer - 2, 2),
        "donut_o": (buffer, buffer - 2),
    }
    return buffer_dict

def calculate_donut_buffer_multi_thread(buffer_dict:dict, shape_path:str, ndvi_path:str, 
                                        output_path:str, output_filename_suffix:str="") -> None:
    import multiprocessing as mp
    if(os.path.exists(output_path) == False):
        os.makedirs(output_path)
    pool = mp.Pool(len(buffer_dict))

    try:
        results = [pool.apply_async( calculate_donut_buffer, 
                                    args=(buffer_item, ndvi_path, 
                                        shape_path, output_path, 
                                        output_filename_suffix, pid) ) 
                        for pid, buffer_item in enumerate(buffer_dict.items())]
        results = [result.get() for result in results]
    except Exception as e:
        raise e
    finally:
        pool.close()
        pool.join()

if __name__ == "__main__":
    shape_path = "/root/data/SHP/CR11_status.shp"
    ndvi_path = "/root/data/NDVI/FIELD_20200716_03_MULT_CR11_090_M04_index_ndvi_register.tiff"
    output_path = "/root/data/buffer/"
    buffer = 5.5
    buffer_dict = gen_buffer_dict(buffer=buffer)
    calculate_donut_buffer_multi_thread(buffer_dict=buffer_dict, shape_path=shape_path, ndvi_path=ndvi_path,
                                        output_path=output_path)