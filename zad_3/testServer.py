from socket import gethostname
import FastAPI

app = FastAPI()

messages = {}

@app.get("/")
def status():
    return {"status": "OK"}

@app.get("/send")
def send_message(sender: str, recipient: str, message: str):
    if recipient in messages:
        messages[recipient].append((sender, message))
    else:
        messages[recipient] = [(sender, message)]
    return {"status": "OK"}

@app.get("/receive")
def receive_message(recipient: str):
    msgs_to_send = []
    if recipient in messages:
        for msg in messages[recipient]:
            msgs_to_send.append(f"You have a message from {msg[0]}: {msg[1]}")
        messages[recipient] = []
    return {"messages": msgs_to_send}


if __name__ == "__main__":
    from uvicorn import run
    run(app, host=gethostname(), port=8000)