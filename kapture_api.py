import requests
import traceback
import ast
import json
import time
from datetime import datetime
from openai import OpenAI
from pymongo import MongoClient
from pydantic import BaseModel, Field

BASE_URL = "https://wakefituat.kapturecrm.com"

SECRET_KEY = "Kapture c1f8b2d03a4e4b6c9d5f7c1e2f8a3b6d"
CREATE_TICKET_AUTH = "Basic eGxpemxlcGRhc21jd3J3d3gzcm55em0xeXdtZW90c20wN3EybTZuNHN6azV1aXlleWY="
UPDATE_TICKET_AUTH = "Basic MnAycHFwMjY1ZHpraWM0dXN6dHZiMW14a2RlNXQ3aHY5dzZ3OHIzazR4OHF5MWY2b2Q="


def customFunction(phone: str, conversation_id: str, request_json: dict):
    """
    Pre-call entry point: calls the Customer API, then creates a Kapture ticket.

    Args:
        phone: Customer phone number (may be overridden from conversation_context).
        conversation_id: Conversation ID (may be overridden from conversation_context).
        request_json: Full request dict containing 'conversation_context' as a string.

    Returns:
        dict with 'conversation_id' and 'ticket_id'.
    """
    print(phone)
    conversation_context_str = request_json.get("conversation_context")
    conversation_context = ast.literal_eval(conversation_context_str)
    print(conversation_id)

    try:
        if not conversation_id:
            conversation_id = conversation_context.get("conversation_id") or ""
        print(f"conversation_id: {conversation_id}")
        if not phone:
            phone = conversation_context.get("data", {}).get("from_phone") or ""
        print(f"phone: {phone}")
    except Exception as e:
        print(f"\nError: {e}; \nTraceback: {traceback.format_exc()}")

    # FIX 2 (order) + FIX 3 (headers): Customer API is the pre-call step — call it first.
    # Only Content-Type is required; no 3X-Secret-Key or Authorization for this endpoint.
    customer_url = f"{BASE_URL}/ms/ticketcustomer/order/api/external/CUSTOMER"
    customer_headers = {"Content-Type": "application/json"}
    customer_payload = {
        "phone": phone,
        "email": "",
        "customerId": "",
        "otherDetail": {}  # FIX 5: removed misleading `"" or {}`
    }
    try:
        customer_response = requests.post(customer_url, headers=customer_headers, json=customer_payload, timeout=10)
        customer_response.raise_for_status()
        try:
            customer_data = customer_response.json()  # FIX 4: store result in a distinct variable
        except ValueError:
            customer_data = customer_response.text
        print(f"CustomerAPI response: {customer_data}")
    except Exception as e:
        print("Error:", str(e))
        raise

    try:
        ticket_payload = [
            {
                "title": "Voicebot",
                "ticket_details": "Voicebot_ticket",
                "due_date": "",
                "customer_id": "",
                "customer_name": "customer_name",
                "phone": phone,
                "email_id": "",
                "testing_object": [
                    {
                        "testing_2": "",
                        "testing_field_-1_": ""
                    }
                ],
                "resolution_disposition": [
                    {
                        "resolution_l1": "",
                        "resolution_l2": "",
                        "request_denied": ""
                    }
                ],
                "internal_order_details": [
                    {
                        "warranty": "",
                        "issue_category_1": "",
                        "issue_category_2": "",
                        "order_id": "order_id",
                        "product": "",
                        "type_of_logisitics": "",
                        "warehouse/3pl": "",
                        "order_source": "",
                        "affiliate_name": "",
                        "request_denied": "",
                        "issue_type_(cet_routing)": "",
                        "product_type": "",
                        "product_category": "",
                        "request_accepted": "",
                        "\\": "",
                        "odr": "",
                        "affiliate_id": "",
                        "issue_type_(itp_routing)": ""
                    }
                ],
                "issue_category_details": [
                    {
                        "issue_category_1": "",
                        "issue_category_2": ""
                    }
                ]
            }
        ]
        ticket_url = f"{BASE_URL}/add-ticket-from-other-source.html/v.2.0"
        ticket_response = requests.post(
            ticket_url,
            json=ticket_payload,
            headers={
                "Authorization": CREATE_TICKET_AUTH,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        ticket_response.raise_for_status()
        ticket_data = ticket_response.json()
        print("Ticket Creation Response:", ticket_data)
        ticket_id = ticket_data.get("ticket_id")
        print("conv:", conversation_id)
        print("ticket_id:", ticket_id)
    except Exception as e:
        print("Error:", str(e))
        raise

    return {
        "conversation_id": conversation_id,
        "ticket_id": ticket_id
    }


def create_customer(phone: str, email: str = "", customer_id: str = "", other_detail: dict = None):
    """
    Create a customer in Kapture during a pre-call.
    No values are stored; used to initiate a customer session.

    Args:
        phone: Customer mobile number.
        email: Customer email (optional).
        customer_id: Existing customer ID (optional).
        other_detail: Additional details dict (optional).

    Returns:
        Response JSON or raises on HTTP error.
    """
    url = f"{BASE_URL}/ms/ticketcustomer/order/api/external/CUSTOMER"
    headers = {"Content-Type": "application/json"}
    payload = {
        "phone": phone,
        "email": email,
        "customerId": customer_id,
        "otherDetail": other_detail if other_detail is not None else {}
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def get_order_list(phone: str, email: str = "", customer_id: str = "", other_detail: dict = None):
    """
    Get the list of orders for a customer.
    Store 'affiliate_id' and 'cart_pid' from the desired cart item
    to pass into get_cart_details().

    Args:
        phone: Customer mobile number.
        email: Customer email (optional).
        customer_id: Existing customer ID (optional).
        other_detail: Additional details dict (optional).

    Returns:
        Response JSON containing 'cart_items' list, or raises on HTTP error.
    """
    url = f"{BASE_URL}/ms/ticketcustomer/order/api/external/ORDER_LIST"
    headers = {
        "Content-Type": "application/json",
        "3X-Secret-Key": SECRET_KEY
    }
    payload = {
        "phone": phone,
        "email": email,
        "customerId": customer_id,
        "otherDetail": other_detail if other_detail is not None else {}
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def get_cart_details(affiliate_id: str, cart_id: str):
    """
    Get complete details for a specific order (cart).

    Args:
        affiliate_id: The affiliate_id from the order list (e.g. "0").
        cart_id: The cart_pid from the order list (e.g. "7101838").

    Returns:
        Response JSON with full order/cart details, or raises on HTTP error.
    """
    url = f"{BASE_URL}/ms/ticketcustomer/order/api/external/CART_DETAILS_API"
    headers = {
        "Content-Type": "application/json",
        "3X-Secret-Key": SECRET_KEY
    }
    payload = {
        "phone": "",
        "email": "",
        "customerId": "",
        "otherDetail": {
            "AFFILIATEID": str(affiliate_id),
            "CARTID": str(cart_id)
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def create_ticket(
    title: str = "",
    ticket_details: str = "",
    due_date: str = "",
    customer_id: str = "",
    customer_name: str = "",
    phone: str = "",
    email_id: str = "",
    testing_object: list = None,
    resolution_disposition: list = None,
    internal_order_details: list = None,
    issue_category_details: list = None
):
    """
    Create a new support ticket in Kapture.

    Args:
        title: Ticket title.
        ticket_details: Description of the issue.
        due_date: Due date string.
        customer_id: Kapture customer ID.
        customer_name: Customer full name.
        phone: Customer phone number.
        email_id: Customer email.
        testing_object: List of testing fields (optional).
        resolution_disposition: List with resolution_l1, resolution_l2, request_denied (optional).
        internal_order_details: List with order metadata fields (optional).
        issue_category_details: List with issue_category_1, issue_category_2 (optional).

    Returns:
        Response JSON or raises on HTTP error.
    """
    url = f"{BASE_URL}/add-ticket-from-other-source.html/v.2.0"
    headers = {
        "Content-Type": "application/json",
        "Authorization": CREATE_TICKET_AUTH
    }
    payload = [
        {
            "title": title,
            "ticket_details": ticket_details,
            "due_date": due_date,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "phone": phone,
            "email_id": email_id,
            "testing_object": testing_object if testing_object is not None else [{"testing_2": "", "testing_field_-1_": ""}],
            "resolution_disposition": resolution_disposition if resolution_disposition is not None else [{"resolution_l1": "", "resolution_l2": "", "request_denied": ""}],
            "internal_order_details": internal_order_details if internal_order_details is not None else [
                {
                    "warranty": "",
                    "issue_category_1": "",
                    "issue_category_2": "",
                    "order_id": "",
                    "product": "",
                    "type_of_logisitics": "",
                    "warehouse/3pl": "",
                    "order_source": "",
                    "affiliate_name": "",
                    "request_denied": "",
                    "issue_type_(cet_routing)": "",
                    "product_type": "",
                    "product_category": "",
                    "request_accepted": "",
                    "\\": "",
                    "odr": "",
                    "affiliate_id": "",
                    "issue_type_(itp_routing)": ""
                }
            ],
            "issue_category_details": issue_category_details if issue_category_details is not None else [{"issue_category_1": "", "issue_category_2": ""}]
        }
    ]
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def update_ticket(
    ticket_id: str,
    comment: str = "",
    callback_time: str = "",
    sub_status: str = "",
    queue: str = "",
    disposition: str = "",
    testing_object: list = None,
    resolution_disposition: list = None,
    internal_order_details: list = None,
    issue_category_details: list = None
):
    """
    Update an existing support ticket in Kapture.

    Args:
        ticket_id: The ID of the ticket to update (required).
        comment: Comment to add to the ticket.
        callback_time: Scheduled callback time string.
        sub_status: Sub-status value.
        queue: Queue to assign the ticket to.
        disposition: Disposition value.
        testing_object: List of testing fields (optional).
        resolution_disposition: List with resolution_l1, resolution_l2, request_denied (optional).
        internal_order_details: List with order metadata fields (optional).
        issue_category_details: List with issue_category_1, issue_category_2 (optional).

    Returns:
        Response JSON or raises on HTTP error.
    """
    url = f"{BASE_URL}/update-ticket-from-other-source.html/v.2.0"
    headers = {
        "Content-Type": "application/json",
        "Authorization": UPDATE_TICKET_AUTH
    }
    payload = [
        {
            "comment": comment,
            "ticket_id": ticket_id,
            "callback_time": callback_time,
            "sub_status": sub_status,
            "queue": queue,
            "disposition": disposition,
            "testing_object": testing_object if testing_object is not None else [{"testing_2": "", "testing_field_-1_": ""}],
            "resolution_disposition": resolution_disposition if resolution_disposition is not None else [{"resolution_l1": "", "resolution_l2": "", "request_denied": ""}],
            "internal_order_details": internal_order_details if internal_order_details is not None else [
                {
                    "warranty": "",
                    "issue_category_1": "",
                    "issue_category_2": "",
                    "order_id": "",
                    "product": "",
                    "type_of_logisitics": "",
                    "warehouse/3pl": "",
                    "order_source": "",
                    "affiliate_name": "",
                    "request_denied": "",
                    "issue_type_(cet_routing)": "",
                    "product_type": "",
                    "product_category": "",
                    "request_accepted": "",
                    "\\": "",
                    "odr": "",
                    "affiliate_id": "",
                    "issue_type_(itp_routing)": ""
                }
            ],
            "issue_category_details": issue_category_details if issue_category_details is not None else [{"issue_category_1": "", "issue_category_2": ""}]
        }
    ]
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def customFunction2(ticket_id: str, conversation_id: str, api_key: str, mongo_url: str):
    """
    Post-call handler: summarises the conversation via OpenAI, updates the Kapture
    ticket with the summary, and uploads the call recording URL.

    Args:
        ticket_id: Kapture ticket ID to update (required).
        conversation_id: Conversation ID used to look up MongoDB records.
        api_key: OpenAI API key.
        mongo_url: MongoDB connection string.
    """
    if not ticket_id:
        return {"error": "ticket_id cannot be empty"}

    # FIX 1: removed self-assignment `API_KEY = API_KEY` / `MONGO_URL = MONGO_URL`
    # (NameError); values are now passed as parameters.
    print("Ticketid:", ticket_id)
    print("Conversationid:", conversation_id)

    # === connect to MongoDB ===
    try:
        conn = MongoClient(mongo_url, maxIdleTimeMS=30000)
        db = conn["vb_platform"]
        be_tp = db["be_tp"]
        conversation_memory = db["conversation_memory_redefined"]
    except Exception as e:
        print(f"Error occured during connecting to DB; \nTraceback: {traceback.format_exc()}")
        return {"error": "Error occured during connecting to DB!"}

    # FIX 2: guard against find_one returning None
    record = conversation_memory.find_one({"conversation_id": conversation_id})
    if not record:
        print("\nConversation record not found!")
        return {"error": "conversation history not found!"}

    conversation_history = record.get("conversation_history", "")
    if not conversation_history:
        print("\nConversation history not found!")
        return {"error": "conversation history not found!"}

    formatted_conversation = ""
    for entry in conversation_history:
        role = entry['role'].capitalize()
        if role == "Agent":
            role = "Bot"
        content = entry['content']
        formatted_conversation += f"{role}: {content}\n"

    # === fetch recording URL with retries ===
    recording_url = ""
    max_retries = 10
    sleep_seconds = 15
    for attempt in range(max_retries):
        be_tp_obj = be_tp.find_one({"conversation_id": conversation_id})
        # FIX 3: guard against find_one returning None inside the retry loop
        if not be_tp_obj:
            print(f"\nbe_tp record not found. Retry {attempt+1}/{max_retries} ...")
            time.sleep(sleep_seconds)
            continue
        recording_url = be_tp_obj.get("recording_url", "")
        if recording_url and recording_url.strip() != "":
            print(f"\nRecording URL fetched successfully on attempt {attempt+1}: {recording_url}")
            break
        print(f"\nRecording URL empty. Retry {attempt+1}/{max_retries} ...")
        time.sleep(sleep_seconds)

    # FIX 3 (continued): guard after loop as well
    be_tp_obj = be_tp.find_one({"conversation_id": conversation_id})
    if not be_tp_obj:
        return {"error": "be_tp record not found for conversation_id"}

    client_id = be_tp_obj.get("client_id", "")
    config_id = be_tp_obj.get("config_id", "")
    to_phone = be_tp_obj.get("to_phone", "")
    from_phone = be_tp_obj.get("from_phone", "")
    start_time = be_tp_obj.get("start_time", "")
    end_time = be_tp_obj.get("end_time", "")
    call_status = be_tp_obj.get("status", "")

    try:
        print("\nstart_time: ", start_time, ", end_time: ", end_time)
        format_string = "%Y-%m-%d %H:%M:%S"
        if start_time and end_time:
            start_time_obj = datetime.strptime(start_time, format_string)
            end_time_obj = datetime.strptime(end_time, format_string)
            duration = (end_time_obj - start_time_obj).total_seconds()
            print("\nDuration: ", duration)
        else:
            duration = 1
            print("\nMissing start_time or end_time")
    except Exception as e:
        print("\nSome error occured during calculating duration")
        duration = 1

    # === OpenAI call ===
    class ResponseModel(BaseModel):
        call_summary: str = Field("NA", description="A concise summary of the call, highlighting the main points of the conversation in 2 to 3 lines.")

    prompt = f"""
You are a professional content extractor.
Your task is to extract structured insights from the given customer-bot conversation.
### Output Fields (STRICT):
- call_summary
call_summary:
- 2-3 concise lines
- Clearly describe the customer's issue and the bot's response
### Conversation:
{formatted_conversation}
"""
    openai_client = OpenAI(api_key=api_key)
    try:
        oai_response = openai_client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a structured information extractor."},
                {"role": "user", "content": prompt}
            ],
            response_format=ResponseModel,
            temperature=0.2
        )
        openai_output = json.loads(oai_response.choices[0].message.content)
        print("\nOpenAI response:\n", openai_output)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse GPT output")
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)}")

    # === update ticket ===
    # FIX 4: removed trailing `?=null` from URL
    update_url = f"{BASE_URL}/update-ticket-from-other-source.html/v.2.0"
    update_headers = {
        "Content-Type": "application/json",
        "Authorization": UPDATE_TICKET_AUTH
    }
    update_body = [
        {
            "comment": "voicebot-ticket",
            "ticket_id": ticket_id,
            "callback_time": "",
            "sub_status": "RS",
            "queue": "",
            "disposition": "",
            "testing_object": [
                {
                    "testing_2": "",
                    "testing_field_-1_": ""
                }
            ],
            "resolution_disposition": [
                {
                    "resolution_l1": openai_output.get("call_summary"),
                    "resolution_l2": "",
                    "request_denied": ""
                }
            ],
            "internal_order_details": [
                {
                    "warranty": "",
                    "issue_category_1": "",
                    "issue_category_2": "",
                    "order_id": "",
                    "product": "",
                    "type_of_logisitics": "",
                    "warehouse/3pl": "",
                    "order_source": "",
                    "affiliate_name": "",
                    "request_denied": "",
                    "issue_type_(cet_routing)": "",
                    "product_type": "",
                    "product_category": "",
                    "request_accepted": "",
                    "\\": "",
                    "odr": "",
                    "affiliate_id": "",
                    "issue_type_(itp_routing)": ""
                }
            ],
            "issue_category_details": [
                {
                    "issue_category_1": "",
                    "issue_category_2": ""
                }
            ]
        }
    ]
    print(f"\nTicket payload: {update_body}")
    update_response = requests.post(update_url, headers=update_headers, json=update_body)
    print("\nSTATUS:", update_response.status_code)
    try:
        print("RESPONSE:", update_response.json())
    except Exception:
        print("RAW RESPONSE:", update_response.text)

    # === upload recording URL ===
    try:
        emp_code = "VoiceBot Inbound"
        recording_upload_url = "https://wakefituat.kapturecrm.com/ms/ai-service/voice-bot/callback"
        recording_upload_auth = "Basic SUl3VFBJNm1tZ09KSjNadlhMaFVTZEVjMUQxMmtj"
        callback_headers = {
            "Content-Type": "application/json",
            "Authorization": recording_upload_auth
        }
        callback_payload = json.dumps({
            "ticketId": ticket_id,
            "ucid": f"@@{client_id}@@{config_id}@@{conversation_id}@@",
            "recording": recording_url,
            "duration": str(duration),
            "agentId": emp_code,
            "dialStatus": call_status,
            "from": from_phone,
            "to": to_phone,
            "callType": "Inbound",
            "callAgent": "VoiceBot",
        })
        print("\nPOSTING RECORDING URL")
        recording_response = requests.post(
            recording_upload_url,
            headers=callback_headers,
            data=callback_payload,
            timeout=10
        )
        if recording_response.status_code == 200:
            print("\nUploading voice recording url: Success")
            print("Upload Recording URL response:", recording_response.json())
        else:
            print("\nUploading voice recording url: Failed")
            print("Upload Recording URL response:", recording_response.json())
    except Exception as e:
        print(f"\nError: {e}")


def customFunction3(phone_number: str):
    """
    Fetch all orders for a customer by phone number.

    Returns a list of dicts with affiliate_id, cart_pid, and product_name,
    which can be passed into get_cart_details().

    Args:
        phone_number: Customer mobile number.

    Returns:
        dict with 'orders' list and 'status', or 'status'/'error' on failure.
    """
    url = f"{BASE_URL}/ms/ticketcustomer/order/api/external/ORDER_LIST"
    headers = {
        "Content-Type": "application/json",
        "3X-Secret-Key": SECRET_KEY
    }
    body = {
        "phone": phone_number,
        "email": "",
        "customerId": "",
        "otherDetail": {}
    }
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        resp_json = response.json()
        raw_orders = resp_json.get("cart_items", [])
        orders = []
        for order in raw_orders:
            orders.append({
                "affiliate_id": order.get("affiliate_id"),
                "cart_pid": order.get("cart_pid"),
                "product_name": order.get("product_info", {}).get("product_name"),
            })
        return {
            "orders": orders,
            "status": "success"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }


def customFunction4(affiliate_id, cart_id):
    """
    Fetch full details for a specific order (cart).

    Args:
        affiliate_id: affiliate_id from the order list (e.g. 0).
        cart_id: cart_pid from the order list (e.g. 7101838).

    Returns:
        dict with 'cartDetails' and 'status', or 'status'/'error' on failure.
    """
    # FIX 1: removed unused `import json` — requests handles JSON natively
    url = f"{BASE_URL}/ms/ticketcustomer/order/api/external/CART_DETAILS_API"
    headers = {
        "Content-Type": "application/json",
        "3X-Secret-Key": SECRET_KEY
    }
    body = {
        "phone": "",
        "email": "",
        "customerId": "",
        "otherDetail": {
            "AFFILIATEID": str(affiliate_id),
            "CARTID": str(cart_id)
        }
    }
    try:
        response = requests.post(url, headers=headers, json=body, timeout=30)
        response.raise_for_status()
        resp_json = response.json()
        return {
            "cartDetails": resp_json,
            "status": "success"
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }
