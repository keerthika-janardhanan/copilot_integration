import pandas as pd

# Read testmanager.xlsx
df = pd.read_excel('framework_repos/a765e0ec2d83/testmanager.xlsx')

# Update IDName for create_payables test
df.loc[df['TestCaseID'] == 'create_payables', 'IDName'] = 'Invoice ID'

# Save back
df.to_excel('framework_repos/a765e0ec2d83/testmanager.xlsx', index=False)

print('✅ Updated testmanager.xlsx: Set IDName to "Invoice ID" for create_payables test')
print('\nUpdated row:')
print(df[df['TestCaseID'] == 'create_payables'][['TestCaseID', 'DatasheetName', 'ReferenceID', 'IDName']].to_string(index=False))
