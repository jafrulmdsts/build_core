from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI()

# Define a root endpoint with a GET operation
@app.get("/")
def read_root():
    return {"message": "Hello World"}