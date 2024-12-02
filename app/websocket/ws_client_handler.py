import asyncio
import json

from websockets import ConnectionClosedOK
from app.datasource.table_methods.client_table_manager import ClientTableManager
from app.helpers.process_message import process_message
from app.models.alice_tlp_data import AliceTLPData
from app.websocket.client import connect_ws_client
from app.websocket.ws_client_validation import validate_client_ip, validate_handshake
from app.datasource.db_manager import db_manager
from app.datasource.table_methods.task_table_manager import TaskTableManager
from app.datasource.table_methods.task_assignment_table import TaskAssignmentTableManager
from app.datasource.table_methods.complaints_table import ComplaintTableManager


db_path = "data/t3.db"


async def handle_client(websocket, path):
    """Handles communication with a single client."""
    client_info = websocket.remote_address
    client_details = await validate_client_ip(client_info)

    # if client_details is None:
    #     await websocket.close(reason="Client IP validation failed")

    #     return

    print(f"Client connected: {client_details}")

    try:
        await websocket.send(
            f"Hello from server! You are connected as {client_details}. Please send a valid handshake message to continue."
        )
        try:
            handshake_message = await asyncio.wait_for(websocket.recv(), timeout=60)

            print(
                f"Received handshake message from {client_details}: {handshake_message}"
            )
            validated_handshake = await validate_handshake(handshake_message)
            print(
                f"Validated handshake message from {client_details}: {validated_handshake}"
            )
            if validated_handshake == None:
                await websocket.send(f"Invalid handshake. Closing the connection")
                await websocket.close(reason=f"Invalid handshake")
                print(
                    f"Client {client_details} disconnected due to invalid handshake f{validated_handshake}"
                )
                return

        except asyncio.TimeoutError:
            print(
                f"No handshake message received from {client_details} within 30 seconds."
            )
            await websocket.send("Timeout. Closing the connection.")
            await websocket.close(reason="Timeout")
            return
        client_schema = ClientTableManager(db_manager)
        await client_schema.add_or_update_client_conn(key=validated_handshake)

        async for message in websocket:
            processed_message = process_message(message)
            if processed_message is None:
                await websocket.send("Invalid TLP message. Closing the connection.")
                await websocket.close(reason="Invalid TLP message")
                print(
                    f"Client {client_details} disconnected due to invalid TLP message"
                )
                return
            if(processed_message.__contains__("complain")):
                cmpJson = json.loads(processed_message)
                complainKey  = cmpJson['complain']
                print(f"COmplain key: {complainKey}")
                task_ass_schema = TaskAssignmentTableManager(db_manager)
                task_ass = await task_ass_schema.get_assignments_by_task(task_key=complainKey)
                tk = task_ass[0]
                solver_id = tk['solver_id']
                task_assignment_id = tk['task_id']
                print(f"VALUD sv{solver_id} tkid {task_assignment_id}")

                complain_schema = ComplaintTableManager(db_manager)
                await complain_schema.add_complaint(client_id=validated_handshake,solver_id=solver_id,task_assignment_id=task_assignment_id)
                return
            print(f"Received message from {client_details}: {processed_message}")
            await websocket.send(
                "TLP is being processed. You will receive a response once TLP is done."
            )

            alice_message = AliceTLPData.from_dict(json.loads(message))

            task_schema = TaskTableManager(db_manager)

            dif = calculate_difficulty(
                alice_message.product,
                alice_message.t,
                alice_message.baseg,
            )
            print(f"Difficulty: {dif}")

            task_key = await task_schema.add_task(
                parameter_t=alice_message.t,
                client_id=alice_message.fn,
                parameter_baseg=alice_message.baseg,
                parameter_product=alice_message.product,
                difficulty=dif,
            )
            to_send = {
                "product": alice_message.product,
                "t": alice_message.t,
                "baseg": alice_message.baseg,
            }
            to_send_json = json.dumps(to_send)

            # send message to processor server
            # start counter in seconds to update elapsed time
            response_from_patrick = await connect_ws_client(message=to_send_json)

            print(f"Received response from processor server: {response_from_patrick}")
            #
            # get last task_assignment by task_key
            print(f"Assignment data: {task_key}")
            # assignment_data = await TaskAssignmentTableManager(db_manager).get_assignments_by_task(task_key=task_key)
            # assignment_v = assignment_data[0]
            # print(f"Assignment data: {assignment_v}")
            res = {"mkey":task_key, "mdata":response_from_patrick}
            final_res = json.dumps(res)
            
            await websocket.send(final_res)
            # 

            #
    except ConnectionClosedOK:
        print(f"Client {client_details} disconnected")
    except Exception as e:
        print(f"Error with client {client_details}: {e}")


def calculate_difficulty(product, t, baseg):
    """
    Calculate the first two digits of the difficulty of a Time-Lock Puzzle (TLP).

    Args:
        product (str): The modulus (large prime number product as a string).
        t (str): The number of squarings (difficulty parameter, as a string).
        baseg (str): The base value (as a string).

    Returns:
        str: The first two digits of the result after modular squaring.
    """
    N = int(product)
    g = int(baseg)
    t = int(t)

    result = pow(g, pow(2, t), N)

    first_two_digits = str(result)[:3]

    return int(first_two_digits)
