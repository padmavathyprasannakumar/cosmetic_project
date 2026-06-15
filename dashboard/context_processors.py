# dashboard/context_processors.py

from django.db.models import Sum, Prefetch

from .models import (
    SiteLogo,
    NavbarLink,
    Category,
    Subcategory,
    CartItem,
    WishlistItem,

    FooterSetting, FooterLink, FooterSocialMedia
)


# =========================================================
# SESSION HELPER
# =========================================================

def get_session_key(request):
    """
    Returns current session key for guest users.
    Does not create a new session only for navbar count display.
    """

    if not request:
        return None

    if not hasattr(request, "session"):
        return None

    return request.session.session_key


# =========================================================
# CART COUNT HELPER
# =========================================================

def get_cart_count(request):
    """
    Shows total product quantity in navbar cart icon.

    Example:
    Product A quantity 2 + Product B quantity 1 = cart_count 3
    """

    if not request:
        return 0

    if request.user.is_authenticated:
        total = (
            CartItem.objects
            .filter(user=request.user)
            .aggregate(total=Sum("quantity"))
            .get("total")
        )

        return total or 0

    session_key = get_session_key(request)

    if not session_key:
        return 0

    total = (
        CartItem.objects
        .filter(
            user__isnull=True,
            session_key=session_key,
        )
        .aggregate(total=Sum("quantity"))
        .get("total")
    )

    return total or 0


# =========================================================
# WISHLIST COUNT HELPER
# =========================================================

def get_wishlist_count(request):
    """
    Shows total wishlist product count in navbar wishlist icon.
    """

    if not request:
        return 0

    if request.user.is_authenticated:
        return WishlistItem.objects.filter(
            user=request.user,
        ).count()

    session_key = get_session_key(request)

    if not session_key:
        return 0

    return WishlistItem.objects.filter(
        user__isnull=True,
        session_key=session_key,
    ).count()


# =========================================================
# WISHLIST PRODUCT IDS HELPER
# =========================================================

def get_wishlist_product_ids(request):
    """
    Returns product ids already added to wishlist.

    Used in eyemakeup.html and category_page.html to show
    active/filled heart icon beside Add to Cart button.
    """

    if not request:
        return []

    if request.user.is_authenticated:
        return list(
            WishlistItem.objects
            .filter(user=request.user)
            .values_list("product_id", flat=True)
        )

    session_key = get_session_key(request)

    if not session_key:
        return []

    return list(
        WishlistItem.objects
        .filter(
            user__isnull=True,
            session_key=session_key,
        )
        .values_list("product_id", flat=True)
    )


# =========================================================
# NAVBAR CATEGORY HELPER
# =========================================================

def get_nav_category():
    """
    Returns active Shop dropdown category with active page items only.

    Used in base.html:
    category_heading.heading
    category_heading.subcategories.all
    """

    return (
        Category.objects
        .filter(is_active=True)
        .prefetch_related(
            Prefetch(
                "subcategories",
                queryset=Subcategory.objects.filter(is_active=True).order_by("order", "id"),
            )
        )
        .order_by("order", "id")
        .first()
    )


# =========================================================
# GLOBAL SITE DATA
# Used automatically in base.html/navbar.
# Add this function in settings.py context_processors.
# =========================================================

def global_site_data(request):
    site_logo = (
        SiteLogo.objects
        .filter(is_active=True)
        .last()
    )

    navbar_links = (
        NavbarLink.objects
        .filter(is_active=True)
        .order_by("order", "id")
    )

    category_heading = get_nav_category()

    cart_count = get_cart_count(request)
    wishlist_count = get_wishlist_count(request)
    wishlist_product_ids = get_wishlist_product_ids(request)

    return {
        # Logo
        "site_logo": site_logo,

        # Navbar links
        "navbar_links": navbar_links,

        # Shop dropdown category
        "category_heading": category_heading,
        "nav_category": category_heading,

        # Navbar icon counts
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,

        # Extra aliases for old/new templates
        "cart_item_count": cart_count,
        "wishlist_item_count": wishlist_count,

        # Product wishlist active heart ids
        "wishlist_product_ids": wishlist_product_ids,
    }


# =========================================================
# BACKWARD COMPATIBILITY ALIASES
# These prevent errors if settings.py uses an older function name.
# =========================================================

def cart_wishlist_counts(request):
    return global_site_data(request)


def global_site_context(request):
    return global_site_data(request)


def footer_data(request):
    footer_setting = FooterSetting.objects.filter(is_active=True).first()

    footer_quick_links = FooterLink.objects.filter(
        section="quick_links",
        is_active=True
    ).order_by("display_order", "id")

    footer_support_links = FooterLink.objects.filter(
        section="support",
        is_active=True
    ).order_by("display_order", "id")

    footer_social_links = FooterSocialMedia.objects.filter(
        is_active=True
    ).order_by("display_order", "id")

    return {
        "footer_setting": footer_setting,
        "footer_quick_links": footer_quick_links,
        "footer_support_links": footer_support_links,
        "footer_social_links": footer_social_links,
    }