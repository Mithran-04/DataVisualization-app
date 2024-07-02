from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware  
import pandas as pd
import io
import google.generativeai as genai
import re
from langchain_experimental.agents import create_csv_agent
from langchain_google_genai import GoogleGenerativeAI
import os
from typing import List
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
API_KEY = os.getenv('GENAI_API_KEY')
genai.configure(api_key=API_KEY)

os.environ['GOOGLE_API_KEY'] = API_KEY

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def extract_sql_query(response_text):
    """Extracts the SQL query from the response text using regular expressions."""
    response_text = re.sub(r"```sql\n|```", "", response_text).strip()
    print("Response text ",response_text)
    return response_text


@app.post("/get_csv_schema/")
async def get_csv_schema(file: UploadFile = File(...)):
    csv_content = await file.read()
    df = pd.read_csv(io.BytesIO(csv_content))
    features = df.columns.tolist()
    return {"features": features}

@app.post("/get_csv_metadata/")
async def get_csv_schema(file: UploadFile = File(...)):
    metadata_file_path = "C:/Users/mithr/Downloads/metadata (8) - Copy.json"
    with open(metadata_file_path, "r") as f:
        metadata = json.load(f)
    return {"features": metadata}


@app.post("/get_feature_metadata/")
async def get_feature_metadata(CsvSchema: str = Form(...)):
    try:
        features = CsvSchema.split(',')

        model = genai.GenerativeModel(model_name='gemini-pro', generation_config={'temperature': 0.0})

        feature_metadata = []

        def process_features_batch(batch):
            features_list = ", ".join(batch)
            prompt = f"Provide detailed metadata for the following features in a CSV file: {features_list}. For each feature, give Description, Data type, and Preferred Visualization Type (Text or Table or Graph(Mention the graph type)) in JSON format as key-value pairs , both key and value in quotes."
            
            response = model.generate_content(prompt)
            
            # Extract the JSON string from the response
            metadata_text = response.candidates[0].content.parts[0].text.strip()
            print("Metadata text:", metadata_text)
            
            # Remove the surrounding markdown code block if present
            if metadata_text.startswith("```json"):
                metadata_text = metadata_text[len("```json"):].strip()
            if metadata_text.startswith("```"):
                metadata_text = metadata_text[len("```"):].strip()
            if metadata_text.endswith("```"):
                metadata_text = metadata_text[:-len("```")].strip()
            
            # Parse the JSON string into a dictionary
            metadata_dict = json.loads(metadata_text)
            # Extract metadata for each feature in the batch
            batch_metadata = []
            for feature in batch:
                print("Feature:  ",feature)
                feature_data = metadata_dict.get(feature, {})
                print("IN loop   ",feature_data)
                if isinstance(feature_data, str):
                    feature_data = {"Description": feature_data, "Data type": "", "Preferred Visualization Type": ""}
        
                metadata = {
                    "name": feature,
                    "description": feature_data.get("Description", ""),
                    "dataType": feature_data.get("Data type", ""),
                    "preferredVisualizationType": feature_data.get("Preferred Visualization Type", "")
                }
                batch_metadata.append(metadata)
            
            return batch_metadata

        # Split the features into batches of 30 and process each batch
        batch_size = 30
        for i in range(0, len(features), batch_size):
            batch = features[i:i+batch_size]
            batch_metadata = process_features_batch(batch)
            feature_metadata.extend(batch_metadata)
        
        return {"metadata": feature_metadata}
    
    except Exception as e:
        print("Error generating feature metadata:", str(e))
        raise


@app.post("/generate_sql/")
async def generate_sql(file: UploadFile = File(...), sentence: str = Form(...), metadata: str = Form(...),CsvSchema: str = Form(...)):
    # Parse metadata
    metadata = json.loads(metadata)

    def extract_relevant_metadata(sentence, metadata):
        sentence=sentence.lower()
        relevant_columns = []
        for item in metadata:
            if item['name'].lower() in sentence:
                relevant_columns.append(item)
        return relevant_columns
    
    relevant_metadata = extract_relevant_metadata(sentence, metadata)
    if not relevant_metadata:
        relevant_metadata = metadata
    

    table_name = "applicantsdata_final"
    model = genai.GenerativeModel(model_name='gemini-pro', generation_config={'temperature':0.0})
    agent = create_csv_agent(GoogleGenerativeAI(temperature=0, model="gemini-pro"), "C:/Users/mithr/Documents/Datasets/neww/RulesFinal_Data.csv",verbose=True,allow_dangerous_code=True,handle_parsing_errors=True)

    response_type_prompt = f"Determine if a text response, or a table response, or a graph response is best suited (See metadata preferredVisualizationType) for the following query: {sentence}. CSV file metadata: {relevant_metadata}. Metadata includes Description,Data type and preferredVisualizationType for all the columns. If peferredVisualizationType is not empty then strictly select the visualization type given in the metadata. Provide only text, or table, or graph"
    response_type_response = model.generate_content(response_type_prompt)
    response_type = response_type_response.text.lower()  # Ensure response type is in lowercase
    print(response_type)

    if "text" in response_type:
        text_response_prompt = f"Generate a detailed text response for the following sentence: {sentence}."
        text_response = agent.run(text_response_prompt)
        return {"response_type": "text", "text_response": text_response.strip()}

    if "graph" in response_type or "chart" in response_type or "map" in response_type:
        graph_type_prompt = f"Determine the best-suited graph type for the following sentence: {sentence}.CSV file Schema{CsvSchema}. Table metadata: {relevant_metadata}, Table name: {table_name}. If PreferredVisualizationType is not empty, strictly select the one given in the metadata. Provide only the graph type."
        graph_response = model.generate_content(graph_type_prompt)
        graph_type = graph_response.text.lower()  # Ensure graph type is in lowercase
        print(graph_type)
        
        # Normalize graph types to Grafana types
        if "bar" in graph_type:
            graph_type = "barchart"
        elif "line" in graph_type:
            graph_type = "timeseries"
        elif "scatter" in graph_type:
            graph_type = "xychart"
        elif "time" in graph_type:
            graph_type = "timeseries"
        elif "pie" in graph_type:
            graph_type = "piechart"
        elif "heat" in graph_type:
            graph_type = "heatmap"
        elif "histogram" in graph_type:
            graph_type = "histogram"
        elif "gauge" in graph_type:
            graph_type = "gauge"
        elif "stat" in graph_type:
            graph_type = "stat"
        elif "map" in graph_type:
            graph_type = "geomap"
        else:
            graph_type = "barchart"  
        print("Chosen graph type:", graph_type)

        prompt = f"""
                Translate the following sentence into a PostgreSQL query which can be displayed in {graph_type}: {sentence}. CSV file Schema{CsvSchema}
                Table metadata: {relevant_metadata}, Table name: {table_name}. Provide only the raw SQL query.
                
                Guidelines:
                Guidelines:
                    - If the graphType is 'timeseries', name at least one field as 'time'. Convert dates from DD-MM-YYYY format using TO_DATE.
                    - If the graphType is 'XYchart' or 'scatter plot':
                        * If both X and Y axes are numerical fields based on the sentence, use the fields directly.
                        * Otherwise, map non-numerical fields to numeric indices using ROW_NUMBER() or a similar function.
                    - For 'bar chart' and 'pie chart', group by categorical fields and use aggregate functions such as COUNT, SUM, or AVG as needed.
                        * Ensure that categorical fields are cast to string (varchar) if they are numeric for proper bar chart display in Grafana.
                        * For bar charts, include at least one string (categorical) field or a static label in the query to categorize the data on the x-axis.
                            Example for bar chart with a static label:
                                select 'Average DPD' as label, avg(total_dpd_for_gold_loans_in_last_2_years) as average_total_dpd_for_gold_loans_in_last_2_years from applicantsdata_final;
                    - Ensure that the query format aligns with the graphType and appropriately handles the specified sentence.
                    - Use JOIN operations where necessary to map categorical fields to numeric indices.
                    - If a percentage value is stored as text in the format '90%', remove the '%' symbol and convert the text to numeric before performing any calculations.
                """

    else:
        graph_type = None
        prompt = f"""
                Translate the following sentence into a PostgreSQL query which can be displayed in a table: {sentence}.Provide only the raw SQL query .CSV file Schema{CsvSchema}. Table metadata: {relevant_metadata}, Table name: {table_name}. 
                Guidelines:
                - Ensure the query format aligns with the specified sentence and the table structure.
                - Use appropriate JOIN operations if necessary to combine data from multiple tables.
                - If a percentage value is stored as text in the format '90%', remove the '%' symbol and convert the text to numeric before performing any calculations.
                - Filter out NULL values and empty strings (e.g., '') for percentage fields before converting them to numeric in the WHERE clause.
                - Apply necessary filters and conditions to accurately reflect the sentence.
                """
    
    response = model.generate_content(prompt)
    sql_query = extract_sql_query(response.text.lower())
    print(sql_query)

    return {"sql_query": sql_query, "response_type": response_type, "graph_type": graph_type}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
