import requests
import json


def get_order_list(phone_number):
    print(phone_number)

    url = (
        f"https://industowers.int.kapturecrm.com/ms/order/list"
        f"?phone={phone_number}"
    )

    headers = {
        "Authorization": (
            "Basic NTd6azJzYmpvZjl0OXVhOW5qZ2RuOWQxaTF0NWVmbGJveDFucHozb3lsYW9scDdnZGg="
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        resp_json = response.json()

        raw_orders = resp_json.get("response", {}).get("orders", [])

        orders = []
        for order in raw_orders:
            orders.append({
                "affiliate_id": order.get("affiliate_id"),
                "cart_pid": order.get("cart_pid"),
                "product_name": order.get("product_info", {}).get("product_name"),
            })

        print(f"Status: {resp_json.get('status')}")
        print(orders)

        return {
            "orders": orders,
            "status": resp_json.get("status")
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }


def get_cart_details(affiliate_id, cart_id):
    print(affiliate_id)
    print(cart_id)

    url = (
        f"https://industowers.int.kapturecrm.com/ms/cart/details"
        f"?affiliateId={affiliate_id}&cartId={cart_id}"
    )

    headers = {
        "Authorization": (
            "Basic NTd6azJzYmpvZjl0OXVhOW5qZ2RuOWQxaTF0NWVmbGJveDFucHozb3lsYW9scDdnZGg="
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        resp_json = response.json()

        cartDetails = resp_json.get("response", {})

        print(f"Status: {resp_json.get('status')}")
        print(resp_json)
        print(cartDetails)

        return {
            "cartDetails": cartDetails,
            "status": resp_json.get("status")
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e)
        }
