from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Echo-Modul")

class EchoInput(BaseModel):
    input: str

@app.post("/echo")
def echo(input: EchoInput):
    return {"output": input.input}
