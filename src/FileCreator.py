import pandas as pd
import numpy as np

# Load the CSV file
file_path = 'C:/Users/mithr/Documents/Datasets/bre-rulesA1May15.xlsx - BRE Rules.csv'
df = pd.read_csv(file_path, header=None)

# Extract feature headings from the first column
feature_headings = df.iloc[:, 0].dropna().values

# Initialize the new dataframe structure with appropriate columns
new_columns = list(feature_headings)

# Create an empty dataframe with the new columns
new_df = pd.DataFrame(columns=new_columns)

# Extract data for each applicant and fill the new dataframe
num_features = len(feature_headings)
applicant_data = []

for col in range(1, df.shape[1], 3):  # Increment by 3 to skip the empty column
    applicant = []
    for i in range(num_features):
        if i < 5:  # For the first five features, take the first column
            value_col = col
        else:  # For the remaining features, take the second column
            value_col = col + 1
        
        # Extract the value
        if value_col < df.shape[1]:
            value = df.iloc[i, value_col]
        else:
            value = np.nan
        
        # Append the value
        applicant.append(value)
    
    applicant_data.append(applicant)

# Convert the list of applicants' data to a DataFrame
applicant_df = pd.DataFrame(applicant_data, columns=new_columns)

# Save the new dataframe to a CSV file
new_file_path = 'C:/Users/mithr/Documents/Datasets/neww/RulesFinal1212_Data.csv'
applicant_df.to_csv(new_file_path, index=False)

new_file_path















# import pandas as pd
# import numpy as np

# # Load the CSV file
# file_path = 'C:/Users/mithr/Documents/Datasets/bre-rulesA1May15.xlsx - BRE Rules.csv'
# df = pd.read_csv(file_path, header=None)

# # Extract feature headings from the first column
# feature_headings = df.iloc[:, 0].dropna().values

# # Initialize the new dataframe structure with appropriate columns
# new_columns = list(feature_headings)

# # Create an empty dataframe with the new columns
# new_df = pd.DataFrame(columns=new_columns)

# # Extract data for each applicant and fill the new dataframe
# num_features = len(feature_headings)
# applicant_data = []

# for col in range(1, df.shape[1], 3):  # Increment by 3 to skip the empty column and the rule column
#     applicant = []
#     for i in range(num_features):
#         value_col = col
        
#         # Extract the value
#         if value_col < df.shape[1]:
#             value = df.iloc[i, value_col]
#         else:
#             value = np.nan
        
#         # Append the value
#         applicant.append(value)
    
#     applicant_data.append(applicant)

# # Convert the list of applicants' data to a DataFrame
# applicant_df = pd.DataFrame(applicant_data, columns=new_columns)

# # Save the new dataframe to a CSV file
# new_file_path = 'C:/Users/mithr/Documents/Datasets/neww/RulesFinal2222_Data.csv'
# applicant_df.to_csv(new_file_path, index=False)

# new_file_path











# import pandas as pd
# import numpy as np

# # Load the CSV file
# file_path = "C:/Users/mithr/Documents/Datasets/bre-rulesA1May15.xlsx - BRE Rules.csv"
# df = pd.read_csv(file_path, header=None)

# # Extract feature headings from the first column
# feature_headings = df.iloc[:, 0].dropna().values

# # Initialize the new dataframe structure with appropriate columns
# new_columns = []
# for heading in feature_headings:
#     new_columns.append(heading)
#     new_columns.append(f"{heading}Stat")

# # Create an empty dataframe with the new columns
# new_df = pd.DataFrame(columns=new_columns)

# # Extract data for each applicant and fill the new dataframe
# num_features = len(feature_headings)
# applicant_data = []

# for col in range(1, df.shape[1], 3):  # Increment by 3 to skip empty columns
#     applicant = []
#     for i in range(num_features):
#         value_col = col
#         rule_col = value_col + 1
        
#         # Extract the value and rule
#         if value_col < df.shape[1]:
#             value = df.iloc[i, value_col]
#         else:
#             value = np.nan
        
#         if rule_col < df.shape[1]:
#             rule = df.iloc[i, rule_col]
#         else:
#             rule = np.nan
        
#         # Append the value and rule
#         applicant.append(value)
#         applicant.append(rule)
    
#     applicant_data.append(applicant)

# # Convert the list of applicants' data to a DataFrame
# applicant_df = pd.DataFrame(applicant_data, columns=new_columns)

# # Save the new dataframe to a CSV file
# new_file_path = "C:/Users/mithr/Documents/Datasets/neww/RulesFinal_Data.csv"
# applicant_df.to_csv(new_file_path, index=False)


# import pandas as pd

# # Load the CSV file
# csv_file_path = "C:/Users/mithr/Documents/Datasets/bre-rulesA1May15.xlsx - BRE Rules.csv"
# data = pd.read_csv(csv_file_path)

# # Display the first 10 rows
# print(data.head(10))




# import pandas as pd

# # Load the Excel file
# file_path = "C:/Users/mithr/Documents/Datasets/bre-rulesA1May15.xlsx - BRE Rules.csv"
# try:
#     # Attempt to read with openpyxl (for .xlsx files)
#     df = pd.read_excel(file_path, header=None, engine='openpyxl')
# except Exception as e:
#     print(f"Failed to read with openpyxl: {e}")
#     try:
#         # Attempt to read with xlrd (for .xls files)
#         df = pd.read_excel(file_path, header=None, engine='xlrd')
#     except Exception as e:
#         print(f"Failed to read with xlrd: {e}")
#         raise Exception("Failed to read the Excel file with both engines. Please check the file format and integrity.")

# # Extract the features and user data
# features = df.iloc[:, 0].dropna().tolist()
# data = df.iloc[:, 1:].dropna(axis=1, how='all')

# # Initialize lists to hold processed data
# processed_data = []

# # Iterate through the data columns to extract each user's information
# num_features = len(features)
# num_columns = data.shape[1]
# i = 0

# while i < num_columns:
#     user_data = []
#     for j in range(num_features):
#         user_data.append(data.iloc[j, i])
#         user_data.append(data.iloc[j, i+1])
#     processed_data.append(user_data)
#     i += 3  # Skip to the next user (current user data + empty column)

# # Create a DataFrame with the transformed data
# columns = []
# for feature in features:
#     columns.append(feature)
#     columns.append(f"{feature}Rule")

# # Transpose the processed data to match the required format
# processed_data = list(map(list, zip(*processed_data)))

# # Create the final DataFrame
# final_df = pd.DataFrame(processed_data, columns=columns)
# # Save the DataFrame to a CSV file
# final_df.to_csv('C:/Users/mithr/Documents/Datasets/TransformedData.csv', index=False)

# print("Transformation complete. The data has been saved to 'TransformedData.csv'.")














# # import pandas as pd
# # import openpyxl
# # # Load the Excel file
# # file_path = "C:/Users/mithr/Documents/Datasets/bre-rulesA1May15.xlsx - BRE Rules.csv"
# # xl = pd.ExcelFile(file_path,engine="openpyxl")

# # # Assume the first sheet is the one we want to process
# # sheet_name = xl.sheet_names[0]
# # df = xl.parse(sheet_name)

# # # Initialize lists to hold the data
# # headers = ["ApplicantID", "CreatedAt", "AreaOffice", "RO", "Pincode"]
# # features = []
# # users_data = []

# # # Identify the feature names and split the data for each user
# # for col in df.columns[1:]:  # Skip the first column which is 'features'
# #     if pd.isna(df[col].iloc[0]):  # Empty column signifies end of user data
# #         continue
# #     else:
# #         features.append(df[col].iloc[0])
# #         user_features = df[col].iloc[1:].tolist()
# #         user_rules = df[col + 1].iloc[1:].tolist()
        
# #         # Assuming the first column is the ApplicantID
# #         applicant_id = user_features[0]
# #         user_data = [applicant_id] + user_features[1:] + user_rules
# #         users_data.append(user_data)

# # # Build the header row
# # extended_headers = headers + features + [feature + "Rule" for feature in features]

# # # Convert the users data into a DataFrame
# # data_df = pd.DataFrame(users_data, columns=extended_headers)

# # # Save the new DataFrame to a CSV file
# # new_csv_path = 'C:/Users/mithr/Documents/Datasets/TransformedData.csv'
# # new_data.to_csv(new_csv_path, index=False)

# # print(f"Transformed data saved to {new_csv_path}")
