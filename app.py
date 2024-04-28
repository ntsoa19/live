import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from langchain_community.tools import DuckDuckGoSearchRun
app = FastAPI()

search = DuckDuckGoSearchRun()

class Query(BaseModel):
    query: str

@app.post("/search")
async def search_query(query: Query):
    result = search.run(query.query)
    return {"result": result}

class TranslationRequest(BaseModel):
  fbid: str
  text: str
  targetlanguage: str = 'en'

def translate_text(text: str, targetlanguage: str = 'en') -> str:
  try:
      translated_text = GoogleTranslator(source='auto', target=targetlanguage).translate(text)
      return translated_text
  except Exception as e:
      print("An error occurred:", e)
      raise HTTPException(status_code=500, detail="Failed to translate the text. Please try again later.")

@app.post("/translate/")
async def translate(request: TranslationRequest):
  translated_text = translate_text(request.text, request.targetlanguage)
  print("An ", request.targetlanguage)
  return {"response_genai": translated_text}
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=7000)
