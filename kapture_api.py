import requests

BASE_URL = "https://wakefituat.kapturecrm.com"

SECRET_KEY = "Kapture c1f8b2d03a4e4b6c9d5f7c1e2f8a3b6d"
CREATE_TICKET_AUTH = "Basic eGxpemxlcGRhc21jd3J3d3gzcm55em0xeXdtZW90c20wN3EybTZuNHN6azV1aXlleWY="
UPDATE_TICKET_AUTH = "Basic MnAycHFwMjY1ZHpraWM0dXN6dHZiMW14a2RlNXQ3aHY5dzZ3OHIzazR4OHF5MWY2b2Q="


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
