import pandas as pd

file = pd.read_excel("FastestConnectAirports.xlsx")
des = pd.read_excel("DestRemovedDuplicate.xlsx")

check = des.Des.values

print(file)
file['Des']=""
file['DesCity']=""
file['DesCity_Name']=""
Output = pd.DataFrame(columns=['Airport', 'City', 'City_Name', 'Des', 'DesCity', 'DesCity_Name'])

for index, row in file.iterrows():
    if row['City'] in check:
        file['Des'] = row['Airport']
        file['DesCity'] = row['City']
        file['DesCity_Name'] = file['City_Name']
        Output = Output.append(file)
        print(index)

Output.to_csv("allODAirport.csv")
Output.to_excel("allODAirport.xlsx")