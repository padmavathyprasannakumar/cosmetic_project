import json
import uuid
import requests
from decimal import Decimal
from types import SimpleNamespace

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q, Sum, Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

from .models import Order, OrderItem

from urllib.parse import quote_plus


from .payment_services import create_cashfree_order, cashfree_headers

from .models import (
    NavbarLink,
    SiteLogo,

    Category,
    Subcategory,

    Product,
    FeaturedProductSection,
    CartItem,
    WishlistItem,

    Banner,
    HomeContent,
    HomeFlashSaleSection,
    PerformanceSection,
    PerformanceIngredient,

    Brand,
    Color,
    DiscountOption,
    PriceRange,

    StoreSetting,
    ShippingMethod,
    PaymentMethod,

    SubscribeBanner,
    Subscriber,

    Order,
    OrderItem,

    AboutHero,
    AboutStorySection,
    AboutCoreValueSection,
    AboutFounderSection,
    AboutCommitmentSection,

    ContactHero,
    ContactServiceInfo,
    ContactMessage,
    ContactFAQSection,
    ContactFAQItem,

    TopCategorySection,
    TopCategoryCard,

    WhyGlowifySection,
    WhyGlowifyPoint,

    HappyCustomerSection,
    HappyCustomerReview,

    OfferBanner,
    OfferSection,
    OfferProduct,
    ExclusiveOffer,

    UserProfile
)

# =========================================================
# CASHFREE PAYMENT HELPERS
# =========================================================

def get_site_url(request):
    """
    Return site URL for Cashfree return_url / notify_url.
    Uses settings.SITE_URL if available, otherwise builds from request.
    """
    site_url = getattr(settings, "SITE_URL", "").strip()
    if site_url:
        return site_url.rstrip("/")
    return request.build_absolute_uri("/").rstrip("/")


def safe_reverse_url(primary_name, fallback_name=None, kwargs=None):
    """
    Try new Cashfree route name first.
    If urls.py is still using old PhonePe route names, fallback will still work.
    """
    kwargs = kwargs or {}

    try:
        return reverse(primary_name, kwargs=kwargs)
    except NoReverseMatch:
        if fallback_name:
            return reverse(fallback_name, kwargs=kwargs)
        raise


def is_cashfree_payment_method(payment_method):
    """
    Treat Cashfree as online payment.
    Also supports old admin data with code='phonepe' so your site does not jump to success.
    Please update admin PaymentMethod code to 'cashfree'.
    """
    if not payment_method:
        return False

    code = (payment_method.code or "").strip().lower()
    name = (payment_method.name or "").strip().lower()

    return (
        code in ["cashfree", "cashfree-pg", "cashfree_pg", "phonepe"]
        or "cashfree" in name
    )


def get_customer_email(request, order):
    if request.user.is_authenticated and request.user.email:
        return request.user.email

    posted_email = request.POST.get("email", "").strip()
    if posted_email:
        return posted_email

    return "customer@example.com"


def get_customer_name(order):
    full_name = f"{order.first_name} {order.last_name}".strip()
    return full_name or "Glowify Customer"


def create_cashfree_checkout_for_order(request, order):
    """
    Create Cashfree order from Django backend and return the Cashfree payment_session_id.
    """
    site_url = get_site_url(request)

    cashfree_order_id = f"GW{order.id}_{uuid.uuid4().hex[:10].upper()}"

    # Reusing existing model field to avoid new migration.
    # Later you can rename this field to cashfree_order_id in models.py.
    order.phonepe_merchant_order_id = cashfree_order_id
    order.payment_status = "pending"
    order.save(update_fields=["phonepe_merchant_order_id", "payment_status"])

    return_path = safe_reverse_url(
        "dashboard:cashfree_return",
        fallback_name="dashboard:phonepe_return",
        kwargs={"order_id": order.id},
    )

    webhook_path = safe_reverse_url(
        "dashboard:cashfree_webhook",
        fallback_name="dashboard:phonepe_webhook",
    )

    payload = {
        "order_id": cashfree_order_id,
        "order_amount": float(order.total),
        "order_currency": "INR",
        "customer_details": {
            "customer_id": str(request.user.id) if request.user.is_authenticated else f"guest_{order.id}",
            "customer_name": get_customer_name(order),
            "customer_email": get_customer_email(request, order),
            "customer_phone": order.mobile,
        },
        "order_meta": {
            "return_url": f"{site_url}{return_path}",
            "notify_url": f"{site_url}{webhook_path}",
        },
        "order_note": f"Glowify order #{order.id}",
    }

    data = create_cashfree_order(payload)

    payment_session_id = data.get("payment_session_id")

    if not payment_session_id:
        order.payment_status = "failed"
        order.phonepe_response = json.dumps(data, indent=2)
        order.save(update_fields=["payment_status", "phonepe_response"])
        raise Exception(data.get("message") or data.get("error") or f"Cashfree order creation failed: {data}")

    order.phonepe_response = json.dumps(data, indent=2)
    order.save(update_fields=["phonepe_response"])

    return payment_session_id


@require_POST
def cashfree_create_order(request):
    """
    Optional direct endpoint.
    Your main checkout_page below already creates the order and redirects to Cashfree.
    This endpoint is kept if you use a separate Pay button/form.
    """
    cart_details = get_cart_details(request)

    if not cart_details["cart_items"]:
        messages.error(request, "Your cart is empty.")
        return redirect("dashboard:cart")

    shipping_cost = Decimal(request.POST.get("shipping_cost", "0") or "0")
    cart_details = get_cart_details(request, shipping_cost=shipping_cost)

    order = Order.objects.create(
        first_name=request.POST.get("first_name", "Glowify").strip(),
        last_name=request.POST.get("last_name", "Customer").strip(),
        mobile=request.POST.get("mobile", request.POST.get("mobile_no", "9999999999")).strip(),
        address=request.POST.get("address", "Customer Address").strip(),
        city=request.POST.get("city", "City").strip(),
        state=request.POST.get("state", "State").strip(),
        pin_code=request.POST.get("pin_code", "000000").strip(),
        subtotal=cart_details["subtotal"],
        offer_discount_total=cart_details["offer_discount_total"],
        shipping_cost=cart_details["estimated_shipping"],
        gst=cart_details["gst"],
        total=cart_details["total"],
        payment_status="pending",
    )

    create_order_items_from_cart(order, cart_details["cart_items"])

    try:
        payment_session_id = create_cashfree_checkout_for_order(request, order)
    except Exception as exc:
        messages.error(request, f"Cashfree payment could not start: {exc}")
        return redirect("dashboard:checkout")

    return render(
        request,
        "dashboard/cashfree_checkout.html",
        {
            "order": order,
            "payment_session_id": payment_session_id,
            "cashfree_mode": "production" if getattr(settings, "CASHFREE_ENV", "SANDBOX") == "PRODUCTION" else "sandbox",
        },
    )

def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # If your Order model has a status field, this will use it.
    # If not, it will default to "processing".
    current_status = getattr(order, "status", "processing") or "processing"

    status_order = [
        "ordered",
        "processing",
        "shipped",
        "out_for_delivery",
    ]

    status_messages = {
        "ordered": "Your order has been placed successfully.",
        "processing": "Your order is currently Packed, and ready to ship.",
        "shipped": "Your order has been shipped.",
        "out_for_delivery": "Your order is currently out for delivery and will reach you soon.",
    }

    if current_status not in status_order:
        current_status = "processing"

    current_index = status_order.index(current_status)
    completed_keys = status_order[:current_index + 1]

    tracking_steps = [
        {
            "key": "ordered",
            "label": "Ordered",
        },
        {
            "key": "processing",
            "label": "Processing",
        },
        {
            "key": "shipped",
            "label": "Shipped",
        },
        {
            "key": "out_for_delivery",
            "label": "Out for Delivery",
        },
    ]

    address_parts = [
        order.address,
        order.city,
        order.state,
        str(order.pin_code),
    ]
    full_address = ", ".join([part for part in address_parts if part])
    map_query = quote_plus(full_address)

    context = {
        "order": order,
        "tracking_steps": tracking_steps,
        "completed_keys": completed_keys,
        "current_status": current_status,
        "status_message": status_messages.get(current_status),
        "map_query": map_query,
    }

    return render(request, "dashboard/track_order.html", context)

def track_order_from_contact(request):
    order_id = request.session.get("last_order_id")

    if order_id:
        return redirect("dashboard:track_order", order_id=order_id)

    messages.info(request, "Please place an order first to track your order.")
    return redirect("dashboard:shop")


def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items__product"),
        id=order_id,
    )

    request.session["last_order_id"] = order.id
    request.session.modified = True

    order_items = order.items.all()

    customer_name = f"{order.first_name} {order.last_name}".strip()

    address_parts = []

    if order.address:
        address_parts.append(order.address)

    if order.city:
        address_parts.append(order.city)

    if order.state:
        address_parts.append(order.state)

    customer_address = ", ".join(address_parts)

    if order.pin_code:
        if customer_address:
            customer_address = f"{customer_address} - {order.pin_code}"
        else:
            customer_address = order.pin_code

    context = common_context(request)

    context.update({
        "order": order,
        "order_items": order_items,
        "order_number": order.order_number,
        "subtotal": order.subtotal,
        "shipping": order.shipping_cost,
        "gst": order.gst,
        "total": order.total,
        "customer_name": customer_name,
        "customer_address": customer_address,
        "customer_phone": order.mobile,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/order_success.html", context)

# =========================================================
# COMMON SESSION / OWNER HELPERS
# =========================================================

def get_session_key(request, create=True):
    if not request:
        return None

    if not hasattr(request, "session"):
        return None

    if create and not request.session.session_key:
        request.session.create()

    return request.session.session_key


def get_owner_lookup(request, create_session=True):
    if request.user.is_authenticated:
        return {
            "user": request.user,
        }

    session_key = get_session_key(
        request,
        create=create_session,
    )

    if not session_key:
        return {
            "pk__in": [],
        }

    return {
        "user__isnull": True,
        "session_key": session_key,
    }


def get_owner_create_kwargs(request, create_session=True):
    if request.user.is_authenticated:
        return {
            "user": request.user,
            "session_key": None,
        }

    session_key = get_session_key(
        request,
        create=create_session,
    )

    return {
        "user": None,
        "session_key": session_key,
    }


# =========================================================
# OFFER PRODUCT SESSION CART HELPERS
# This is for your existing small OfferProduct cards.
# ExclusiveOffer uses CartItem directly.
# =========================================================

def get_offer_cart(request):
    if not request or not hasattr(request, "session"):
        return {}

    return request.session.get("offer_cart", {})


def save_offer_cart(request, offer_cart):
    request.session["offer_cart"] = offer_cart
    request.session.modified = True


def get_offer_cart_count(request):
    offer_cart = get_offer_cart(request)

    total = 0

    for quantity in offer_cart.values():
        try:
            total += int(quantity)
        except (TypeError, ValueError):
            pass

    return total


def clear_offer_cart(request):
    if request and hasattr(request, "session"):
        request.session["offer_cart"] = {}
        request.session.modified = True


# =========================================================
# CART / WISHLIST QUERY HELPERS
# =========================================================

def get_cart_queryset(request):
    lookup = get_owner_lookup(
        request,
        create_session=False,
    )

    return (
        CartItem.objects
        .filter(**lookup)
        .select_related(
            "product",
            "product__brand",
            "product__page_item",
            "claimed_offer",
        )
    )


def get_wishlist_queryset(request):
    lookup = get_owner_lookup(
        request,
        create_session=False,
    )

    return (
        WishlistItem.objects
        .filter(**lookup)
        .select_related(
            "product",
            "product__brand",
            "product__page_item",
        )
    )


def get_cart_count(request):
    normal_total = (
        get_cart_queryset(request)
        .aggregate(total=Sum("quantity"))
        .get("total")
    ) or 0

    offer_total = get_offer_cart_count(request)

    return normal_total + offer_total


def get_wishlist_count(request):
    return get_wishlist_queryset(request).count()


def get_wishlist_product_ids(request):
    return list(
        get_wishlist_queryset(request)
        .values_list("product_id", flat=True)
    )


# =========================================================
# LOGIN MERGE HELPER
# Moves guest cart/wishlist into logged-in user account
# =========================================================

def merge_guest_data_to_user(request, user):
    session_key = request.session.session_key

    if not session_key:
        return

    guest_cart_items = CartItem.objects.filter(
        user__isnull=True,
        session_key=session_key,
    )

    for guest_item in guest_cart_items:
        user_cart_item = CartItem.objects.filter(
            user=user,
            product=guest_item.product,
        ).first()

        if user_cart_item:
            user_cart_item.quantity += guest_item.quantity

            if guest_item.is_offer_claimed:
                user_cart_item.claimed_offer = guest_item.claimed_offer
                user_cart_item.is_offer_claimed = True
                user_cart_item.voucher_code = guest_item.voucher_code
                user_cart_item.offer_price = guest_item.offer_price
                user_cart_item.original_price = guest_item.original_price

            user_cart_item.save()
            guest_item.delete()

        else:
            guest_item.user = user
            guest_item.session_key = None
            guest_item.save()

    guest_wishlist_items = WishlistItem.objects.filter(
        user__isnull=True,
        session_key=session_key,
    )

    for guest_item in guest_wishlist_items:
        exists = WishlistItem.objects.filter(
            user=user,
            product=guest_item.product,
        ).exists()

        if exists:
            guest_item.delete()
        else:
            guest_item.user = user
            guest_item.session_key = None
            guest_item.save()



# =========================================================
# AUTHENTICATION
# =========================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    next_url = request.GET.get("next") or request.POST.get("next") or reverse("dashboard:home")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()
        mobile = request.POST.get("mobile", "").strip()

        if not full_name or not email or not password:
            messages.error(request, "Please fill all required fields.")
            return redirect("dashboard:register")

        User = get_user_model()

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "This email is already registered. Please login.")
            return redirect("dashboard:login")

        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.full_name = full_name
        profile.mobile = mobile
        profile.save()

        auth_login(request, user)
        merge_guest_data_to_user(request, user)

        messages.success(request, f"Welcome {first_name}! Your profile has been created.")

        return redirect(next_url)

    context = common_context(request)
    context.update({
        "next": next_url,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/register.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    next_url = request.GET.get("next") or request.POST.get("next") or reverse("dashboard:home")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()
        remember_me = request.POST.get("remember_me")

        if not email or not password:
            messages.error(request, "Please enter email and password.")
            return redirect("dashboard:login")

        User = get_user_model()

        username = email

        try:
            user_obj = User.objects.get(email__iexact=email)
            username = user_obj.get_username()
        except User.DoesNotExist:
            pass

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(request, "Invalid email or password.")
            return redirect("dashboard:login")

        auth_login(request, user)
        merge_guest_data_to_user(request, user)

        if remember_me:
            request.session.set_expiry(1209600)
        else:
            request.session.set_expiry(0)

        messages.success(request, f"Welcome back {user.first_name or user.username}!")

        return redirect(next_url)

    context = common_context(request)
    context.update({
        "next": next_url,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/login.html", context)


def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("dashboard:login")


@login_required(login_url="dashboard:login")
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pin_code = request.POST.get("pin_code", "").strip()

        profile.full_name = full_name
        profile.mobile = mobile
        profile.address = address
        profile.city = city
        profile.state = state
        profile.pin_code = pin_code

        if request.FILES.get("profile_image"):
            profile.profile_image = request.FILES.get("profile_image")

        profile.save()

        if full_name:
            name_parts = full_name.split(" ", 1)
            request.user.first_name = name_parts[0]
            request.user.last_name = name_parts[1] if len(name_parts) > 1 else ""
            request.user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("dashboard:profile")

    context = common_context(request)
    context.update({
        "profile": profile,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/profile.html", context)

# =========================================================
# COMMON SITE CONTEXT
# =========================================================

def common_context(request=None):
    cart_count = 0
    wishlist_count = 0
    wishlist_product_ids = []

    if request is not None:
        cart_count = get_cart_count(request)
        wishlist_count = get_wishlist_count(request)
        wishlist_product_ids = get_wishlist_product_ids(request)

    category_heading = (
        Category.objects
        .filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "subcategories",
                queryset=Subcategory.objects.filter(
                    is_active=True
                ).order_by(
                    "order",
                    "id",
                )
            )
        )
        .order_by(
            "order",
            "id",
        )
        .first()
    )

    return {
        "navbar_links": NavbarLink.objects.filter(
            is_active=True
        ).order_by(
            "order",
            "id",
        ),

        "site_logo": SiteLogo.objects.filter(
            is_active=True
        ).last(),

        "category_heading": category_heading,
        "nav_category": category_heading,

        "cart_count": cart_count,
        "wishlist_count": wishlist_count,

        "cart_item_count": cart_count,
        "wishlist_item_count": wishlist_count,

        "wishlist_product_ids": wishlist_product_ids,
    }


# =========================================================
# GENERAL HELPERS
# =========================================================

def split_ids_and_slugs(values):
    ids = []
    slugs = []

    for value in values:
        value = str(value).strip()

        if value.isdigit():
            ids.append(value)
        elif value:
            slugs.append(value)

    return ids, slugs


def get_store_setting():
    return (
        StoreSetting.objects.filter(is_active=True).first()
        or StoreSetting.objects.first()
    )


def get_active_subscribe_banner():
    banner_with_image = (
        SubscribeBanner.objects
        .filter(is_active=True)
        .exclude(left_image="")
        .exclude(left_image__isnull=True)
        .order_by("-id")
        .first()
    )

    if banner_with_image:
        return banner_with_image

    return (
        SubscribeBanner.objects
        .filter(is_active=True)
        .order_by("-id")
        .first()
    )


def get_eyemakeup_page_item():
    return (
        Subcategory.objects
        .filter(
            Q(slug__iexact="eyemakeup") |
            Q(page_name__iexact="Eye Makeup") |
            Q(page_name__iexact="Eye Make Up") |
            Q(page_name__iexact="Eyemakeup") |
            Q(page_url__iexact="/eyemakeup/") |
            Q(page_url__iexact="eyemakeup/"),
            is_active=True,
        )
        .first()
    )


# =========================================================
# CART DETAILS / CHECKOUT HELPERS
# Supports:
# 1. Normal Product cart items.
# 2. ExclusiveOffer claimed items using CartItem.
# 3. Existing OfferProduct session cart items.
# =========================================================

def get_cart_details(request, shipping_cost=None):
    cart_items = []

    subtotal = Decimal("0.00")
    original_subtotal = Decimal("0.00")
    offer_discount_total = Decimal("0.00")
    count = 0

    normal_cart_items = (
        get_cart_queryset(request)
        .filter(product__is_active=True)
    )

    for item in normal_cart_items:
        product = item.product
        quantity = item.quantity

        unit_price = Decimal(str(item.unit_price))
        original_unit_price = Decimal(str(item.item_original_price))

        line_total = unit_price * quantity
        line_original_total = original_unit_price * quantity

        line_discount = Decimal("0.00")

        if item.is_offer_claimed:
            line_discount = line_original_total - line_total

        subtotal += line_total
        original_subtotal += line_original_total
        offer_discount_total += line_discount
        count += quantity

        cart_items.append(
            SimpleNamespace(
                product=product,
                quantity=quantity,

                unit_price=unit_price,
                original_unit_price=original_unit_price,

                line_total=line_total,
                line_original_total=line_original_total,
                line_discount=line_discount,

                is_offer=False,
                is_session_offer=False,

                is_offer_claimed=item.is_offer_claimed,
                is_exclusive_offer=item.is_offer_claimed,
                claimed_offer=item.claimed_offer,
                voucher_code=item.voucher_code,
                offer_label="Exclusive Offer" if item.is_offer_claimed else "",

                cart_item=item,
            )
        )

    offer_cart = get_offer_cart(request)
    offer_ids = []

    for offer_product_id in offer_cart.keys():
        if str(offer_product_id).isdigit():
            offer_ids.append(int(offer_product_id))

    offer_products = OfferProduct.objects.filter(
        id__in=offer_ids,
        is_active=True,
    )

    offer_product_map = {
        str(product.id): product
        for product in offer_products
    }

    for offer_product_id, quantity in offer_cart.items():
        offer_product = offer_product_map.get(str(offer_product_id))

        if not offer_product:
            continue

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        quantity = max(quantity, 1)

        unit_price = Decimal(str(offer_product.discounted_price))
        original_unit_price = Decimal(str(offer_product.original_price))

        line_total = unit_price * quantity
        line_original_total = original_unit_price * quantity
        line_discount = line_original_total - line_total

        subtotal += line_total
        original_subtotal += line_original_total
        offer_discount_total += line_discount
        count += quantity

        cart_items.append(
            SimpleNamespace(
                product=offer_product,
                quantity=quantity,

                unit_price=unit_price,
                original_unit_price=original_unit_price,

                line_total=line_total,
                line_original_total=line_original_total,
                line_discount=line_discount,

                is_offer=True,
                is_session_offer=True,

                is_offer_claimed=True,
                is_exclusive_offer=False,
                claimed_offer=None,
                voucher_code="",
                offer_label="Buy 1 Get 1 Free",

                cart_item=None,
            )
        )

    store_setting = get_store_setting()

    if cart_items and store_setting:
        default_shipping = Decimal(str(store_setting.estimated_shipping))
        gst = Decimal(str(store_setting.gst))
    else:
        default_shipping = Decimal("0.00")
        gst = Decimal("0.00")

    if shipping_cost is None:
        estimated_shipping = default_shipping
    else:
        estimated_shipping = Decimal(str(shipping_cost))

    if not cart_items:
        estimated_shipping = Decimal("0.00")
        gst = Decimal("0.00")

    total = subtotal + estimated_shipping + gst

    return {
        "cart_items": cart_items,
        "items": cart_items,

        "subtotal": subtotal,
        "original_subtotal": original_subtotal,
        "offer_discount_total": offer_discount_total,

        "estimated_shipping": estimated_shipping,
        "shipping": estimated_shipping,
        "gst": gst,
        "total": total,
        "count": count,
    }


def clear_cart(request):
    get_cart_queryset(request).delete()
    clear_offer_cart(request)


# =========================================================
# HOME PAGE
# =========================================================

def home(request):
    search_query = request.GET.get("q", "").strip()

    featured_section = FeaturedProductSection.objects.filter(
        is_active=True
    ).first()

    featured_products = (
        Product.objects
        .filter(
            is_active=True,
            is_featured=True,
        )
        .select_related(
            "brand",
            "page_item",
        )
        .prefetch_related(
            "colors",
            "discount_options",
        )
    )

    if search_query:
        featured_products = featured_products.filter(
            Q(name__icontains=search_query) |
            Q(shade_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query) |
            Q(colors__name__icontains=search_query) |
            Q(discount_options__label__icontains=search_query) |
            Q(page_item__page_name__icontains=search_query) |
            Q(page_item__heading__icontains=search_query)
        ).distinct()

    featured_products = featured_products.order_by(
        "order",
        "-created_at",
        "-id",
    )[:6]

    performance_section = PerformanceSection.objects.filter(
        is_active=True
    ).first()

    if performance_section:
        ingredients = PerformanceIngredient.objects.filter(
            Q(section=performance_section) | Q(section__isnull=True),
            is_active=True,
        ).order_by(
            "order",
            "id",
        )
    else:
        ingredients = PerformanceIngredient.objects.filter(
            is_active=True
        ).order_by(
            "order",
            "id",
        )

    top_category_section = TopCategorySection.objects.filter(
        is_active=True
    ).first()

    top_category_cards = TopCategoryCard.objects.filter(
        is_active=True
    ).select_related(
        "section",
        "category_page",
    )

    if top_category_section:
        top_category_cards = top_category_cards.filter(
            Q(section=top_category_section) |
            Q(section__isnull=True)
        )

    top_category_cards = top_category_cards.order_by(
        "order",
        "id",
    )

    why_glowify_section = WhyGlowifySection.objects.filter(
        is_active=True
    ).first()

    if why_glowify_section:
        why_glowify_points = why_glowify_section.points.filter(
            is_active=True
        ).order_by(
            "order",
            "id",
        )
    else:
        why_glowify_points = WhyGlowifyPoint.objects.none()

    happy_customer_section = HappyCustomerSection.objects.filter(
        is_active=True
    ).first()

    if happy_customer_section:
        happy_customer_reviews = happy_customer_section.reviews.filter(
            is_active=True
        ).order_by(
            "order",
            "id",
        )
    else:
        happy_customer_reviews = HappyCustomerReview.objects.none()

    subscribe_banner = get_active_subscribe_banner()

    flash_sale_section = HomeFlashSaleSection.objects.filter(
        is_active=True
    ).first()

    context = common_context(request)

    context.update({
        "banners": Banner.objects.filter(
            is_active=True
        ).order_by(
            "order",
            "id",
        ),

        "home_content": HomeContent.objects.filter(
            is_active=True
        ).first(),

        "performance_section": performance_section,
        "ingredients": ingredients,

        "top_category_section": top_category_section,
        "top_category_cards": top_category_cards,

        "featured_section": featured_section,
        "featured_products": featured_products,

        "subscribe_banner": subscribe_banner,

        "search_query": search_query,
        "search_placeholder": "Search products...",

        "why_glowify_section": why_glowify_section,
        "why_glowify_points": why_glowify_points,

        "happy_customer_section": happy_customer_section,
        "happy_customer_reviews": happy_customer_reviews,

        "flash_sale_section": flash_sale_section,
    })

    return render(request, "dashboard/home.html", context)


# =========================================================
# SHOP / CATEGORY / EYE MAKEUP PRODUCT LISTING
# =========================================================

def shop(request):
    return render_product_listing(
        request=request,
        page_item=None,
        template_name="dashboard/category_page.html",
        page_heading="Shop",
    )


def category_page(request, sub_id):
    page_item = get_object_or_404(
        Subcategory,
        id=sub_id,
        is_active=True,
    )

    return render_product_listing(
        request=request,
        page_item=page_item,
        template_name="dashboard/category_page.html",
        page_heading=page_item.heading or page_item.page_name,
    )


def category_slug_page(request, slug):
    page_item = get_object_or_404(
        Subcategory,
        slug=slug,
        is_active=True,
    )

    if page_item.slug and page_item.slug.lower() == "eyemakeup":
        template_name = "dashboard/eyemakeup.html"
    else:
        template_name = "dashboard/category_page.html"

    return render_product_listing(
        request=request,
        page_item=page_item,
        template_name=template_name,
        page_heading=page_item.heading or page_item.page_name,
    )


def eyemakeup_page(request):
    page_item = get_eyemakeup_page_item()

    if not page_item:
        search_query = request.GET.get("q", "").strip()
        sort_by = request.GET.get("sort", "")

        context = common_context(request)

        context.update({
            "page_item": None,
            "subcategory": None,
            "products": Product.objects.none(),

            "brands": Brand.objects.filter(is_active=True).order_by("name"),
            "colors": Color.objects.filter(is_active=True).order_by("name"),
            "discounts": DiscountOption.objects.filter(is_active=True).order_by("id"),
            "price_ranges": PriceRange.objects.filter(is_active=True).order_by("min_price", "id"),

            "selected_brands": request.GET.getlist("brand"),
            "selected_colors": request.GET.getlist("color"),
            "selected_discounts": request.GET.getlist("discount"),
            "selected_prices": request.GET.getlist("price"),

            "search_query": search_query,
            "sort_by": sort_by,
            "search_placeholder": "Search Eye Makeup...",
            "page_heading": "Eye Makeup",
            "page_error": "Please add Page Item: Eye Makeup with URL /eyemakeup/ in admin.",
            "subscribe_banner": get_active_subscribe_banner(),
        })

        return render(request, "dashboard/eyemakeup.html", context)

    return render_product_listing(
        request=request,
        page_item=page_item,
        template_name="dashboard/eyemakeup.html",
        page_heading=page_item.heading or "Eye Makeup",
    )


eyemakeup = eyemakeup_page


def render_product_listing(request, page_item, template_name, page_heading="Shop"):
    if page_item:
        products = Product.objects.filter(
            page_item=page_item,
            is_active=True,
        )
    else:
        products = Product.objects.filter(
            is_active=True,
        )

    products = (
        products
        .select_related(
            "brand",
            "page_item",
        )
        .prefetch_related(
            "colors",
            "discount_options",
        )
    )

    search_query = request.GET.get("q", "").strip()

    selected_brands = request.GET.getlist("brand")
    selected_colors = request.GET.getlist("color")
    selected_discounts = request.GET.getlist("discount")
    selected_prices = request.GET.getlist("price")
    sort_by = request.GET.get("sort", "")

    if search_query:
        search_terms = [term for term in search_query.split() if term]
        search_filter = Q()

        for term in search_terms:
            search_filter &= (
                Q(name__icontains=term) |
                Q(shade_name__icontains=term) |
                Q(description__icontains=term) |
                Q(tagline__icontains=term) |
                Q(how_to_use__icontains=term) |
                Q(benefits__icontains=term) |
                Q(brand__name__icontains=term) |
                Q(colors__name__icontains=term) |
                Q(colors__slug__icontains=term) |
                Q(discount_options__label__icontains=term) |
                Q(discount_options__slug__icontains=term) |
                Q(page_item__page_name__icontains=term) |
                Q(page_item__heading__icontains=term)
            )

        products = products.filter(search_filter)

    brand_ids, brand_slugs = split_ids_and_slugs(selected_brands)
    color_ids, color_slugs = split_ids_and_slugs(selected_colors)
    discount_ids, discount_slugs = split_ids_and_slugs(selected_discounts)
    price_ids, price_slugs = split_ids_and_slugs(selected_prices)

    if selected_brands:
        brand_query = Q()

        if brand_ids:
            brand_query |= Q(brand_id__in=brand_ids)

        if brand_slugs:
            brand_query |= Q(brand__slug__in=brand_slugs)

        products = products.filter(brand_query)

    if selected_colors:
        color_query = Q()

        if color_ids:
            color_query |= Q(colors__id__in=color_ids)

        if color_slugs:
            color_query |= Q(colors__slug__in=color_slugs)

        products = products.filter(color_query)

    if selected_discounts:
        discount_query = Q()

        if discount_ids:
            discount_query |= Q(discount_options__id__in=discount_ids)

        if discount_slugs:
            discount_query |= Q(discount_options__slug__in=discount_slugs)

        products = products.filter(discount_query)

    if selected_prices:
        price_range_query = Q()

        price_ranges_for_filter = PriceRange.objects.filter(
            is_active=True,
        )

        if price_ids and price_slugs:
            price_ranges_for_filter = price_ranges_for_filter.filter(
                Q(id__in=price_ids) |
                Q(slug__in=price_slugs)
            )
        elif price_ids:
            price_ranges_for_filter = price_ranges_for_filter.filter(
                id__in=price_ids
            )
        elif price_slugs:
            price_ranges_for_filter = price_ranges_for_filter.filter(
                slug__in=price_slugs
            )

        for price_range in price_ranges_for_filter:
            single_query = Q(
                price__gte=price_range.min_price,
            )

            if price_range.max_price is not None:
                single_query &= Q(
                    price__lte=price_range.max_price,
                )

            price_range_query |= single_query

        if price_range_query:
            products = products.filter(price_range_query)

    if sort_by in ["price_low", "price-low"]:
        products = products.order_by("price", "id")

    elif sort_by in ["price_high", "price-high"]:
        products = products.order_by("-price", "id")

    elif sort_by == "rating":
        products = products.order_by(
            "-rating",
            "-reviews_count",
            "id",
        )

    elif sort_by == "latest":
        products = products.order_by(
            "-created_at",
            "-id",
        )

    else:
        products = products.order_by(
            "order",
            "-created_at",
            "-id",
        )

    products = products.distinct()

    brands = Brand.objects.filter(
        is_active=True
    ).order_by(
        "name"
    )

    colors = Color.objects.filter(
        is_active=True
    ).order_by(
        "name"
    )

    discounts = DiscountOption.objects.filter(
        is_active=True
    ).order_by(
        "id"
    )

    price_ranges = PriceRange.objects.filter(
        is_active=True
    ).order_by(
        "min_price",
        "id",
    )

    context = common_context(request)

    context.update({
        "page_item": page_item,
        "subcategory": page_item,
        "products": products,

        "brands": brands,
        "colors": colors,
        "discounts": discounts,
        "price_ranges": price_ranges,

        "selected_brands": selected_brands,
        "selected_colors": selected_colors,
        "selected_discounts": selected_discounts,
        "selected_prices": selected_prices,

        "search_query": search_query,
        "sort_by": sort_by,

        "search_placeholder": (
            page_item.search_placeholder
            if page_item
            else "Search products..."
        ),

        "page_heading": page_heading,
        "subscribe_banner": get_active_subscribe_banner(),
        "wishlist_product_ids": get_wishlist_product_ids(request),
    })

    return render(request, template_name, context)




# =========================================================
# PRODUCT DETAIL PAGE
# =========================================================

def product_detail(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related("brand", "page_item").prefetch_related("colors", "discount_options"),
        id=product_id,
        is_active=True,
    )

    related_products = Product.objects.filter(is_active=True).exclude(id=product.id)

    if product.page_item_id:
        related_products = related_products.filter(page_item=product.page_item)

    related_products = related_products.select_related("brand", "page_item")[:4]

    context = common_context(request)
    context.update({
        "product": product,
        "related_products": related_products,
        "search_placeholder": "Search products...",
        "wishlist_product_ids": get_wishlist_product_ids(request),
    })

    return render(request, "dashboard/product_detail.html", context)

# =========================================================
# CART
# =========================================================

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    lookup = get_owner_lookup(
        request,
        create_session=True,
    )

    create_kwargs = get_owner_create_kwargs(
        request,
        create_session=True,
    )

    quantity = request.POST.get("quantity", 1)

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(quantity, 1)

    cart_item = CartItem.objects.filter(
        product=product,
        **lookup,
    ).first()

    if cart_item:
        cart_item.quantity += quantity
        cart_item.save()
    else:
        CartItem.objects.create(
            product=product,
            quantity=quantity,
            **create_kwargs,
        )

    messages.success(request, f"{product.name} added to cart.")

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:cart")


@require_POST
def claim_exclusive_offer(request, offer_id):
    exclusive_offer = get_object_or_404(
        ExclusiveOffer,
        id=offer_id,
        is_active=True,
        product__is_active=True,
    )

    product = exclusive_offer.product

    lookup = get_owner_lookup(
        request,
        create_session=True,
    )

    create_kwargs = get_owner_create_kwargs(
        request,
        create_session=True,
    )

    cart_item = CartItem.objects.filter(
        product=product,
        **lookup,
    ).first()

    if cart_item:
        cart_item.quantity += 1
        cart_item.claimed_offer = exclusive_offer
        cart_item.is_offer_claimed = True
        cart_item.voucher_code = exclusive_offer.voucher_code
        cart_item.offer_price = exclusive_offer.offer_price
        cart_item.original_price = exclusive_offer.original_price
        cart_item.save()
    else:
        CartItem.objects.create(
            product=product,
            quantity=1,
            claimed_offer=exclusive_offer,
            is_offer_claimed=True,
            voucher_code=exclusive_offer.voucher_code,
            offer_price=exclusive_offer.offer_price,
            original_price=exclusive_offer.original_price,
            **create_kwargs,
        )

    messages.success(
        request,
        f"Offer claimed! Voucher {exclusive_offer.voucher_code} applied for {product.name}."
    )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:cart")


claim_exclusive_offer_to_cart = claim_exclusive_offer


@require_POST
def add_offer_to_cart(request, offer_product_id):
    offer_product = get_object_or_404(
        OfferProduct,
        id=offer_product_id,
        is_active=True,
    )

    get_session_key(request, create=True)

    offer_cart = get_offer_cart(request)
    offer_product_id = str(offer_product.id)

    if offer_product_id in offer_cart:
        offer_cart[offer_product_id] += 1
    else:
        offer_cart[offer_product_id] = 1

    save_offer_cart(request, offer_cart)

    messages.success(request, f"{offer_product.image_name} added to cart.")

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:cart")


def cart_page(request):
    cart_details = get_cart_details(request)

    context = common_context(request)
    context.update(cart_details)

    context.update({
        "cart_details": cart_details,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/cart.html", context)


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
    )

    lookup = get_owner_lookup(
        request,
        create_session=False,
    )

    cart_item = CartItem.objects.filter(
        product=product,
        **lookup,
    ).first()

    action = request.POST.get("action")

    if cart_item:
        if action in ["increase", "plus"]:
            cart_item.quantity += 1
            cart_item.save()

        elif action in ["decrease", "minus"]:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

        elif action == "remove":
            cart_item.delete()

    return redirect("dashboard:cart")


@require_POST
def update_offer_cart(request, offer_product_id):
    offer_cart = get_offer_cart(request)
    offer_product_id = str(offer_product_id)
    action = request.POST.get("action")

    if offer_product_id in offer_cart:
        try:
            current_quantity = int(offer_cart[offer_product_id])
        except (TypeError, ValueError):
            current_quantity = 1

        if action in ["increase", "plus"]:
            offer_cart[offer_product_id] = current_quantity + 1

        elif action in ["decrease", "minus"]:
            current_quantity -= 1

            if current_quantity <= 0:
                del offer_cart[offer_product_id]
            else:
                offer_cart[offer_product_id] = current_quantity

        elif action == "remove":
            del offer_cart[offer_product_id]

    save_offer_cart(request, offer_cart)

    return redirect("dashboard:cart")


@require_POST
def remove_from_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
    )

    lookup = get_owner_lookup(
        request,
        create_session=False,
    )

    CartItem.objects.filter(
        product=product,
        **lookup,
    ).delete()

    messages.success(request, "Product removed from cart.")

    return redirect("dashboard:cart")


@require_POST
def remove_offer_from_cart(request, offer_product_id):
    offer_cart = get_offer_cart(request)
    offer_product_id = str(offer_product_id)

    if offer_product_id in offer_cart:
        del offer_cart[offer_product_id]

    save_offer_cart(request, offer_cart)

    messages.success(request, "Offer product removed from cart.")

    return redirect("dashboard:cart")


cart = cart_page


# =========================================================
# WISHLIST
# =========================================================

@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    lookup = get_owner_lookup(
        request,
        create_session=True,
    )

    create_kwargs = get_owner_create_kwargs(
        request,
        create_session=True,
    )

    wishlist_item = WishlistItem.objects.filter(
        product=product,
        **lookup,
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.info(request, f"{product.name} removed from wishlist.")
    else:
        WishlistItem.objects.create(
            product=product,
            **create_kwargs,
        )
        messages.success(request, f"{product.name} added to wishlist.")

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:wishlist")


@require_POST
def add_to_wishlist(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    lookup = get_owner_lookup(
        request,
        create_session=True,
    )

    create_kwargs = get_owner_create_kwargs(
        request,
        create_session=True,
    )

    wishlist_item = WishlistItem.objects.filter(
        product=product,
        **lookup,
    ).first()

    if not wishlist_item:
        WishlistItem.objects.create(
            product=product,
            **create_kwargs,
        )
        messages.success(request, f"{product.name} added to wishlist.")
    else:
        messages.info(request, f"{product.name} is already in wishlist.")

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:wishlist")


def wishlist_page(request):
    wishlist_items = get_wishlist_queryset(request)

    context = common_context(request)

    context.update({
        "wishlist_items": wishlist_items,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/wishlist.html", context)


@require_POST
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
    )

    lookup = get_owner_lookup(
        request,
        create_session=False,
    )

    WishlistItem.objects.filter(
        product=product,
        **lookup,
    ).delete()

    messages.success(request, "Product removed from wishlist.")

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("dashboard:wishlist")


wishlist = wishlist_page


# =========================================================
# CHECKOUT
# =========================================================



def create_order_items_from_cart(order, cart_items):
    for item in cart_items:
        product = item.product

        if item.is_session_offer:
            OrderItem.objects.create(
                order=order,
                product=None,
                title=product.image_name,
                shade_name=item.offer_label,
                price=item.unit_price,
                original_price=item.original_unit_price,
                quantity=item.quantity,
                line_total=item.line_total,
                discount_amount=item.line_discount,
                is_offer_item=True,
                voucher_code=item.voucher_code,
            )
        else:
            OrderItem.objects.create(
                order=order,
                product=product,
                title=product.name,
                shade_name=product.shade_name,
                price=item.unit_price,
                original_price=item.original_unit_price,
                quantity=item.quantity,
                line_total=item.line_total,
                discount_amount=item.line_discount,
                is_offer_item=item.is_offer_claimed,
                voucher_code=item.voucher_code,
            )

def checkout_page(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login or register to continue payment.")
        login_url = f"{reverse('dashboard:login')}?next={request.get_full_path()}"
        return redirect(login_url)

    cart_preview = get_cart_details(request)

    if not cart_preview["cart_items"]:
        return redirect("dashboard:cart")

    shipping_methods = ShippingMethod.objects.filter(
        is_active=True,
    ).order_by(
        "order",
        "id",
    )

    payment_methods = PaymentMethod.objects.filter(
        is_active=True,
    ).order_by(
        "order",
        "id",
    )

    default_shipping = (
        shipping_methods.filter(is_default=True).first()
        or shipping_methods.first()
    )

    selected_shipping = default_shipping

    if request.method == "POST":
        shipping_id = request.POST.get("shipping_method")
        payment_id = request.POST.get("payment_method")

        if shipping_id:
            selected_shipping = get_object_or_404(
                ShippingMethod,
                id=shipping_id,
                is_active=True,
            )

        selected_payment = None

        if payment_id:
            selected_payment = get_object_or_404(
                PaymentMethod,
                id=payment_id,
                is_active=True,
            )

        shipping_cost = (
            selected_shipping.cost
            if selected_shipping
            else Decimal("0.00")
        )

        cart_details = get_cart_details(
            request,
            shipping_cost=shipping_cost,
        )

        if not cart_details["cart_items"]:
            messages.error(request, "Your cart is empty.")
            return redirect("dashboard:cart")

        order = Order.objects.create(
            first_name=request.POST.get("first_name", "").strip(),
            last_name=request.POST.get("last_name", "").strip(),
            mobile=request.POST.get(
                "mobile",
                request.POST.get("mobile_no", "")
            ).strip(),
            address=request.POST.get("address", "").strip(),
            city=request.POST.get("city", "").strip(),
            state=request.POST.get("state", "").strip(),
            pin_code=request.POST.get("pin_code", "").strip(),

            shipping_method=selected_shipping,
            payment_method=selected_payment,

            subtotal=cart_details["subtotal"],
            offer_discount_total=cart_details["offer_discount_total"],
            shipping_cost=cart_details["estimated_shipping"],
            gst=cart_details["gst"],
            total=cart_details["total"],
            payment_status="pending",
        )

        create_order_items_from_cart(order, cart_details["cart_items"])

        # CASHFREE ONLINE PAYMENT
        # In admin, create Payment Method with code: cashfree
        # Old code='phonepe' is also supported temporarily.
        if is_cashfree_payment_method(selected_payment):
            try:
                payment_session_id = create_cashfree_checkout_for_order(request, order)

                return render(
                    request,
                    "dashboard/cashfree_checkout.html",
                    {
                        "order": order,
                        "payment_session_id": payment_session_id,
                        "cashfree_mode": "production" if getattr(settings, "CASHFREE_ENV", "SANDBOX") == "PRODUCTION" else "sandbox",
                    },
                )

            except Exception as exc:
                messages.error(request, f"Cashfree payment could not start: {exc}")
                return redirect("dashboard:checkout")

        # OTHER PAYMENT METHODS
        # Only non-online methods come here. This is why Cashfree code must be 'cashfree'.
        order.payment_status = "completed"
        order.status = "ordered"
        order.save(update_fields=["payment_status", "status"])

        clear_cart(request)

        messages.success(request, "Order placed successfully.")

        return redirect(
            "dashboard:order_success",
            order_id=order.id,
        )

    shipping_cost = (
        selected_shipping.cost
        if selected_shipping
        else Decimal("0.00")
    )

    cart_details = get_cart_details(
        request,
        shipping_cost=shipping_cost,
    )

    context = common_context(request)
    context.update(cart_details)

    context.update({
        "cart_details": cart_details,
        "shipping_methods": shipping_methods,
        "payment_methods": payment_methods,
        "selected_shipping": selected_shipping,
        "default_shipping": selected_shipping,
        "shipping_cost": cart_details["estimated_shipping"],
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/checkout.html", context)

checkout = checkout_page


# =========================================================
# CASHFREE PAYMENT RETURN / WEBHOOK
# =========================================================

def verify_cashfree_order_status(cashfree_order_id):
    response = requests.get(
        f"{settings.CASHFREE_BASE_URL}/orders/{cashfree_order_id}",
        headers=cashfree_headers(),
        timeout=30,
    )

    try:
        data = response.json()
    except ValueError:
        data = {
            "message": response.text,
        }

    if response.status_code != 200:
        raise Exception(data.get("message") or f"Cashfree verification failed: {data}")

    return data


def cashfree_payment_return(request, order_id):
    """
    Cashfree redirects customer here after payment.
    Never show success directly. First verify the Cashfree order from backend.
    """
    order = get_object_or_404(Order, id=order_id)

    cashfree_order_id = (
        order.phonepe_merchant_order_id
        or request.GET.get("order_id")
        or request.GET.get("cf_order_id")
    )

    if not cashfree_order_id:
        order.payment_status = "failed"
        order.save(update_fields=["payment_status"])
        messages.error(request, "Cashfree order reference is missing.")
        return redirect("dashboard:checkout")

    try:
        data = verify_cashfree_order_status(cashfree_order_id)

        order.phonepe_response = json.dumps(data, indent=2)
        order_status = data.get("order_status", "")

        if order_status == "PAID":
            order.payment_status = "completed"
            order.status = "ordered"
            order.save(update_fields=["payment_status", "status", "phonepe_response"])

            clear_cart(request)

            messages.success(request, "Cashfree payment completed successfully.")
            return redirect("dashboard:order_success", order_id=order.id)

        if order_status in ["EXPIRED", "TERMINATED", "CANCELLED", "FAILED"]:
            order.payment_status = "failed"
            order.save(update_fields=["payment_status", "phonepe_response"])

            messages.error(request, "Cashfree payment failed or was cancelled. Please try again.")
            return redirect("dashboard:checkout")

        order.payment_status = "pending"
        order.save(update_fields=["payment_status", "phonepe_response"])

        messages.info(request, f"Cashfree payment status is {order_status or 'pending'}. Please check again.")
        return redirect("dashboard:checkout")

    except Exception as exc:
        messages.error(request, f"Could not verify Cashfree payment: {exc}")
        return redirect("dashboard:checkout")


@csrf_exempt
def cashfree_webhook(request):
    """
    Cashfree server-to-server webhook.
    This updates the order after Cashfree sends payment event.
    For production, add signature verification as per your Cashfree dashboard/webhook secret.
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"status": "error", "detail": "Invalid JSON"}, status=400)

    try:
        data = payload.get("data", {})
        order_data = data.get("order", {})
        payment_data = data.get("payment", {})

        cashfree_order_id = (
            order_data.get("order_id")
            or payload.get("order_id")
            or payload.get("cf_order_id")
        )

        payment_status = (
            payment_data.get("payment_status")
            or order_data.get("order_status")
            or payload.get("payment_status")
        )

        if cashfree_order_id:
            order = Order.objects.filter(phonepe_merchant_order_id=cashfree_order_id).first()

            if order:
                order.phonepe_response = json.dumps(payload, indent=2)

                if payment_status in ["SUCCESS", "PAID"]:
                    order.payment_status = "completed"
                    order.status = "ordered"
                elif payment_status in ["FAILED", "CANCELLED", "EXPIRED"]:
                    order.payment_status = "failed"
                else:
                    order.payment_status = "pending"

                order.save(update_fields=["payment_status", "status", "phonepe_response"])

        return JsonResponse({"status": "ok"})

    except Exception as exc:
        return JsonResponse({"status": "error", "detail": str(exc)}, status=400)


# Backward-compatible aliases.
# These stop your current urls.py from breaking if it still uses old PhonePe route names.
phonepe_payment_return = cashfree_payment_return
phonepe_webhook = cashfree_webhook



# =========================================================
# SUBSCRIBE
# =========================================================

@require_POST
def subscribe_user(request):
    email = request.POST.get("email", "").strip()

    next_url = (
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or "/"
    )

    if not email:
        messages.error(request, "Please enter your email address.")
        return redirect(next_url)

    subscriber, created = Subscriber.objects.get_or_create(
        email=email,
    )

    if created:
        messages.success(request, "Email registered successfully.")
    else:
        messages.info(request, "This email is already registered.")

    return redirect(next_url)


# =========================================================
# ORDER SUCCESS
# =========================================================




# =========================================================
# ABOUT PAGE
# =========================================================

def about(request):
    about_hero = AboutHero.objects.filter(
        is_active=True,
    ).order_by(
        "-updated_at",
    ).first()

    about_story = AboutStorySection.objects.filter(
        is_active=True,
    ).order_by(
        "-updated_at",
    ).first()

    core_value_section = AboutCoreValueSection.objects.filter(
        is_active=True,
    ).order_by(
        "-updated_at",
    ).first()

    if core_value_section:
        core_value_cards = core_value_section.cards.filter(
            is_active=True,
        ).order_by(
            "order",
            "id",
        )
    else:
        core_value_cards = []

    founder_section = AboutFounderSection.objects.filter(
        is_active=True,
    ).order_by(
        "-updated_at",
    ).first()

    commitment_section = AboutCommitmentSection.objects.filter(
        is_active=True,
    ).order_by(
        "-updated_at",
    ).first()

    context = common_context(request)

    context.update({
        "about_hero": about_hero,
        "about_story": about_story,
        "core_value_section": core_value_section,
        "core_value_cards": core_value_cards,
        "founder_section": founder_section,
        "commitment_section": commitment_section,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/about.html", context)




# =========================================================
# CONTACT PAGE
# =========================================================

def contact(request):
    contact_hero = ContactHero.objects.filter(
        is_active=True,
    ).first()

    contact_service = ContactServiceInfo.objects.filter(
        is_active=True,
    ).first()

    faq_section = ContactFAQSection.objects.filter(
        is_active=True,
    ).first()

    if faq_section:
        faq_items = faq_section.faq_items.filter(
            is_active=True,
        ).order_by(
            "order",
            "id",
        )
    else:
        faq_items = ContactFAQItem.objects.filter(
            is_active=True,
            section__isnull=True,
        ).order_by(
            "order",
            "id",
        )

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        user_message = request.POST.get("message", "").strip()

        if not full_name or not email or not mobile or not user_message:
            messages.error(request, "Please fill all contact form fields.")
            return redirect("dashboard:contact")

        ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            mobile=mobile,
            message=user_message,
        )

        receiver_email = settings.CONTACT_RECEIVER_EMAIL

        if contact_service and contact_service.service_email:
            receiver_email = contact_service.service_email

        subject = f"New Contact Message from {full_name}"

        email_body = f"""
New contact message received from Glowify website.

Full Name: {full_name}
Email: {email}
Mobile No: {mobile}

Message:
{user_message}
"""

        try:
            if not settings.BREVO_API_KEY:
                raise Exception("BREVO_API_KEY is missing in Render Environment Variables")

            if not settings.BREVO_SENDER_EMAIL:
                raise Exception("BREVO_SENDER_EMAIL is missing in Render Environment Variables")

            payload = {
                "sender": {
                    "name": settings.BREVO_SENDER_NAME,
                    "email": settings.BREVO_SENDER_EMAIL,
                },
                "to": [
                    {
                        "email": receiver_email,
                    }
                ],
                "replyTo": {
                    "email": email,
                    "name": full_name,
                },
                "subject": subject,
                "textContent": email_body,
            }

            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "accept": "application/json",
                    "api-key": settings.BREVO_API_KEY,
                    "content-type": "application/json",
                },
                json=payload,
                timeout=15,
            )

            if response.status_code >= 300:
                raise Exception(f"Brevo error {response.status_code}: {response.text}")

            messages.success(request, "Your message has been sent successfully.")

        except Exception as e:
            print("Email sending error:", repr(e))

            messages.error(
                request,
                "Your message was saved, but email could not be sent. Please check email settings."
            )

        return redirect("dashboard:contact")

    context = common_context(request)

    context.update({
        "contact_hero": contact_hero,
        "contact_service": contact_service,
        "faq_section": faq_section,
        "faq_items": faq_items,
        "search_placeholder": "Search products...",
    })

    return render(request, "dashboard/contact.html", context)


# =========================================================
# OFFERS PAGE
# =========================================================

def offers(request):
    offer_banners = OfferBanner.objects.filter(
        is_active=True
    ).order_by(
        "order",
        "id",
    )

    offer_section = OfferSection.objects.filter(
        is_active=True
    ).first()

    offer_products = OfferProduct.objects.filter(
        is_active=True
    ).order_by(
        "order",
        "id",
    )[:3]

    exclusive_offers = (
        ExclusiveOffer.objects
        .filter(
            is_active=True,
            product__is_active=True,
        )
        .select_related(
            "product",
            "product__brand",
            "product__page_item",
        )
        .order_by(
            "order",
            "-created_at",
            "-id",
        )
    )

    context = common_context(request)

    context.update({
        "offer_banners": offer_banners,
        "offer_section": offer_section,
        "offer_products": offer_products,
        "exclusive_offers": exclusive_offers,
        "subscribe_banner": get_active_subscribe_banner(),
        "search_placeholder": "Search offers...",
    })

    return render(request, "dashboard/offers.html", context)
