import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

from deep_translator import GoogleTranslator
# Initialize Google Generative AI

app = FastAPI()

llm = ChatGoogleGenerativeAI(model="gemini-pro")

# Initialize memory and tools
memory = ConversationBufferMemory(memory_key="chat_history")
tools = load_tools(["ddg-search"], llm=llm, description="add value on you answer",)

# Define agent executor initialization function
def initialize_agent_executor():
    # Initialize agent executor
    agent_executor = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
    # Clear memory
    memory.clear()
    return agent_executor

class Question(BaseModel):
    fbid: str
    question: str

@app.post("/generate/")
async def generate_response(question: Question):
    try:
        # Initialize agent executor and clear memory
        agent_executor = initialize_agent_executor()
        # Invoke agent with input from the request
        response = agent_executor.invoke({"input": question.question})

        return {"response_genaiput": response['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
  uvicorn.run(app, port=7000)
