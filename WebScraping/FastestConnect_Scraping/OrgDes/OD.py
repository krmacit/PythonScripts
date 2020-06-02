import pandas as pd

file = pd.read_excel("FastestConnectAirports.xlsx")

print(file)

Output = pd.DataFrame(columns=['Org', 'Des'])

for index1, row1 in file.iterrows():
    for index2, row2 in file.iterrows():
        if row1['Airport'] != row2['Airport']:
            Output = Output.append({'Org': row1['Airport'], 'Des': row2['Airport']}, ignore_index=True)
        else:
            print(index1)


Output.to_csv("allODAirport.csv")
Output.to_excel("allODAirport.xlsx")