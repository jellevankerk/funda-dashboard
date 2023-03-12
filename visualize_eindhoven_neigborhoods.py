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
    "max_area": ("area", "max"),
    "mean_area": ("area", "mean"),
    "min_area": ("area", "min"),
    "max_price": ("price", "max"),
    "mean_price": ("price", "mean"),
    "min_price": ("price", "min"),
    "max_bedrooms": ("bedrooms", "max"),
    "mean_bedrooms": ("bedrooms", "mean"),
    "min_bedrooms": ("bedrooms", "min"),
}
summary_sales = eindhoven_funda_sales_data.groupby("neigborhood").agg(**aggregations)

# %% Merge geo data and summary
eindhoven_merge_geodata = eindhoven_geodata.merge(
    summary_sales, how='left',  left_on="name", right_on="neigborhood"
)

#%% plot geodata
eindhoven_merge_geodata.plot(column="number_of_houses_for_sale", legend=True, missing_kwds={'color': 'lightgrey'})
eindhoven_merge_geodata.plot(column="mean_price", legend=True, missing_kwds={'color': 'lightgrey'})
plt.show()