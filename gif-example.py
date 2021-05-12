
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os
import imageio

import matplotlib.patches as mpatches


        
def hex_map(img_count):
    for offset in range(img_count,0,-1):
        #  pull data from the COVID API
        df = pd.read_csv('https://api.coronavirus.data.gov.uk/v2/data?areaType=ltla&metric=newCasesBySpecimenDateRollingRate&format=csv')
        df['date'] = pd.to_datetime(df['date'],errors = 'coerce')
        df = df.rename(columns={"areaCode": "Lacode"})
        
        # keep latest date for shading the map
        maxdate = max(df['date'])-pd.DateOffset(days=offset)
        df = df[(df['date']==maxdate)].reset_index()
        
        A = []
        for x in range(0,len(df)):
            if df.loc[x,'newCasesBySpecimenDateRollingRate'] < 10:
                A.append('1: Under 10')
            elif df.loc[x,'newCasesBySpecimenDateRollingRate'] < 25:
                A.append('2: 10 - 25')    
            elif df.loc[x,'newCasesBySpecimenDateRollingRate'] < 50:
                A.append('3: 25 - 50')    
            elif df.loc[x,'newCasesBySpecimenDateRollingRate'] < 100:
                A.append('4: 50 - 100')
            elif df.loc[x,'newCasesBySpecimenDateRollingRate'] < 200:
                A.append('5: 100 - 200')
            else:  
                A.append('6: Over 200')       
        
        df['rateGrouped'] = A
        
        # Hex map data from the gpkg from here https://github.com/houseofcommonslibrary/uk-hex-cartograms-noncontiguous
        gpkg = os.path.dirname(__file__)+'/LocalAuthorities-lowertier.gpkg'
        
        # Pull the layer information from the geopackage
        ltla_hex = gpd.read_file(gpkg, layer='4 LTLA-2019')
        labels = gpd.read_file(gpkg, layer='1 Group labels')
        background = gpd.read_file(gpkg, layer='7 Background')
        
        # Merge the case data to the hex map
        ltla_hex_data = ltla_hex.merge(df,on='Lacode',how='left')
        
        colPalette = { '1: Under 10': '#E0E543',
                       '2: 10 - 25': '#74BB68',
                       '3: 25 - 50': '#399384',
                       '4: 50 - 100': '#2067AB',
                       '5: 100 - 200':'#12407F',
                       '6: Over 200':'#53084A'
                       }
        # Make a plot of the LTLAs colored by the number of cases
        fig, ax = plt.subplots(figsize=(10,13),dpi=(150))
        
        # set the background colour for the UK map
        background.plot(ax=ax,alpha=0.3, color='xkcd:grey')
        
        for rateGrouped, data in ltla_hex_data.groupby('rateGrouped'):
        
            # Define the color for each group using the dictionary
            color = colPalette[rateGrouped]
            
            # Plot each group using the color defined above
            data.plot(color=color,
                      ax=ax,
                      label=rateGrouped)
        
        # add labels to each area
        for x in range(0,len(labels)):
            plt.text(labels['geometry'][x].x,labels['geometry'][x].y-0.25,labels['Group-labe'][x],horizontalalignment=labels['LabelPosit'][x].lower(),fontsize=6,color='xkcd:dark grey')
        
        # legend
        vol1 = str(len(ltla_hex_data[ltla_hex_data['rateGrouped']=='1: Under 10']))
        vol2 = str(len(ltla_hex_data[ltla_hex_data['rateGrouped']=='2: 10 - 25']))
        vol3 = str(len(ltla_hex_data[ltla_hex_data['rateGrouped']=='3: 25 - 50']))
        vol4 = str(len(ltla_hex_data[ltla_hex_data['rateGrouped']=='4: 50 - 100']))
        vol5 = str(len(ltla_hex_data[ltla_hex_data['rateGrouped']=='5: 100 - 200']))
        vol6 = str(len(ltla_hex_data[ltla_hex_data['rateGrouped']=='6: Over 200']))
    
        lab_Under_10 = mpatches.Patch(color='#E0E543', label='Under 10 ('+vol1+')')
        lab_10_25 = mpatches.Patch(color='#74BB68', label='10 - 25 ('+vol2+')')
        lab_25_50 = mpatches.Patch(color='#399384', label='25 - 50 ('+vol3+')')
        lab_50_100 = mpatches.Patch(color='#2067AB', label='50 - 100 ('+vol4+')')
        lab_100_200 = mpatches.Patch(color='#12407F', label='100 - 200 ('+vol5+')')
        lab_over_200 = mpatches.Patch(color='#53084A', label='Over 200 ('+vol6+')')
        plt.legend(handles=[lab_Under_10,lab_10_25,lab_25_50, lab_50_100,lab_100_200,lab_over_200])
    
        # add the data
        plt.text(50,-1,str(maxdate.date()),fontsize=20)
    
        # Remove the axes
        ax.axis("off") 
        
        plt.title("LTLAs in the UK\n 7 Day Case Rates per 100k Population",fontsize=16)
            
        # save the image
        fig.savefig(os.path.dirname(__file__)+'/out/img-'+str(offset)+'.png')
        filenames.append('img-'+str(offset)+'.png')

filenames = []
hex_map(img_count=10)

images = []
for filename in filenames:
    images.append(imageio.imread(os.path.dirname(__file__)+"/out/"+filename))
imageio.mimsave(os.path.dirname(__file__)+'/out/movie.gif', images,duration=0.75)
