import os,sys
import configparser
from optparse import OptionParser
import seaborn as sns
import numpy as np
from optparse import OptionParser
from pyarrow import feather as pf
import configparser
import pandas as pd
import matplotlib.pylab as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import geopandas as gpd
from pyarrow import feather as pf
from glob import glob
from parse import parse
import logging
from pyproj import Transformer
from scipy.spatial import cKDTree
import plotly
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import math
import pickle
from tqdm import tqdm
import multiprocessing as mpl

def adjust_spines(ax, spines):
    for loc, spine in ax.spines.items():
        if loc in spines:
            spine.set_position(('outward', 10))  # outward by 10 points
        else:
            spine.set_color('none')  # don't draw spine

    # turn off ticks where there is no spine
    if 'left' in spines:
        ax.yaxis.set_ticks_position('left')
    elif 'right' in spines:
        ax.yaxis.set_ticks_position('right')
        ax.yaxis.set_label_position("right")
    else:
        # no yaxis ticks
        ax.yaxis.set_ticks([])

    if 'bottom' in spines:
        ax.xaxis.set_ticks_position('bottom')
    elif 'top' in spines:
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position("top")
    else:
        # no xaxis ticks
        ax.xaxis.set_ticks([])

def get_wnd_dir_scen(wnd_dir_deg):
    '''Get Wind Direction Scenario from direction in geographical degrees'''
    if wnd_dir_deg <= 11.25:
        return 'N'
    elif 11.25 < wnd_dir_deg <= 33.75:
        return 'NNE'
    elif 33.75 < wnd_dir_deg <= 56.25:
        return 'NE'
    elif 56.25 < wnd_dir_deg <= 78.75:
        return 'ENE'
    elif 78.75 < wnd_dir_deg <= 101.25:
        return 'E'
    elif 101.25 < wnd_dir_deg <= 123.75:
        return 'ESE'
    elif 123.75 < wnd_dir_deg <= 146.25:
        return 'SE'
    elif 146.25 < wnd_dir_deg <= 168.75:
        return 'SSE'
    elif 168.75 < wnd_dir_deg <= 191.25:
        return 'S'
    elif 191.25 < wnd_dir_deg <= 213.75:
        return 'SSW'
    elif 213.75 < wnd_dir_deg <= 236.25:
        return 'SW'
    elif 236.25 < wnd_dir_deg <= 258.75:
        return 'WSW'
    elif 258.75 < wnd_dir_deg <= 281.25:
        return 'W'
    elif 281.25 < wnd_dir_deg <= 303.75:
        return 'WNW'
    elif 303.75 < wnd_dir_deg <= 326.25:
        return 'NW'
    elif 326.25 < wnd_dir_deg <= 348.75:
        return 'NNW'
    elif wnd_dir_deg > 348.75:
        return 'N'
    else:
        return None

def unwrap_worker(*arg,**kwarg):
    return Validate._worker(*arg,**kwarg)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
class Validate:
    def __init__(self,options):        
        self.logger = self._createLoggingFile()
        self._readConfigFile(options.config)
        self._readResults()

        mode = int(options.mode)
        if mode in [0]: self._plotDistribution()
        if mode in [1]: self._plotVulnerability()
        
        
        
    def _createLoggingFile(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        
        logger = logging.getLogger('BuildingsThreshold')
        logger.setLevel(logging.DEBUG)        
        logger.addHandler(stream_handler)
        return logger           
        
    
    def _readConfigFile(self,_config):
        parser = configparser.ConfigParser()
        parser.read(_config)
        
        _outFolder = parser.get('ANALYSIS','folder')
        self._outFile = os.path.join(_outFolder, 'TILE_{TILE}_BARFloodingSCN.feather') 
        self._geoj = gpd.read_file(parser.get('ANALYSIS','footprint'))
        print(self._geoj)
    
    
    def _readResults(self):               
        _template = self._outFile        
        info = [(_f,parse(_template,_f)['TILE']) for _f in glob(_template.format(TILE='*')) 
                                        if not parse(_template,_f) is None]
        self.logger.info(f'         files to read: \n{info}')
        lst_df = []
        for _f,_ in info:
            lst_df.append(pf.read_feather(_f))
        self.dfr = pd.concat(lst_df)
        self.logger.info(f'         files read:\n{self.dfr}')
    
        
    def _readBuildingFiles(self,options):
        parser = configparser.ConfigParser()
        parser.read(options.config)        
        
        tile_id = int(options.tile_id)
        prob_buildings = pd.read_csv(parser.get('ANALYSIS','problem'),sep=';').astype({'TILE_ID':int})
        self.pob_building_ids = prob_buildings[prob_buildings.TILE_ID==tile_id].NEW_BUILD_ID
        
        buildings = pd.read_csv(parser.get('ANALYSIS','buildings'),sep=';').astype({'TILE_ID':int})
        buildings = buildings[buildings.TILE_ID==int(tile_id)][['ID_BUILD_NEW','P10','LON_build','LAT_build']]
        gdf_build = gpd.GeoDataFrame({'geometry':[Point(lon,lat) for lon,lat in zip(buildings['LON_build'],buildings['LAT_build'])]})
        gdf_build.crs = 4326
        gdf_build['BUILD_ID'] = buildings['ID_BUILD_NEW'].values
        gdf_build['elev'] = buildings['P10'].values
        gdf_build['LAT'] = buildings['LAT_build'].values
        gdf_build['LON'] = buildings['LON_build'].values
        self.gdf_build = gdf_build               
        
        
    def _plotDistribution(self):
        df = self.data
        print(f'            dataframe:\n{df}')
        base_df = df.copy().drop_duplicates('BUILD_ID')
        # fig = plt.figure(figsize =([12, 16]))
        unique_hs = np.sort(df.Hs.unique())
        # sns.set_style("darkgrid")
        sns.set_context("paper")        
        fig, axes = plt.subplots(nrows=4, ncols=3, #sharey=True,
                                 sharey='row',
                                #  sharex=True,
                                 
                            #    gridspec_kw={'height_ratios': [2, 1]},
                               figsize=(12, 16))           
        # fig, axes = plt.subplots(nrows=4, ncols=3, sharex='col', sharey=True,
        #                        gridspec_kw={'height_ratios': [1, 1]},
        #                        figsize=(4, 7))
        num_fig=0
        labels=['74.0-74.5','74.5-75.0','75.0-75.5','75.5-76.0','76.0-76.5','76.5-77.0','77.0-77.5','77.5-78.0']
        df['bin_elev'] = pd.cut(df.elev,bins=np.arange(74,78.5,.5),labels=labels)
        max_count = df.groupby('Hs')[['BUILD_ID']].nunique().max().values[0]
        dummy = df[['bin_elev']].drop_duplicates()
        dummy['WL'] = np.nan
        dummy['BUILD_ID'] = np.nan
        num_colors= df.bin_elev.unique().shape[0]
        stats=[]
        for i in range(4):
            for j in range(3):  
                ax = axes[i,j]  
                df_ = df[df.Hs==unique_hs[num_fig]].sort_values(['WL','BUILD_ID']).drop_duplicates('BUILD_ID',keep='first')[['WL','Hs','elev','BUILD_ID','TP','bin_elev']]                
                count_lower_levels = df_[df_.WL<75.5].drop_duplicates('BUILD_ID').shape[0]
                count_higher_levels = df_[df_.WL>=75.5].drop_duplicates('BUILD_ID').shape[0] 
                
                if unique_hs[num_fig] <= 2:
                    for lev in np.arange(75.48,75.61,0.01):
                        low = df_[df_.WL<lev].drop_duplicates('BUILD_ID').shape[0]
                        hi = df_[df_.WL>=lev].drop_duplicates('BUILD_ID').shape[0] 
                        stats.append(pd.DataFrame({'y':(hi-low)/max_count * 100, 'x':lev,'hs':str(unique_hs[num_fig])},index=[0]))    
                    
                   
                # lows.append(count_lower_levels)
                # his.append(count_higher_levels)  
                # hs.append(unique_hs[num_fig])                     
                sns.histplot(pd.concat([df_,dummy]).reset_index(),
                                            x='WL',
                                            hue='bin_elev',
                                            hue_order=labels,
                                            binwidth=0.01,
                                            multiple='stack',
                                            ax=ax,
                                            legend=False,
                                            palette=sns.color_palette('PuBuGn',num_colors+1))
                ax.text(
                    0.52,
                    0.95,
                    f"Hs={unique_hs[num_fig]}m [{count_lower_levels} / {count_higher_levels}]",
                    ha="right",
                    va="top",
                    fontweight='bold',
                    transform=ax.transAxes
                )  

                # ax.set_ylim([0,max_count])
                ax.set_xlim([75.4,75.6])
                xticks = ax.get_xticks()                                
                ax.axvline(x=75.5,color='k',linewidth=1,linestyle=':')             
                if i in [0,1,2] and j == 0:
                    sns.despine(ax=ax,fig=fig,offset=10,bottom=True)                    
                    ax.set_xticks([])        
                    ax.xaxis.set_visible(False)
                    ax.yaxis.set_visible(True)
                    ax.spines['left'].set_color('black')                    
                    ax.spines['bottom'].set_color('white')                    
                elif i == 3 and j==0:
                    sns.despine(ax=ax,fig=fig,offset=10)
                    ax.set_xticks(xticks)
                elif i == 3  and j in [1,2]:     
                    sns.despine(ax=ax,fig=fig,offset=10,left=True)
                    # ax.set_yticks([])   
                    ax.xaxis.set_visible(True)  
                    ax.set_xticks(xticks)                                                 
                else:           
                    sns.despine(ax=ax,fig=fig,left=True,bottom=True)  
                    # ax.spines[['left','bottom']].set_visible(False) 
                    # ax.set_yticks([])     
                    ax.set_xticks([])        
                    ax.xaxis.set_visible(False)
                    ax.spines['bottom'].set_color('white')
                                    
                ax.set_ylabel('')
                ax.set_xlabel('')
                num_fig+=1    
        
        plt.close()
        stats = pd.concat(stats)
        print(stats)
        sns.set_style("darkgrid")
        sns.lineplot(stats,x='x',y='y',hue='hs')
        # plt.axhline(y=100,color='k',linewidth=2,linestyle=':')
        plt.axhline(y=0,color='k',linewidth=1)
        plt.xlabel('Thrs Level (m)',fontsize=14,fontweight='bold')
        plt.ylabel('Change in BAR (over vs. below thrs, %)',fontsize=14,fontweight='bold')
        plt.gca().tick_params(axis='both',labelsize=12)
        plt.legend(title='Significant Wave Height (m)',fontsize=12)
        plt.show()
        exit(1)
        
        
        # [ax.legend_.remove() for ax in axs]
        plt.tight_layout(rect=[0, 0, 1, 0.9])   
        fig.subplots_adjust(bottom=0.1,left=0.1) 
        fig.text(0.5, 0.02, 'Offshore Lake Level (m)', ha='center',fontsize=14,fontweight='bold')
        fig.text(0.02, 0.5, 'Number BARs',rotation='vertical', va='center',fontsize=14,fontweight='bold')
        axs=[]
        [axs.append(mpatches.Patch(color=c, label=l,alpha=.8)) for c,l in zip(sns.color_palette('PuBuGn',num_colors+2),labels)]
        # fig.legend(axs, loc='upper right')
        
        # handles, labels = axs.get_legend_handles_labels()   
        # exit(1)
        # handles,labels = axs[0].legend_.get_legend_handler_map()
        
    
        
        fig.legend(axs,labels, loc='upper right',title='Elev. (p10, m)')
        
        plt.show()
        
        plt.plot(hs,lows,'ok',ms=8,label='Levels < 75.5 m')
        plt.plot(hs,his,'ob',ms=8,label='Levels > 75.5 m')
        plt.xlabel('Significant Wave Height (m)',fontsize=14,fontweight='bold')
        plt.ylabel('Number of BARs',fontsize=14,fontweight='bold')
        plt.legend(title='Minimum Level BAR experienced flooding',fontsize=12)
        plt.gca().tick_params(axis='both',labelsize=12)
        adjust_spines(plt.gca(),['left','bottom'])
        plt.show()
        
        exit(1)
            
        
        exit(1)
        
             
        bins = [0] + list(np.arange(75.48,76.61,.01)) + [100]
        labels= [75.47] + list(np.arange(75.48,76.61,.01))
        
        df['wl_bins'] = pd.cut(df.WL,bins=bins,labels=labels)
        df = df.groupby(['wl_bins','Hs','BUILD_ID']).nunique().replace(0,np.nan).dropna(axis=0,how='all')[['WL']]
        df = df.reset_index().set_index('BUILD_ID').join(base_df.set_index('BUILD_ID')[['elev']])
        df = df.reset_index().sort_values(['wl_bins','Hs']).drop_duplicates('BUILD_ID',keep='first')
        sns.histplot(df,x='labels',hue='Hs')
        plt.show()        
        
        
        print(df)
        exit(1)
        
        
        bin_labels = ['<75.48','75.48-75.5','75.5-75.51','75.51-75.52','75.52-75.53','75.53-75.54','>75.54'] 
        df['wl_bins'] = pd.cut(df.WL,bins=[0,75.48,75.5,75.51,75.52,75.53,75.54,100],labels=bin_labels)
        
        # df = df.sort_values(by=['wl_bins','Hs','BUILD_ID']).drop_duplicates('BUILD_ID',keep='first')
        lst_df=[]
        for hs in np.unique(df.Hs):
            tmp = df[df.Hs==hs]
            tmp = tmp.sort_values(by=['wl_bins','BUILD_ID']).drop_duplicates('BUILD_ID',keep='first')
            print(tmp)
            print('-----------')
            lst_df.append(tmp)
        
        df = pd.concat(lst_df)
    
        # df = df.sort_values(by=['wl_bins','Hs','BUILD_ID']).drop_duplicates('BUILD_ID',keep='first')
        # sns.set_style("whitegrid")
        g = sns.FacetGrid(df, col="wl_bins", row='Hs',sharex=True,aspect=1)# sharey=True)
        g.map(sns.histplot,
                    'elev',
                    bins=10,              
                )
        
        for ax in g.axes.flatten():
            ax.set_title("")

        for col_val, ax in zip(g.col_names, g.axes[0]):
            ax.set_xlabel("")
            ax.set_title(col_val)

        for row_val, ax in zip(g.row_names, g.axes[:,0]):
            ax.set_ylabel("")
            ax.set_ylabel(row_val)
    
        for hs in np.unique(df.Hs):            
            big_total =0
            print(hs)
            for wl in bin_labels:
                print(wl)
                subset = df[( (df.Hs==hs) & (df.wl_bins==wl) )]
                
        # for (hs, wl), data_subset in df.groupby(["Hs", "wl_bins"]):
                total = len(subset)                
                big_total += total
                
                ax = g.axes[g.row_names.index(hs)][g.col_names.index(wl)]
                
                ax.text(
                    0.95,
                    0.95,
                    f"n = {total} / {big_total}",
                    ha="right",
                    va="top",
                    transform=ax.transAxes
                )
                
        plt.tight_layout()
        plt.savefig('histogram_346.png')
        plt.show()
        
    
    def _correctForDirections(self,dfg,trx):
        RAW_SCN_DIR = np.arange(0,69,10).tolist()[::-1] 
        possible_directions = np.unique(RAW_SCN_DIR)
        
        # extract transects from shapefile        
        _pts = dfg.sort_values(by='distance')['geometry']
        pts = _pts.iloc[[0,_pts.shape[0]-1]].values
        
        epsg = dfg.crs.to_epsg()
        trans = Transformer.from_crs(epsg,4326)
        lats,lons = trans.transform([pts[0].x,pts[1].x],[pts[0].y,pts[1].y])
        # print(f'point init (x,y): {pts[0].x}, {pts[0].y}')
        # dist,indx = self.tree.query(np.c_[pts[0].x,pts[0].y])
        # self.dfTrxInfo.append([trx.zfill(4),pts[0].x,pts[0].y,self.grid.iloc[indx].PT_ID.values[0],indx[0],dist[0]])
      
        lat1,lat2 = [math.radians(l) for l in lats]
        long1,long2 = [math.radians(l) for l in lons]
        
        bearing = math.atan2(
              math.sin(long2 - long1) * math.cos(lat2),
              math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(long2 - long1)
          )

        bearing = (math.degrees(bearing) + 360) % 360            
 
        inc_angles = [(bearing - angle + 540) % 360  for angle in possible_directions[::-1][:-1]]
        inc_angles_inv = [(bearing + angle + 540) % 360 for angle in possible_directions]
        
        SCEN_DIR1 = dict([(np.round(dir,2),key) for key,dir in zip(possible_directions[::-1][:-1],inc_angles)])
        SCEN_DIR2 = dict([(np.round(dir,2),key) for key,dir in zip(possible_directions,inc_angles_inv)])
        SCEN_DIR = SCEN_DIR1 | SCEN_DIR2
        SCEN_DIR = dict([(v,get_wnd_dir_scen(k)) for k,v in SCEN_DIR.items()])
        
        return SCEN_DIR
    
    def _worker(self,trx_id):
        sys.stdout.write(f'\r{trx_id}')       
        epsg = self.dfr[self.dfr.TRX_ID==trx_id].iloc[0].epsg 
        trx = str(trx_id)
        _geojson = os.path.join('runs',str(epsg),'info/geojson',f'TRX_{trx.zfill(6)}.geojson')            
        gdf = gpd.read_file(_geojson, driver='GeoJSON')

        SCEN_DIR = self._correctForDirections(gdf,trx)        
        # SCEN_DIR_NAMES = [elem for elem in list(SCEN_DIR.keys())]
        df_ = self.dfr[self.dfr.TRX_ID==trx_id]
        df_['GEODIR'] = df_.Dir.map(lambda x: SCEN_DIR[x])
        return df_
        
    def _plotVulnerability(self):
        geo_directions = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
        dfr = self.dfr
        dfr = dfr[dfr.BUILD_ELEV>0]
        self.dfr=dfr
        
        if not os.path.exists('all_scn_trx.pkl'):            
            pool = mpl.Pool(40)
            unique_trx = dfr.TRX_ID.unique()        
            # pool.starmap(unwrap_interp, zip([self]*len(iterable),iterable))
            with mpl.Pool(40) as pool:
                res = pool.starmap(unwrap_worker, zip([self]*len(unique_trx),unique_trx))
            dfr = pd.concat(res)
            with open('all_scn_trx.pkl','wb') as fid:
                pickle.dump(dfr,fid)
        else:
            with open('all_scn_trx.pkl','rb') as fid:
                dfr = pickle.load(fid)     
        
        unique_wls = np.unique(dfr.WL)        
        base = px.colors.sequential.Pinkyl
        N = len(unique_wls)
        
        colors = px.colors.sample_colorscale(base, [i/(N - 1) for i in range(N)])       
        
        geojson = self._geoj.__geo_interface__ 
        
        import plotly.graph_objects as go
        frames=[]
        dfr = dfr.astype({'Hs':str})
        unique_Hs = np.unique(dfr.Hs)[:-4]
        print(unique_Hs)
            
        for hs in unique_Hs:
            
            df = dfr[dfr.Hs==hs].round({'SCN_LEVEL':3,'BUILD_ELEV':3})
            df = df.sort_values(['WL','GEODIR']).drop_duplicates('BUILD_ID',keep='first')
            for dir in geo_directions:
                df__ = df[df.GEODIR==dir]
                subframes=[]
                total_bars = 0
                for i,wl in enumerate(unique_wls):
                    df_ = df__[df__.WL==wl]
                    total_bars += df_.shape[0]
                    subframes.append(
                                go.Scattermap(lat=df_.LAT, 
                                            lon=df_.LON,
                                            mode='markers',
                                            marker=go.scattermap.Marker(size=20,
                                                                        color=colors[i],      
                                                                        ),
                                            name=f'{wl}, BARS: {df_.shape[0]} (tot {total_bars})',
                                            showlegend=True,                                    
                                            legendgroup=wl,                                        
                                            customdata=df_[['BUILD_ID','TILE_ID','BUILD_ELEV','TP','GEODIR','TRX_ID','SCN_LEVEL','Hs','WL']],
                                            hovertemplate =(
                                                "<b>Tile %{customdata[1]}, BUILD ID %{customdata[0]}</b><br><br>" +
                                                "<b>TRX ID:  %{customdata[5]}</b><br>"+
                                                "    offshore lake elevation: %{customdata[8]} m<br>" + 
                                                "    elevation (p10):         %{customdata[2]} m<br>" +
                                                "    run-up elevation:       %{customdata[6]} m<br>" +
                                                "    wave height:             %{customdata[7]} m<br>" +
                                                "    wave period:             %{customdata[3]} s<br>" +
                                                "    wave direction:          %{customdata[4]} deg<br>" 
                                                )) 
                                
                    )
                frames.append(go.Frame(data=subframes,name=f"HS={hs}_Dir={dir}"))
                                 
                            
        # frames = [go.Frame(data=d,name=str(hs)) for d,hs in zip(data,np.unique(dfr.Hs))]
        steps_hs_dir = []
        for i, hs in enumerate(unique_Hs):
            for j, dir in enumerate(geo_directions):
                steps_hs_dir.append(
                    dict(
                        method="animate",
                        args=[[f"HS={hs}_Dir={dir}"], dict(mode="immediate",transition=dict(duration=0))],
                        label=f'<b>{hs}</b> m, {dir}'
                    )
                )      
     
            
        init_traces = []
        for i,wl in enumerate(np.unique(dfr.WL)):
            init_traces.append(
                go.Scattermap(
                    lat=[],
                    lon=[],
                    mode="markers",
                    name=str(wl),
                    legendgroup=str(wl),
                    showlegend=True,
                    marker=dict(size=20, color=colors[i])
                )
            ) 
                        
        fig = go.Figure(data=init_traces,
                            frames=frames,                       
                            layout=go.Layout(
                                map=dict(
                                            style='carto-positron',
                                            bearing=0,
                                            center=go.layout.map.Center(
                                                    lat=43.656,
                                                    lon=-77.972,
                                                ),
                                            pitch=0,
                                            zoom=8,
                                            layers=[
                                            {
                                                "below": "traces",
                                                "sourcetype": "raster",
                                                "sourceattribution": "ArcGIS Online, World Imagery",
                                                "source": [
                                                    "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                                                ]
                                            },
                                            dict(
                                                sourcetype="geojson",
                                                source=geojson,
                                                type="line",        # or "fill"
                                                color="white",
                                                line=dict(width=2)
                                            )
                                        ]),
                                                                
                ),
            )


        sliders = [
            # Slider 1: Hs (Wave Height)
            {
                'active': 0,
                # 'yanchor': 'top',
                'y': 0,
                'xanchor': 'left',
                'currentvalue': {
                    'prefix': 'Hs (Wave Height), Dir: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'pad': {'b': 10, 't': 50},
                'len': 1.3,
                'x': 0,
                'steps': steps_hs_dir,
            },
        ]




        # Update layout
        fig.update_layout(
            sliders=sliders,
            title='Wave Analysis - Use sliders to change Significant Wave Heights and Direction',                           
        )
        pio.write_html(fig, file='test_anim.html', auto_open=False, auto_play=False)
               
      
        
        
if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")


    parser.add_option("-m", "--mode",
                      dest="mode",
                      metavar="OPTION",
                      help="mode") 
    
    parser.add_option("-c", "--config",
                      dest="config",
                      metavar="FOLDER",
                      help="directory where are saved the CSHORE results in *.csv") 


    # parser.add_option("-t", "--tileID",
    #                   dest="tileID",
    #                   metavar="OPTION",
    #                   help="tile ID") 

    # parser.add_option("-p", "--csvTemplate",
    #                   dest="csvTemplate",
    #                   metavar="TEMPLATE",
    #                   default='TRX_{TRX}',
    #                   help="template for directory name")

    # parser.add_option("-g", "--geojFolder",
    #                   dest="geojFolder",
    #                   metavar="Folder",
    #                   help="geojson folder")


    (options, args) = parser.parse_args() 
    Validate(options)        