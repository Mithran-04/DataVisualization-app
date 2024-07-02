import pandas as pd
from sqlalchemy import create_engine

csv_file_path = "C:/Users/mithr/Documents/Datasets/neww/RulesFinal_Data.csv"

df = pd.read_csv(csv_file_path)
df.columns = [col.lower() for col in df.columns]
df = df.applymap(lambda s: s.lower() if type(s) == str else s)


db_username = ''
db_password = ''
db_host = ''
db_port = ''  # default is 5432
db_name = ''
db_table_name = ''

connection_string = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'

engine = create_engine(connection_string)
df.to_sql(db_table_name, engine, if_exists='replace', index=False)

print("Data uploaded successfully!")
