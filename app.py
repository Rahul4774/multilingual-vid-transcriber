import os, time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from src.graphs.graphbuilder import GraphBuilder
from src.llms.groqllm import GroqModel, AudioToTextGroqModel
from src.models.routemodels import bloggenerationRequest, videotranscriptRequest
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/blog")
async def blog_generation(payload:bloggenerationRequest):
    topic = payload.topic
    language = payload.language
    chatmodel = GroqModel().get_model()
    model = AudioToTextGroqModel().get_model()
    graphBuilder = GraphBuilder(chatmodel,model)
    if topic and topic.strip() != "":
        graph = graphBuilder.setup_graph("blog")
        config = {"configurable":{"thread_id":str(time.time())}}
        res = graph.invoke({"topic": topic},config)
        graphBuilder.delete_memory(graph,config)
        json_response =jsonable_encoder(res)
        if json_response.get("error"):
            error = json_response.get("error")
            return JSONResponse(status_code=200, content={"status":error["status"], "message":error["message"], "text":error["error"]})
        return JSONResponse(status_code=200, content={"status":200, "message":"Success", "text":json_response})
    else:
        return JSONResponse(status_code=200, content={"status":400, "message":"Topic is required", "text":None})
    
@app.post("/videotranscript")
async def video_transcript(payload:videotranscriptRequest):
    user_input = payload.user_input
    print(user_input)
    chatmodel = GroqModel().get_model()
    model = AudioToTextGroqModel().get_model()
    graph_builder = GraphBuilder(chatmodel,model)
    if user_input and user_input.strip() != "":
        graph = graph_builder.setup_graph("transcript")
        config = {"configurable":{"thread_id":str(time.time())}}
        res = graph.invoke({"videoinput": user_input},config)
        graph_builder.delete_memory(graph,config)
        json_response =jsonable_encoder(res)
        if json_response.get("error"):
            error = json_response.get("error")
            return JSONResponse(status_code=200, content={"status":error["status"], "message":error["message"], "text":error["error"]})
        return JSONResponse(status_code=200, content={"status":200, "message":"Success", "text":json_response["finalarticle"]})
    else:
        return JSONResponse(status_code=200, content={"status":400, "message":"User input is required", "text":None})

def start_fastapi_service():
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)