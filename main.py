from fastapi import FastAPI
import pandas as pd
from typing import Dict, List

import os

# File ka dynamic path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "UrduTranslationsFatehMuhammadAndShaikhulHind.xlsx")

# Read Excel file
df = pd.read_excel(file_path)
# Initialize FastAPI app
app = FastAPI()

# Base route (default route)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Quran Data API!"}

# Route to get data by key (column)
@app.get("/get_data/{key}")
async def get_data_by_key(key: str):
    if key in df.columns:
        data = df[key].tolist()
        return {key: data}
    else:
        return {"error": "Key not found in the file"}

# Route to get data for a specific Sura ID and Aya No
@app.get("/get_sura_data/{sura_id}/{aya_no}")
async def get_sura_data(sura_id: int, aya_no: int):
    filtered_data = df[(df['SuraID'] == sura_id) & (df['AyaNo'] == aya_no)]
    if not filtered_data.empty:
        return filtered_data.to_dict(orient='records')[0]
    else:
        return {"error": "Data not found for this SuraID and AyaNo"}

# Route to get all columns
@app.get("/all_columns")
async def get_all_columns():
    return {"columns": df.columns.tolist()}

# Route to fetch Surah Name (in English and Urdu)
@app.get("/get_surah_name/{sura_id}")
async def get_surah_name(sura_id: int):
    filtered_data = df[df['SuraID'] == sura_id]
    if not filtered_data.empty:
        surah_name = filtered_data.iloc[0][['SurahNameE', 'SurahNameU']]
        return {"SurahNameE": surah_name['SurahNameE'], "SurahNameU": surah_name['SurahNameU']}
    else:
        return {"error": "Surah not found for this SuraID"}

# Route to search Ayat containing a specific word/root
@app.get("/search_ayat/{word}")
async def search_ayat(word: str):
    filtered_data = df[df['Arabic Text'].str.contains(word, na=False)]
    if not filtered_data.empty:
        return {
            "count": len(filtered_data),
            "ayat": filtered_data[['SuraID', 'AyaNo', 'Arabic Text']].to_dict(orient='records')
        }
    else:
        return {"error": "No Ayat found containing the given word/root."}

# Route to fetch all translations for a specific Ayat
@app.get("/get_translations/{sura_id}/{aya_no}")
async def get_translations(sura_id: int, aya_no: int):
    filtered_data = df[(df['SuraID'] == sura_id) & (df['AyaNo'] == aya_no)]
    if not filtered_data.empty:
        return filtered_data[['Fateh Muhammad Jalandhri', 'Mehmood ul Hassan']].to_dict(orient='records')[0]
    else:
        return {"error": "No translations found for this SuraID and AyaNo"}

# Route to fetch all occurrences of a specific grammatical form (e.g., a verb form)
@app.get("/search_form/{form}")
async def search_form(form: str):
    filtered_data = df[df['Arabic Text'].str.contains(form, na=False)]
    if not filtered_data.empty:
        return {
            "count": len(filtered_data),
            "occurrences": filtered_data[['SuraID', 'AyaNo', 'Arabic Text']].to_dict(orient='records')
        }
    else:
        return {"error": "No occurrences found for the given form."}

# Route to fetch all Ayat or Ayat with translations for a specific Surah
@app.get("/get_surah_content/{sura_id}")
async def get_surah_content(sura_id: int, with_translation: bool = False):
    filtered_data = df[df['SuraID'] == sura_id]
    if not filtered_data.empty:
        if with_translation:
            return {
                "surah_content": filtered_data[['AyaNo', 'Arabic Text', 'Fateh Muhammad Jalandhri', 'Mehmood ul Hassan']].to_dict(orient='records')
            }
        else:
            return {
                "surah_content": filtered_data[['AyaNo', 'Arabic Text']].to_dict(orient='records')
            }
    else:
        return {"error": "Surah not found for this SuraID"}

# Route to fetch a range of Ayat within a specific Surah
@app.get("/get_surah_range/{sura_id}/{start_aya}/{end_aya}")
async def get_surah_range(sura_id: int, start_aya: int, end_aya: int, with_translation: bool = False):
    filtered_data = df[(df['SuraID'] == sura_id) & (df['AyaNo'] >= start_aya) & (df['AyaNo'] <= end_aya)]
    if not filtered_data.empty:
        if with_translation:
            return {
                "surah_range": filtered_data[['AyaNo', 'Arabic Text', 'Fateh Muhammad Jalandhri', 'Mehmood ul Hassan']].to_dict(orient='records')
            }
        else:
            return {
                "surah_range": filtered_data[['AyaNo', 'Arabic Text']].to_dict(orient='records')
            }
    else:
        return {"error": "No Ayat found for the given range in this Surah."}

# Route to get the total number of Ayat in a specific Surah
@app.get("/get_ayah_count/{sura_id}")
async def get_ayah_count(sura_id: int):
    filtered_data = df[df['SuraID'] == sura_id]
    if not filtered_data.empty:
        return {"sura_id": sura_id, "ayah_count": len(filtered_data)}
    else:
        return {"error": "Surah not found for this SuraID"}

# Route to list all available API endpoints
@app.get("/all_endpoints")
async def list_endpoints():
    return {
        "endpoints": [
            "/", "/get_data/{key}", "/get_sura_data/{sura_id}/{aya_no}", "/all_columns",
            "/get_surah_name/{sura_id}", "/search_ayat/{word}", "/get_translations/{sura_id}/{aya_no}", "/search_form/{form}", "/get_surah_content/{sura_id}", "/get_surah_range/{sura_id}/{start_aya}/{end_aya}", "/get_ayah_count/{sura_id}", "/all_endpoints"
        ]
    }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)