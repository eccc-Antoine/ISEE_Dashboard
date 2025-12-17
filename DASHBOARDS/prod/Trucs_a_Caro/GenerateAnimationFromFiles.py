import os,sys
import numpy as np
import configparser
from optparse import OptionParser
import datetime as dt
import multiprocessing as mp

import xarray as xr
import matplotlib.pyplot as plt
import imageio.v3 as iio
import numpy as np
from scipy.spatial import cKDTree
import pandas as pd
from glob import glob
from dask.diagnostics import ProgressBar
from parse import parse
from tqdm import tqdm
from pyproj import Transformer
import geopandas as gpd
import matplotlib.dates as mdates
import logging
from utils.CSHOREReadInputs import ReadForcing as CSHOREF
from utils.CSHORETileProcess_15MAR2024 import CSHORETileProcess as CSHORET
# xr.set_options(file_cache_maxsize=128)

TILEID=346
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
def unwrap_netcdf(*arg,**kwarg):
    return GenerateAnimationFromFiles._ncReader(*arg,**kwarg)



def reshape_all_times(data, mask, m, n, dummy):
    """Vectorized reshaping for all time steps"""
    result = np.tile(dummy[np.newaxis, :], (data.shape[0], 1))
    
    for i in range(data.shape[0]):
        result[i, mask] = data[i].ravel()
    result = result.reshape((data.shape[0],m,n))
    return result


class GenerateAnimationFromFiles:
    def __init__(self,options):
        self.logger = self._createLoggingFile()
        self._readConfigFile(options.config)
        self.tile = tile = CSHORET(options.config,TILEID,logger=None)
        tile.gridc
        
        self.grid = grid = tile.grid.set_index('id')
        _shape = tile.shapeDEM 
        trans = Transformer.from_crs(4326,tile.epsg)
        xin,yin = trans.transform(self._ext[2:],self._ext[:2])
        grid2d = np.unique(grid.x.values)
        self.i_in = np.where(((grid2d>xin[0]) & (grid2d<xin[1])))[0]
        grid2d = np.unique(grid.y.values)

        self.j_in = np.where(((grid2d>yin[0]) & (grid2d<yin[1])))[0]
        self.out_mask,self.out_mask_indx = tile.out_mask

               
        self.dummy = grid['z'].values.reshape(_shape) 
        selected_dates = pd.date_range(start=dt.datetime(1960,1,1),end=dt.datetime(2020,1,1),freq='3h')
        self.forcings = CSHOREF(config=options.config,
                                            logger=self.logger,
                                            selected_dates=selected_dates,
                                            resample_ts=True,
                                            ts_base=self._tsQMID) 
        df_winds = self.forcings.winds.copy()
        rad = np.deg2rad(270 - df_winds.mwdir.values)
        df_winds['u'] =  df_winds.mwspd * np.cos(rad)
        df_winds['v'] = df_winds.mwspd * np.sin(rad)
        self.winds = df_winds
        self._create()
               

    def _createLoggingFile(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        
        logger = logging.getLogger('Animation')
        logger.setLevel(logging.DEBUG)        
        logger.addHandler(stream_handler)
        return logger   
    
    def _readConfigFile(self,_config):
        parser = configparser.ConfigParser()
        parser.read(_config)       
        
        for section in ['INPUTS','OUTPUTS','DEEPWAVES','BUILDINGS']:
            if parser.has_section(section):            
                if section == 'INPUTS':
                    _inputsFolder = parser.get(section,'folder')
                    _template = parser.get(section,'template')
                    _getNameFrom = parser.get(section,'get_name_from')        
                    self.info = [(f,parse(_template,os.path.basename(f))[_getNameFrom]) for 
                                            f in glob(os.path.join(_inputsFolder,_template.format(PLAN='*')))
                                            if not parse(_template,os.path.basename(f)) is None]
                    
                    if parser.has_option(section,'time_series'):
                        self.ts_base = (pd.read_csv(parser.get(section,'time_series'),sep=',')
                                                [['QM_ID','YEAR_QM','YEAR','date']]                                        
                                                .rename(columns={'YEAR_QM':'QM','date':'DATE'})
                                                .set_index(['DATE']))  
                        self.ts_base.index = pd.to_datetime(self.ts_base.index)                      
                        self._tsQMID = (self.ts_base.copy()
                                                .drop_duplicates(keep='last')  
                                                .reset_index())
                        self._tsQMID['DATE']= pd.to_datetime(self._tsQMID['DATE'].dt.strftime('%Y-%m-%d'))
                        print(f'time series loaded:\n{self._tsQMID}')  
                    dates = parser.get(section,'dates').split(',')
                    try:
                        dt.datetime.strptime(dates[0],'%Y%m%d%H')
                        dt.datetime.strptime(dates[1],'%Y%m%d%H')
                    except:
                        raise ValueError(f'Config: dates given in the [INPUTS] should must be in YYYYMMDDHH format.')
                    _dates = [dt.datetime.strptime(date,'%Y%m%d%H') for date in dates]
                    self._timeStep = parser.get(section,'time_step')
                    self.selected_dates = pd.date_range(start=_dates[0],end=_dates[-1],freq=self._timeStep)                        
    
                elif section == 'DEEPWAVES':
                    self._wavesSeries = parser.get(section,'series')                    
                    self._wavesTemplate = parser.get(section,'template')
                    self._wavesGrid = parser.get(section,'grid')
                    self._wavePts = dict([item.split(',') for item in parser.get(section,'point').split(';')])
                    self._readWaveConditions()
                    
                elif section == 'BUILDINGS':
                    self._geoj = gpd.read_file(parser.get(section,'geoj')).to_crs(4326)
                    
                elif section == 'OUTPUTS':
                    self._outFolder = parser.get(section,'folder')
                    os.makedirs(self._outFolder,exist_ok=True)
                    self._outTemplate = parser.get(section,'template')
                    self._ext = list(np.array(parser.get(section,'extent').split(','),float))
                    
                    
                    
    def _ncReader(self,info):
        sys.stdout.write(f'\r{info[0]}')
        (_file,_year) = info
        _nc = self._nc.replace('WAVES',f'WAVES_{_year}')
        if not os.path.exists(_nc):
            indx = self.indx
            ds = xr.open_dataset(_file,chunks='auto')#,chunks={'time':-1,'lat':1,'lon':1})  
            ds = ds[['hs']].isel(lat=self.ilat,lon=self.ilon).stack(pts=('lat','lon')).drop(['lat','lon'])
            ds['pts'] = indx
            with ProgressBar():
                ds = ds.compute()
            ds.to_netcdf(_nc)
        else:
            ds = xr.open_dataset(_nc)                      
        return ds            
    
    
    def _readWaveConditions(self):
        # waves grid
        waves = xr.open_dataset(self._wavesGrid).isel(time=0).squeeze()
        lat,lon = waves['latitude'].values,waves['longitude'].values        
        tree = cKDTree(np.c_[lat.ravel(),lon.ravel()])
        
        pts = pd.DataFrame(self._wavePts,index=[0]).astype('float')
        _,indx = tree.query(pts[['lat','lon']].values,k=1)        
        self.ilat,self.ilon = np.unravel_index(np.unique(indx.ravel()),lat.shape)

        self.indx = indx
        print(f'     -> PROCESS waves')
        _wavesTemplate = self._wavesTemplate
        _wavesFolder = self._wavesSeries
        info = [(f,parse(_wavesTemplate,os.path.basename(f))['YEAR']) 
                                for f in glob(os.path.join(_wavesFolder,'*.nc'))
                                if not parse(_wavesTemplate,os.path.basename(f)) is None]
                    
        self._nc = _nc = os.path.join(self._outFolder,self._outTemplate.format(TILE=TILEID,TYPE='WAVES.nc'))
        
        if not os.path.exists(_nc):
            with mp.Pool(30) as pool:     
                lst_nc = pool.starmap(unwrap_netcdf, zip([self]*len(info),info))
            self.waves = xr.concat(lst_nc,dim='time').sortby('time').chunk({'time':-1}) 
            self.waves.to_netcdf(_nc)
        else: self.waves = xr.open_dataset(_nc)
                
    
    
    def _create(self):
        info = self.info
        winds = self.winds.set_index('DATE')
        waves = self.waves.to_dataframe()
        wl = self.forcings.glrrm
        wli = self.forcings.isee

        grid2d = self.tile.dem
        trans = Transformer.from_crs(self.tile.epsg,4326)
        grid2d['lat'],grid2d['lon'] = trans.transform(grid2d.x.values,grid2d.y.values)
        _shape = self.dummy.shape
        
        lats = grid2d.lat.values.reshape(_shape)
        lons = grid2d.lon.values.reshape(_shape)

        import contextily as cx
        import matplotlib.gridspec as gridspec
        import datetime as dt
        from moviepy.editor import ImageSequenceClip
        from moviepy.video.io.bindings import mplfig_to_npimage
        from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
        from matplotlib.animation import FFMpegWriter
        import pickle

        lon_min,lon_max,lat_min,lat_max = self._ext
        _pkl = os.path.join(self._outFolder,self._outTemplate.format(TILE=TILEID,TYPE='DATA.pkl'))
        if not os.path.exists(_pkl):
            data={}
            dummy=None
            indx=None
            for _file,_name in info:            
                dat = xr.open_dataset(_file)
                lse = dat['mlse'].data
                if indx is None: a=1
                    
                time = dat['time'].data
                nt,_ = lse.shape
                if dummy is None:
                    z = np.tile(self.dummy[np.newaxis, :, :], (lse.shape[0],1, 1))
                    dummy = z.copy() + np.nan
                    nt,nx,ny = dummy.shape                
                dummy_ = dummy.copy().reshape((nt,nx*ny))
                dummy_[:,self.out_mask_indx] = lse            
                dummy_ = dummy_.reshape((nt,nx,ny))
                dummy_ = dummy_ - z
                dummy_[dummy_<0] = np.nan    
                data[_name] = dummy_
            with open(_pkl,'wb') as fid:
                pickle.dump([time,data],fid)
        else:
            with open(_pkl,'rb') as fid:
                time,data = pickle.load(fid)

        frames = []
        plans = list(data.keys())
        
        metadata = dict(title='Example Video', artist='Matplotlib', comment='pcolormesh animation')
        writer = FFMpegWriter(fps=2, metadata=metadata)
        
        plt.rcParams["figure.autolayout"] = False
        
        # vmin,vmax = np.min(values),np.max(values)
        fig = plt.figure(figsize=(16,8),frameon=False,dpi=300)
        fig.set_layout_engine(None)
        fig.subplots_adjust(left=0.05, bottom=0.05, right=1, top=1)
        ax1 = fig.add_subplot(1,2,1)  
        ax2 = fig.add_subplot(1,2,2)         

        im1 = ax1.pcolormesh(lons,lats,data[plans[0]][0,:,:].squeeze(), 
                            shading='auto',
                            alpha=1,
                            zorder=100,
                            vmin=0.01,
                            vmax=2,
                            cmap='RdYlBu_r',
                            rasterized=True,
                            linewidth=0,
                            edgecolors='none',
                            antialiased=False)
        im1.set_edgecolor('face')
        cbar = fig.colorbar(im1, ax=ax1, shrink=0.8,orientation='horizontal',pad=0.02, fraction=0.046)
        cbar.set_label(r"Water Depth (m)", fontsize=12, labelpad=1)       
                    
        ax1.set_xticks([])
        ax1.set_yticks([])
        ax1.set_title(f'{plans[0]}')
        ax1.set_xlim(lon_min, lon_max)
        ax1.set_ylim(lat_min, lat_max)            
        cx.add_basemap(ax1, crs="EPSG:4326", source=cx.providers.Esri.WorldImagery,attribution=False)

        diff = data[plans[0]][0,:,:].squeeze() - data[plans[1]][0,:,:].squeeze()
        diff[np.abs(diff)<=0.001] = np.nan
        masked_diff = np.ma.masked_invalid(diff)*100        
        cmap = plt.get_cmap('RdBu_r',20).copy()
        # cmap.set_bad(color=(0,0,0,0))
        im2 = ax2.pcolormesh(lons,lats,masked_diff, 
                            alpha=1,
                            zorder=100,
                            vmin=-20,
                            vmax=20,
                            cmap=cmap,
                            rasterized=True,
                            linewidth=0,
                            edgecolors='none',
                            antialiased=False)
        im2.set_edgecolor('face')
        ax2.set_xticks([])
        ax2.set_yticks([])    
        ax2.set_xlim(lon_min, lon_max)
        ax2.set_ylim(lat_min, lat_max)              
        cx.add_basemap(ax2, crs="EPSG:4326", source=cx.providers.Esri.WorldImagery,attribution=False)        
        cbar = fig.colorbar(im2, ax=ax2, shrink=0.8,orientation='horizontal',pad=0.02, fraction=0.046)
        cbar.set_label(r"$\Delta$ Water Depth (mm)", fontsize=12, labelpad=1)    
        self._geoj.boundary.plot(ax=ax1, linewidth=1.0, edgecolor="white", zorder=500)
        self._geoj.boundary.plot(ax=ax2, linewidth=1.0, edgecolor="white", zorder=500)     

        dft = pd.DataFrame({'time':time})
        dft['time'] = pd.to_datetime(dft.time)
        _outFile = os.path.join(self._outFolder,self._outTemplate.format(TILE=TILEID,TYPE='VIDEO.mp4'))
        with writer.saving(fig, _outFile, dpi=300):        
            for it in tqdm(range(time.shape[0])):
                tt = dt.datetime.utcfromtimestamp(time[it].astype(int)*1e-9)
                w = winds.loc[tt]
                ww = waves.loc[tt]
                t = tt.strftime('%Y/%m/%d %H:%M')                  
                                                
                # colors=['b','g']
                # styles=['-','-.']
                # values=[]
                glrrm,isee={},{}
                for i,(_name,ts) in enumerate(wl.items()):                
                    indx = ts[ts.DATE==tt].index.values[0]                
                    # ax.plot(ts.set_index('DATE'),label=_name,color=colors[i],linestyle=styles[i],linewidth=2)                
                    # dates = ts.loc[indx-250:indx+250].DATE.values#.set_index('DATE')            
                    # ax.set_xlim([dates[0],dates[-1]])  
                    # values.extend([ts.loc[indx-250:indx+250].WATER_LEVEL.max(),ts.loc[indx-250:indx+250].WATER_LEVEL.min()]) 
                    glrrm[_name] = np.round(ts.loc[indx].WATER_LEVEL,2)
                    del ts
                    ts = wli[_name]
                    indx = ts[ts.DATE==tt].index.values[0]         
                    isee[_name] = np.round(ts.loc[indx].WATER_LEVEL,2)
                im1.set_array(data[plans[0]][it,:,:].squeeze().ravel())    
                ax1.set_title(f'{t}, {plans[0]} [GLRRM:{np.round(glrrm[plans[0]],2)}/ISEE:{np.round(isee[plans[0]],2)} m]')       
                
                d1,d2 = data[plans[0]][it,:,:].squeeze(),data[plans[1]][it,:,:].squeeze()
                d1[np.isnan(d1)] = 0
                d2[np.isnan(d2)] = 0
                diff = d1 - d2
                diff = np.round(diff*1000)
                diff[diff==0] = np.nan
                masked_diff = np.ma.masked_invalid(diff)
                im2.set_array(masked_diff)                                
                ax2.set_title(f'{plans[0]} - {plans[1]} [{int(np.round((glrrm[plans[0]]-glrrm[plans[1]])*100))} cm]')            
                at = ax1.text(0.7,0.92,
                            f'Winds [Hs: {np.round(ww.hs.values[0],1)} m]',
                            transform=ax1.transAxes,
                            color='white',
                            weight="bold",
                            zorder=500
                            )
                aq = ax1.quiver(0.7, 0.7, w.u, w.v, transform=ax1.transAxes,
                                    scale=60, color="white", zorder=600)  
                fig.canvas.draw()
                # fig.tight_layout(pad=0)
                for ax in (ax1, ax2):
                    for spine in ax.spines.values():
                        spine.set_visible(False)
                # plt.show()
                # exit(1)
                writer.grab_frame()
                aq.remove()
                at.remove()
       
    
    
    
    
    
    
if __name__ == "__main__":    
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    
    parser.add_option("-c", "--config",
                      dest="config",
                      metavar="FILE",
                      help="configuration file")     
    
     

        
    (options, args) = parser.parse_args() 
    print(options)
    GenerateAnimationFromFiles(options)    
    