import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

#importing dataset
df = pd.read_csv(r'Property_Price_Register_Ireland-05-04-2019.csv')
print(df.head())
print(df.shape)
col_list = df.columns
print(col_list)

#tidying up data types
print(df.dtypes)
df['Date of Sale (dd/mm/yyyy)'] = pd.to_datetime(df['Date of Sale (dd/mm/yyyy)'])
print(df['Price (€)'].apply(type).value_counts())
df['Price (€)'] = df['Price (€)'].str[1:]
df['Price (€)'] = df['Price (€)'].str.replace(',','').astype('float')
print(df.dtypes)
df['Year'] = pd.DatetimeIndex(df['Date of Sale (dd/mm/yyyy)']).year

#removing duplicate rows
df_dup = df[df.duplicated()]
dup_add = df_dup['Address'].tolist()
check_dup = df[df['Address'].isin(dup_add)]
print(check_dup.iloc[0:10,0:2])
print(df_dup.shape)
df_no_dup = df.drop_duplicates(subset = col_list)
print(df_no_dup.shape)

#checking for missing values
print(df_no_dup.isnull().sum())
df_no_dup = df_no_dup.fillna(0)

#count of irish entries in 'Description of Property'
print(df_no_dup['Description of Property'].value_counts())
df_no_dup = df_no_dup[df_no_dup['Description of Property'].isin(['Second-Hand Dwelling house /Apartment', 'New Dwelling house /Apartment'])]
print(df_no_dup.shape)

#dictionary for mapping county to region
map_region = { 'Cavan':'Border',
               'Donegal':'Border',
               'Leitrim':'Border',
               'Monaghan':'Border',
               'Sligo':'Border',
               'Dublin':'Dublin',
               'Kildare':'Mid-East',
               'Louth':'Mid-East',
               'Meath':'Mid-East',
               'Wicklow':'Mid-East',
               'Laois':'Midland',
               'Longford':'Midland',
               'Offaly':'Midland',
               'Westmeath':'Midland',
               'Clare':'Mid-West',
               'Limerick':'Mid-West',
               'Tipperary':'Mid-West',
               'Carlow':'South-East',
               'Kilkenny':'South-East',
               'Waterford':'South-East',
               'Wexford':'South-East',
               'Cork':'South-West',
               'Kerry':'South-West',
               'Galway':'West',
               'Mayo':'West',
               'Roscommon':'West' }

#mapping county to region
df_no_dup['Region'] = df_no_dup['County'].map(map_region)

#adding a flag for Dublin using looping
result = []
for value in df_no_dup["Region"]:
    if value == "Dublin":
        result.append(1)
    else:
        result.append(0)

df_no_dup["Dublin_Flag"] = result

#merging on pop density
pop_data = pd.read_excel(r'pop_density.xlsx', skiprows=[0,1])
print(pop_data.dtypes)
cols = pop_data.select_dtypes(['object']).columns
pop_data[cols] = pop_data[cols].apply(lambda x: x.str.strip())

df2 = df_no_dup.merge(pop_data, on='Region', how='left')
print(df2.isnull().sum())
print(df2.shape)
print(df2.columns)

#grouped summary statistics
avg_price_per_county = df2.groupby('County')['Price (€)'].mean().sort_values(ascending=False)
print(avg_price_per_county)

def pivot_to_csv(data, values, index, aggfunc, output_file):

    # Create pivot table of summary statistics
    table = data.pivot_table(values=values, index=index, aggfunc=aggfunc)

    # Write the new DataFrame to a csv file
    filename = str(output_file) + '.csv'
    table.to_csv(filename)

pivot_to_csv(df2, 'Price (€)',  ['Region','County'], [np.mean, np.median, np.min, np.max], 'SummStats_Region_County')

pivot_to_csv(df2, 'Price (€)',  ['Region','Description of Property'], np.mean, 'Avg_Price_Region_TypeProperty')

#bar plot of average price by region and property type
price_by_region_type = df2.groupby(['Region', 'Description of Property'])['Price (€)'].mean().reset_index()
price_by_region_type = price_by_region_type.sort_values('Price (€)', ascending=False)
print(price_by_region_type)
new = price_by_region_type[price_by_region_type['Description of Property'] == 'New Dwelling house /Apartment'].reset_index()
second_hand = price_by_region_type[price_by_region_type['Description of Property'] == 'Second-Hand Dwelling house /Apartment'].reset_index()
region_list = price_by_region_type['Region'].unique()
print(region_list)

x = np.arange(len(region_list))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, new['Price (€)'], width, label='New House/Apartment')
rects2 = ax.bar(x + width/2, second_hand['Price (€)'], width, label='Second-Hand House/Apartment')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Average Price (€)')
ax.set_xlabel('Region')
ax.set_title('Average Price by House Type in Ireland')
ax.set_xticks(x)
ax.set_xticklabels(region_list, rotation=45)
ax.legend()

fig.tight_layout()

plt.show()

#time series graph of average price by region
avg_price_by_year = df2.groupby(['Region','Year'])['Price (€)'].mean().reset_index()
df3 = avg_price_by_year.set_index('Year')

border = df3[df3['Region'] == "Border"]
dublin = df3[df3['Region'] == "Dublin"]
me = df3[df3['Region'] == "Mid-East"]
west = df3[df3['Region'] == "West"]
mw = df3[df3['Region'] == "Mid-West"]
midland = df3[df3['Region'] == "Midland"]
se = df3[df3['Region'] == "South-East"]
sw = df3[df3['Region'] == "South-West"]

def plot_timeseries(axes, x, y, marker, color, label, xlabel, ylabel):

    axes.plot(x,y, marker=marker, color=color, label=label)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.legend(loc=2, prop={'size': 7})

fig, ax = plt.subplots()

plot_timeseries(ax, dublin.index, dublin['Price (€)'], "o", "tab:blue", "Dublin", "Year", "Average House Price (€)")
plot_timeseries(ax, border.index, border['Price (€)'], "o", "tab:orange", "Border", "Year", "Average House Price (€)")
plot_timeseries(ax, me.index, me['Price (€)'], "o", "tab:green", "Mid-East", "Year", "Average House Price (€)")
plot_timeseries(ax, mw.index, mw['Price (€)'], "o", "tab:red", "Mid-West", "Year", "Average House Price (€)")
plot_timeseries(ax, se.index, se['Price (€)'], "o", "tab:purple", "South-East", "Year", "Average House Price (€)")
plot_timeseries(ax, sw.index, sw['Price (€)'], "o", "tab:pink", "South-West", "Year", "Average House Price (€)")
plot_timeseries(ax, midland.index, midland['Price (€)'], "o", "tab:cyan", "Midland", "Year", "Average House Price (€)")
plot_timeseries(ax, west.index, west['Price (€)'], "o", "tab:olive", "West", "Year", "Average House Price (€)")

ax.set_title("Average House Price by Region from 2010-2019")
plt.xticks(range(2010, 2020))

plt.tight_layout()

plt.show()









