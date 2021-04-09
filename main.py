import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
print(price_by_region_type)

fig, ax = plt.subplots()






