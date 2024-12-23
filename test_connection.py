import json
import ssl
import requests
import websockets
import asyncio
import os
import hashlib
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from app.utils.encryption import Encryption

working_dir = os.getcwd()

# Paths for certificates
server_path = os.path.join(working_dir, "Certificates/Server")
client_path = os.path.join(working_dir, "Certificates/Client")
hacker_client_path = os.path.join(working_dir, "Certificates/Client from Hacker")


# Function to generate client ID from certificate
def generate_client_id(cert_path):
    with open(cert_path, "rb") as cert_file:
        cert_data = cert_file.read()
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    public_key = cert.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    fingerprint = hashlib.sha256(public_key).hexdigest()
    return fingerprint[:16]


# Test with valid client certificate for HTTPS
try:
    print("Testing valid client certificate for HTTPS...")
    response = requests.get(
        "https://127.0.0.1:8000",
        verify=os.path.join(server_path, "fullchain.pem"),
        cert=(
            os.path.join(client_path, "certificate.crt"),
            os.path.join(client_path, "private.key"),
        ),
    )
    print("Response:", response.status_code, response.text)
except requests.exceptions.ConnectionError as e:
    print("Connection failed with valid client certificate:", e)

# Test with invalid client certificate for HTTPS
try:
    print("\nTesting invalid client certificate for HTTPS...")
    response = requests.get(
        "https://127.0.0.1:8000",
        verify=os.path.join(server_path, "fullchain.pem"),
        cert=(
            os.path.join(hacker_client_path, "certificate.crt"),
            os.path.join(hacker_client_path, "private.key"),
        ),
    )
except requests.exceptions.ConnectionError as e:
    print("This has failed as expected:", e)


# Helper function to create an SSLContext
def create_ssl_context(certfile, keyfile, cafile):
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=cafile)
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    return ssl_context


# Async function to test WebSocket connection
async def test_websocket_connection(cert_path, key_path, description):
    client_id = generate_client_id(cert_path)
    print(f"Generated client ID: {client_id}")
    uri = f"wss://127.0.0.1:8000/ws/solver/{client_id}"  # Include client ID in the URI
    ssl_context = create_ssl_context(
        cert_path, key_path, os.path.join(server_path, "fullchain.pem")
    )
    try:
        print(f"\n{description}...")
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("WebSocket connection established!")
            enc = Encryption()
            testJson = json.dumps({"type": "ping", "data": {"message": "Hello, World!"}})
            
            await websocket.send(testJson)
            response = await websocket.recv()            
            # message = enc.decrypt(response)                      
            print("Response:", response)
    except Exception as e:
        print(f"WebSocket connection failed for {description}: {e}")


# Run WebSocket tests
async def main():
    await test_websocket_connection(
        os.path.join(hacker_client_path, "certificate.crt"),
        os.path.join(hacker_client_path, "private.key"),
        "Testing invalid client certificate for WebSocket",
    )
    await test_websocket_connection(
        os.path.join(client_path, "certificate.crt"),
        os.path.join(client_path, "private.key"),
        "Testing valid client certificate for WebSocket",
    )



# Run the main event loop
if __name__ == "__main__":
    asyncio.run(main())
