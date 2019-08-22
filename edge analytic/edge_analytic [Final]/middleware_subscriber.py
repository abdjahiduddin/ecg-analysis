import ast
import threading
from datetime import datetime
from socketIO_client import SocketIO, LoggingNamespace
from cloud import authenticate_users, check_authentication, upload_data
from mongodb import connections

# Websocket frame identification
frame_id = {}


# Main process for middleware subscriber component
# Subscribe to heart rate data or health data in middleware
def main_process():
    try:
        authenticate_users()
        channel = "/ble/advertise/healthdata/*"
        websocket_client = SocketIO('localhost', 3000, LoggingNamespace)
        websocket_client.on("/r/" + channel, handle_websocket)
        websocket_client.emit('subscribe', channel)
        print("[Middleware Subscriber] Subscribed to Channel: " + channel)
        websocket_client.wait(seconds=600)
    except Exception as e:
        print("[Middleware Subscriber] Exited " + str(e))
        websocket_client.disconnect()
        exit(0)


# Handle data from websocket by thread
def handle_websocket(websocket_data):
    thread = threading.Thread(target=collect, args=(websocket_data,))
    thread.setDaemon(True)
    thread.start()


# Collect websocket data
def collect(websocket_data):
    # Convert unicode to list
    websocket_data = ast.literal_eval(websocket_data)

    print("[Middleware Subscriber] " + str(websocket_data) + " Received")
    if websocket_data[1] != "abcd":
        # Define frame label
        label = str(websocket_data[0]) + "(" + str(websocket_data[4]) + ")"
        # Check authentication
        auth_exist, age = check_authentication(label)
        # If authentication exist
        if auth_exist:
            # If frame sent by new user
            if label not in frame_id.keys():
                # Append user with device and define frame id by -1
                frame_id[label] = -1
                print("[Middleware Subscriber] Add " + (label) + " To List")

            # If different frame id
            if frame_id[label] != websocket_data[3]:
                # Renew frame id
                frame_id[label] = websocket_data[3]

                # Construct new data to dictionary
                new_data = {}
                new_data["username"] = websocket_data[0]
                new_data["activity"] = websocket_data[1]
                new_data["heart_rate"] = websocket_data[2]

                # Upload new data to cloud
                upload_data(label, new_data)
                print("[Middleware Subscriber] " + str(new_data) + " Sent to Cloud")

                # Add age, device's MAC address, time, and processed to new data
                new_data["age"] = age
                new_data["device"] = websocket_data[4]
                new_data["time"] = datetime.now()
                new_data["processed"] = False

                # Insert new data to raw collection
                connections["raw"].insert_one(new_data)
                print("[Middleware Subscriber] " + str(new_data) + " Saved to Collection: Raw")
            else:
                print("[Middleware Subscriber] Skip, Similar Frame Id")
        else:
            print("[Middleware Subscriber] Skip, Username " + label + " isn't Registered in MongoDB or Try Restart This")
    else:
        label = websocket_data[0] + "(" + websocket_data[2] + ")"
        if label in frame_id.keys():
            frame_id.pop(label)
            print("[Middleware Subscriber] Remove " + (label) + " From List, Final Frame Detected")
        else:
            print("[Middleware Subscriber] Skip, Another Final Frame")


if __name__ == "__main__":
    main_process()
