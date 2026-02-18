import numpy as np
import pandas as pd
import os
import xarray as xr
import geopandas as gpd

##TODO ca plante avec ecriture sur Windows besoin de le refaire mais on ecrivant directement sur AZure

def tile_year_to_region(tx, ty, year, ref_year):
    t_idx = year - ref_year

    x0 = X_MIN + tx * TILE_SIZE
    y0 = Y_MIN + ty * TILE_SIZE

    x_idx = int((x0 - X_MIN) / RES)
    y_idx = int((y0 - Y_MIN) / RES)

    return {
        "time": slice(t_idx, t_idx + 1),
        "y": slice(y_idx, y_idx + NY),
        "x": slice(x_idx, x_idx + NX),
    }

def rasterize_tile(df_tile, tile_x_coords, tile_y_coords, var_name):
    """
    Convert sparse points in a tile DataFrame to a dense 2D array.
    """
    NX, NY = len(tile_x_coords), len(tile_y_coords)
    arr = np.full((NY, NX), NODATA, dtype="float32")

    # Vectorized index calculation
    ix = ((df_tile['XVAL'].to_numpy() - tile_x_coords[0]) // RES).astype(int)
    iy = ((tile_y_coords[0] - df_tile['YVAL'].to_numpy()) // RES).astype(int)  # flip Y

    arr[iy, ix] = df_tile[var_name].to_numpy()
    return arr

def write_tile_year(ds_block, tile_zarr_path, encoding):
    """
    Write or append a year to a tile Zarr, safe for Windows.
    """
    temp_path = tile_zarr_path + "_tmp"

    if not os.path.exists(tile_zarr_path):
        # First year → write new Zarr safely
        ds_block.to_zarr(temp_path, mode="w", consolidated=False,encoding=encoding)
        # Replace folder atomically
        if os.path.exists(tile_zarr_path):
            os.rename(tile_zarr_path, tile_zarr_path + "_backup")
        os.rename(temp_path, tile_zarr_path)
    else:
        # Subsequent years → append along time
        ds_block.to_zarr(tile_zarr_path, mode="a", append_dim="time", consolidated=False)

dct_tile_sect = {'LKO': [491, 490, 489, 488, 487, 486, 485, 484, 483, 482, 481, 480, 479, 478, 477, 476, 475, 474, 473, 472, 471, 470, 469, 468, 467, 466, 465, 464, 463, 462, 461, 460, 459, 458, 457, 456, 455, 454, 453, 452, 451, 450, 449, 448, 447, 446, 445, 444, 443, 442, 441, 440, 439, 438, 437, 436, 435, 434, 433, 432, 431, 430, 429, 428, 427, 426, 425, 424, 423, 422, 421, 420, 419, 418, 417, 416, 415, 414, 413, 412, 411, 410, 409, 408, 407, 406, 405, 404, 403, 402, 401, 400, 399, 398, 397, 396, 395, 394, 393, 392, 391, 390, 389, 388, 387, 386, 385, 384, 383, 382, 381, 380, 379, 378, 377, 376, 375, 374, 373, 372, 371, 370, 369, 368, 367, 366, 365, 364, 363, 362, 361, 360, 359, 358, 357, 356, 355, 354, 353, 352, 351, 350, 349, 348, 347, 346, 345, 344, 343, 342, 341, 340, 339, 338, 337, 336, 335, 334, 332, 331, 330, 329, 328, 327, 326, 325, 324, 323, 322, 321, 320, 319, 318, 317, 316, 315, 314, 313, 312, 311, 310, 309, 308, 307, 306, 305, 304, 303, 302, 301, 300, 299, 298, 297, 296, 295, 294, 293, 292, 291, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280, 279, 278, 277, 276, 275, 274, 273, 272, 271, 270, 269, 268, 267, 266, 265, 264, 263, 262, 261, 260, 259, 258, 257, 256, 255, 254, 253, 252, 251, 250, 249, 248, 247, 246, 245, 244, 243, 242, 241, 240, 239, 238, 237, 236, 235, 234, 233, 232, 231, 230, 229, 228, 226, 225, 224, 223, 222, 221, 220, 219, 216, 215, 214, 213, 212, 211, 210, 209, 208, 204, 203, 202, 201],
                 'SLR_DS': [121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 84, 83, 82, 81, 79, 78, 74],
                'SLR_US': [166, 165, 164, 163, 162, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115],
                'USL_DS': [184, 182, 181, 180, 179, 178, 177, 176, 175, 174, 173, 172, 170, 169],
                'USL_US': [238, 237, 236, 228, 227, 226, 218, 217, 216, 207, 206, 205, 204, 200, 199, 198, 197, 196, 195, 194, 193, 192, 191, 190, 189, 188, 187, 186, 185, 184, 183, 182, 181, 180],
                 'LKO_CAN': [492, 491, 490, 489, 488, 487, 486, 485, 484, 483, 482, 481, 480, 479, 478, 477, 476, 475, 474, 473, 472, 471, 470, 469, 468, 467, 466, 465, 464, 463, 462, 461, 460, 459, 458, 457, 456, 455, 454, 453, 452, 451, 450, 449, 448, 447, 446, 445, 444, 443, 440, 439, 438, 437, 436, 435, 434, 433, 429, 428, 427, 426, 425, 421, 420, 419, 418, 417, 413, 412, 411, 410, 406, 405, 404, 403, 398, 397, 396, 395, 394, 390, 389, 388, 387, 386, 382, 381, 380, 379, 378, 374, 373, 372, 371, 370, 369, 365, 364, 363, 362, 361, 355, 354, 353, 352, 351, 350, 344, 343, 342, 341, 340, 339, 332, 331, 330, 329, 328, 327, 326, 325, 320, 319, 318, 317, 316, 315, 314, 313, 308, 307, 306, 305, 304, 303, 302, 301, 296, 295, 294, 293, 292, 291, 290, 289, 284, 283, 282, 281, 280, 279, 278, 277, 272, 271, 270, 269, 268, 267, 266, 261, 260, 259, 258, 257, 256, 255, 249, 248, 247, 246, 245, 238, 237, 236, 235, 228, 226],
'SLR_DS_CAN': [121, 120, 119, 118, 117, 116, 115, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100, 99, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87, 86, 84, 83, 82, 81, 79, 78, 74],
'SLR_US_CAN': [166, 165, 164, 163, 162, 159, 158, 157, 156, 155, 154, 153, 152, 151, 150, 149, 148, 147, 146, 145, 144, 143, 142, 141, 140, 139, 137, 136, 135, 134, 133, 132, 131, 130, 129, 128, 127, 126, 124, 123, 122, 121, 120, 119, 118, 117, 116, 115],
'USL_DS_CAN': [182, 181, 179, 178, 176, 175, 173, 172, 170],
'USL_US_CAN': [238, 237, 236, 228, 227, 226, 218, 217, 216, 207, 206, 205, 200, 199, 198, 196, 195, 194, 192, 191, 190, 188, 187, 185, 184, 182, 181],
 'LKO_US': [462, 453, 452, 451, 450, 449, 444, 443, 442, 441, 440, 439, 438, 433, 432, 431, 430, 425, 424, 423, 422, 417, 416, 415, 414, 410, 409, 408, 407, 403, 402, 401, 400, 399, 394, 393, 392, 391, 386, 385, 384, 383, 378, 377, 376, 375, 369, 368, 367, 366, 361, 360, 359, 358, 357, 356, 350, 349, 348, 347, 346, 345, 339, 338, 337, 336, 335, 334, 325, 324, 323, 322, 321, 313, 312, 311, 310, 309, 301, 300, 299, 298, 297, 289, 288, 287, 286, 285, 277, 276, 275, 274, 273, 267, 266, 265, 264, 263, 262, 257, 256, 255, 254, 253, 252, 251, 250, 247, 246, 245, 244, 243, 242, 241, 240, 239, 236, 235, 234, 233, 232, 231, 230, 229, 226, 225, 224, 223, 222, 221, 220, 219, 216, 215, 214, 213, 212, 211, 210, 209, 208, 204, 203, 202, 201],
'USL_DS_US': [184, 182, 181, 180, 179, 178, 177, 176, 175, 174, 172, 170, 169],
'USL_US_US': [227, 226, 217, 216, 206, 205, 204, 199, 198, 197, 195, 194, 193, 191, 190, 189, 188, 187, 186, 185, 184, 183, 181, 180]
}

sections=['LKO', 'SLR_DS',
                'SLR_US',
                'USL_DS',
                'USL_US', 'LKO_CAN']


ZARR_DIR=fr'F:\prod\dataset.zarr'
TILE_SIZE = 10000   # meters
RES = 10             # meters
#NX = NY = TILE_SIZE // RES   # 1000
NODATA = np.nan
tile_shp=gpd.read_file(fr"F:\DEM_GLAMM\DEM_CREATION_FINAL\GLAM_ISEE_TILES\Tuile_final_w_conversions.shp")
crs_dct={'17': 32617, '18':32618, '19':32619}

for s in sections:
    print(f'--> processing section {s}')
    tiles=dct_tile_sect[s]

    years=list(range(1961,2021))
    ref_year=years[0]



    for t in tiles:
        print(f'    --> processing tile {t}')
        df_grid = pd.read_feather(fr"T:\GLAM\Input_ISEE\prod\GRID\grd_v44_20250527\feather\{t}_regular_grid.feather")
        utm = tile_shp.loc[tile_shp['tile'] == int(t), 'UTM'].iloc[0]
        crs = crs_dct[str(utm)]
        df_grid = df_grid[['PT_ID', 'XVAL', 'YVAL']]
        df_grid['PT_ID'] = df_grid['PT_ID'].astype('int32')
        tile_x_coords = np.sort(df_grid['XVAL'].unique())
        tile_y_coords = np.sort(df_grid['YVAL'].unique())[::-1]

        tile_zarr_path = os.path.join(ZARR_DIR, f"tile_{t}")

        if os.path.exists(tile_zarr_path):
            print('zarr file for this tile already exists skipping...')
            continue


        for y in years:
            print(f'        --> processing year {y}')

            path = fr"T:\GLAM\Output_ISEE\results_off\DASHBOARD_RESULTS_NEW\WL_ISEE_2D\Bv7_2014_ComboC\{s}\{y}\WL_ISEE_2D_Bv7_2014_ComboC_{s}_{t}_{y}.feather"

            if not os.path.exists(path):
                print(f'results for tile {t} and year {y} dont exists, skipping')
                continue

            df= pd.read_feather(path)

            df=df.merge(df_grid, on='PT_ID', how='left', suffixes=('', ''))

            df['PT_ID']=df['PT_ID'].astype('int32')

            df= df.drop_duplicates(subset=['PT_ID', 'XVAL', 'YVAL'])

            vars_col=[x for x in list(df) if 'VAR' in x]
            data_vars = {}
            for var in vars_col:
                data_vars[var] = (("y", "x"), rasterize_tile(df, tile_x_coords, tile_y_coords, var))


            # Wrap as xarray Dataset
            ds_block = xr.Dataset(
                data_vars=data_vars,
                coords={
                    "x": tile_x_coords,
                    "y": tile_y_coords,
                    "time": [y]
                }
            )

            comp = None
            encoding = {var: {"chunks": (100, 100), "compressor": comp} for var in ds_block.data_vars.keys()}

            # Write / append to Zarr
            tile_zarr_path = os.path.join(ZARR_DIR, f"tile_{t}")

            write_tile_year(ds_block, tile_zarr_path, encoding)

quit()




print(vars_col)

x0=df_grid['XVAL'].min()
y0=df_grid['YVAL'].min()

print(len(df_grid['XVAL'].unique()))
print(len(df_grid['YVAL'].unique()))

ix = np.floor((df["XVAL"] - x0) / RES).astype("int32")
iy = np.floor((y0 + TILE_SIZE - df["YVAL"]) / RES).astype("int32")

ix = np.clip(ix, 0, NX - 1)
iy = np.clip(iy, 0, NY - 1)



print(ix, iy)

block = {
    v: np.full((NY, NX), NODATA, dtype="float32")
    for v in vars_col
}

for v in vars_col:
    block[v][iy, ix] = df[v].values

# xs = x0 + np.arange(NX) * RES
# ys = y0 + TILE_SIZE - np.arange(NY) * RES

ds_block = xr.Dataset(
    {
        k: (("YVAL", "XVAL"), v) for k, v in block.items()
    },
    coords={"XVAL": tile_x_coords, "YVAL": tile_x_coords}, attrs={"crs": f"EPSG:{crs}"}
).expand_dims(time=[year])

print(ds_block)

#region=tile_year_to_region(tx, ty, year, ref_year)

# ds_block.to_zarr(
#     "dataset.zarr/10m",
#     region=region

# Write / append to Zarr
ds_block.to_zarr(
    f"P:/GLAM/Dashboard/ISEE_Dash_portable/ISEE_POST_PROCESS_DATA_3/dataset.zarr/tile_{tile_id}",
    mode="a",
    append_dim="time",
    consolidated=True
)

quit()