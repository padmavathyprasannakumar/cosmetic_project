# dashboard/utils.py

from decimal import Decimal, InvalidOperation

from .models import Product, StoreSetting


# =========================================================
# CART SESSION HELPERS
# =========================================================

def get_cart(request):
    """
    Cart will be stored in session like this:

    {
        "1": 2,
        "5": 1
    }

    This function also supports old cart format:

    {
        "1": {"quantity": 2}
    }
    """

    cart = request.session.get("cart", {})

    if not isinstance(cart, dict):
        cart = {}

    cleaned_cart = {}

    for product_id, value in cart.items():
        product_key = str(product_id)

        try:
            if isinstance(value, dict):
                quantity = int(value.get("quantity", 1))
            else:
                quantity = int(value)
        except (TypeError, ValueError):
            quantity = 1

        if quantity > 0 and product_key.isdigit():
            cleaned_cart[product_key] = quantity

    request.session["cart"] = cleaned_cart
    request.session.modified = True

    return cleaned_cart


def save_cart(request, cart):
    """
    Save cart to session after cleaning invalid data.
    """

    cleaned_cart = {}

    for product_id, quantity in cart.items():
        product_key = str(product_id)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity > 0 and product_key.isdigit():
            cleaned_cart[product_key] = quantity

    request.session["cart"] = cleaned_cart
    request.session.modified = True


def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True


def get_cart_count(request):
    cart = get_cart(request)
    return sum(cart.values())


# =========================================================
# CART ACTION HELPERS
# =========================================================

def add_product_to_cart(request, product_id, quantity=1):
    cart = get_cart(request)
    product_key = str(product_id)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(quantity, 1)

    cart[product_key] = cart.get(product_key, 0) + quantity

    save_cart(request, cart)


def increase_cart_item(request, product_id):
    cart = get_cart(request)
    product_key = str(product_id)

    if product_key in cart:
        cart[product_key] += 1

    save_cart(request, cart)


def decrease_cart_item(request, product_id):
    cart = get_cart(request)
    product_key = str(product_id)

    if product_key in cart:
        cart[product_key] -= 1

        if cart[product_key] <= 0:
            cart.pop(product_key)

    save_cart(request, cart)


def remove_cart_item(request, product_id):
    cart = get_cart(request)
    product_key = str(product_id)

    if product_key in cart:
        cart.pop(product_key)

    save_cart(request, cart)


# =========================================================
# STORE CHARGES
# =========================================================

def get_store_setting():
    """
    Get active store setting first.
    If no active setting exists, get first setting.
    """

    return (
        StoreSetting.objects.filter(is_active=True).first()
        or StoreSetting.objects.first()
    )


def get_store_charges(has_items=True):
    """
    Returns estimated shipping and GST from admin.

    If cart is empty, return 0 shipping and 0 GST.
    """

    if not has_items:
        return Decimal("0.00"), Decimal("0.00")

    setting = get_store_setting()

    if setting:
        return setting.estimated_shipping, setting.gst

    return Decimal("0.00"), Decimal("0.00")


def decimal_value(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0.00")


# =========================================================
# CART DETAILS
# =========================================================

def get_cart_details(request, shipping_cost=None):
    """
    Returns full cart details for cart page and checkout page.

    Returns both naming styles:
    - cart_items and items
    - estimated_shipping and shipping

    So your cart.html, checkout.html, and old views can all work.
    """

    cart = get_cart(request)

    product_ids = []

    for product_id in cart.keys():
        if str(product_id).isdigit():
            product_ids.append(int(product_id))

    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True
    ).select_related(
        "brand",
        "page_item"
    ).prefetch_related(
        "colors",
        "discount_options"
    )

    product_map = {
        str(product.id): product
        for product in products
    }

    cart_items = []
    subtotal = Decimal("0.00")

    for product_id, quantity in cart.items():
        product = product_map.get(str(product_id))

        if not product:
            continue

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        quantity = max(quantity, 1)

        line_total = product.price * quantity
        subtotal += line_total

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "line_total": line_total,
        })

    has_items = bool(cart_items)

    default_shipping, gst = get_store_charges(has_items=has_items)

    if shipping_cost is None:
        final_shipping = default_shipping
    else:
        final_shipping = decimal_value(shipping_cost)

    if not has_items:
        final_shipping = Decimal("0.00")
        gst = Decimal("0.00")

    total = subtotal + final_shipping + gst

    return {
        # New template-friendly names
        "cart_items": cart_items,
        "subtotal": subtotal,
        "estimated_shipping": final_shipping,
        "gst": gst,
        "total": total,

        # Old compatibility names
        "items": cart_items,
        "shipping": final_shipping,

        # Extra useful values
        "count": sum(item["quantity"] for item in cart_items),
        "item_count": len(cart_items),
    }
