from pprint import pformat

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt


path_geoshape = r'geoshapes\eindhoven.geojson'
path_results = r'results\eindhoven_20230312.json'

# Load data
eindhoven_geodata = gpd.read_file(path_geoshape)
eindhoven_funda_sales_data = pd.read_json(path_results)

#%% Cleaning
# Make the dubble name neiborhoods more consisted
eindhoven_geodata.name = eindhoven_geodata.name.astype("string")
eindhoven_funda_sales_data.neigborhood = eindhoven_funda_sales_data.neigborhood.astype(
    "string"
)

# Make the names of the neighborhoods the same for easy mergning
eindhoven_geodata.name = eindhoven_geodata.name.str.replace(", ", ",")
eindhoven_funda_sales_data.neigborhood = (
    eindhoven_funda_sales_data.neigborhood.str.replace(", ", ",")
)

#%% Validate Cleaning
assert (
    len(
        list(
            set(eindhoven_funda_sales_data.neigborhood.unique())
            - set(eindhoven_geodata.name.unique())
        )
    )
    == 0
)

#%% Info about the difference
neigborhoods_without_sale = list(
    set(eindhoven_geodata.name.unique())
    - set(eindhoven_funda_sales_data.neigborhood.unique())
)
print(
    f"Neigborhoods not included in the sales data: \n{pformat(neigborhoods_without_sale)}"
)

#%% Summary of all interesting parameters
aggregations = {
    "number_of_houses_for_sale": ("price", "size"),
    "mean_area": ("area", "mean"),
    "mean_price": ("price", "mean"),
    "mean_bedrooms": ("bedrooms", "mean")
}
summary_sales = eindhoven_funda_sales_data.groupby("neigborhood").agg(**aggregations)

# %% Merge geo data and summary
eindhoven_merge_geodata = eindhoven_geodata.merge(
    summary_sales, how='left',  left_on="name", right_on="neigborhood"
)

#%% plot geodata
fig, ax = plt.subplots(ncols=2, nrows=2 ,sharex=True, sharey=True)
fig.suptitle('Mean statistics Eindhoven per neighborhood')
eindhoven_merge_geodata.plot(ax = ax[0][0], column="number_of_houses_for_sale", legend=True, missing_kwds={'color': 'lightgrey'})
ax[0][0].set_title('number of houses')
eindhoven_merge_geodata.plot(ax = ax[1][0], column="mean_price", legend=True, missing_kwds={'color': 'lightgrey'})
ax[1][0].set_title('Price (euro)')
eindhoven_merge_geodata.plot(ax = ax[0][1], column="mean_area", legend=True, missing_kwds={'color': 'lightgrey'})
ax[0][1].set_title('Area (m2)')
eindhoven_merge_geodata.plot(ax = ax[1][1], column="mean_bedrooms", legend=True, missing_kwds={'color': 'lightgrey'})
ax[1][1].set_title('Number of bedrooms')
plt.show()
