from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # =========================================================
    # MAIN PAGES
    # =========================================================
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
    path("offers/", views.offers, name="offers"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),

    # =========================================================
    # CATEGORY / SHOP PRODUCT PAGES
    # =========================================================
    path(
        "category/<int:sub_id>/",
        views.category_page,
        name="category_page"
    ),

    path(
        "shop/<slug:slug>/",
        views.category_slug_page,
        name="category_slug_page"
    ),

    path(
        "eyemakeup/",
        views.eyemakeup_page,
        name="eyemakeup"
    ),

    # =========================================================
    # CART
    # =========================================================
    path(
        "cart/",
        views.cart_page,
        name="cart"
    ),

    path(
        "product/<int:product_id>/",
        views.product_detail,
        name="product_detail"
    ),

    path(
        "add-to-cart/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "update-cart/<int:product_id>/",
        views.update_cart,
        name="update_cart"
    ),

    path(
        "remove-from-cart/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    # =========================================================
    # WISHLIST
    # =========================================================
    path(
        "wishlist/",
        views.wishlist_page,
        name="wishlist"
    ),

    path(
        "wishlist/toggle/<int:product_id>/",
        views.toggle_wishlist,
        name="toggle_wishlist"
    ),

    path(
        "add-to-wishlist/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),

    path(
        "remove-from-wishlist/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),

    # =========================================================
    # CHECKOUT / ORDER
    # =========================================================
    path(
        "checkout/",
        views.checkout_page,
        name="checkout"
    ),

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),

    # CASHFREE PAYMENT
path(
    "cashfree/return/<int:order_id>/",
    views.cashfree_payment_return,
    name="cashfree_return"
),

path(
    "cashfree/webhook/",
    views.cashfree_webhook,
    name="cashfree_webhook"
),

    # =========================================================
    # SUBSCRIBE
    # =========================================================
    path(
        "subscribe/",
        views.subscribe_user,
        name="subscribe_user"
    ),

    path("offers/add-to-cart/<int:offer_product_id>/", views.add_offer_to_cart, name="add_offer_to_cart"),
    path("offers/cart/update/<int:offer_product_id>/", views.update_offer_cart, name="update_offer_cart"),
    path("offers/cart/remove/<int:offer_product_id>/", views.remove_offer_from_cart, name="remove_offer_from_cart"),
    path(
    "offers/claim/<int:offer_id>/",
    views.claim_exclusive_offer,
    name="claim_exclusive_offer"
),
path("login/", views.login_view, name="login"),
path("register/", views.register_view, name="register"),
path("logout/", views.logout_view, name="logout"),
path("profile/", views.profile_view, name="profile"),

path("track-order/", views.track_order_from_contact, name="track_order_from_contact"),
path("track-order/<int:order_id>/", views.track_order, name="track_order"),
]
