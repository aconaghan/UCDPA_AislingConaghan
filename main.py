import pandas as pd

#importing dataset
df = pd.read_csv(r'Property_Price_Register_Ireland-05-04-2019.csv')
print(df.head())
print(df.shape)
col_list = df.columns
print(col_list)

#tidying up data types
print(df.dtypes)
df['Date of Sale (dd/mm/yyyy)'] = pd.to_datetime(df['Date of Sale (dd/mm/yyyy)'])
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

#adding a flag for Dublin
result = []
for value in df_no_dup["Region"]:
    if value == "Dublin":
        result.append(1)
    else:
        result.append(0)

df_no_dup["Dublin_Flag"] = result

#merging on pop density
pop_data = pd.read_excel(r'pop_density.xlsx', skiprows=[0,1])
print(pop_data)

df2 = df_no_dup.merge(pop_data, on='Region', how='left')
print(df2[df2['Region'] == "Dublin"])











