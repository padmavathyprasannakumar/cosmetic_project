from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.text import slugify
import uuid

class HomeFlashSaleSection(models.Model):
    title = models.CharField(max_length=100, default="Flash Sale")
    sale_text = models.CharField(max_length=100, default="50 % Off")
    quote_text = models.CharField(max_length=200, default="Glow Confidently every Day")
    button_text = models.CharField(max_length=50, default="Shop Now")

    left_image = models.ImageField(max_length=500, upload_to="home_flash_sale/", blank=True, null=True)
    right_image = models.ImageField(max_length=500, upload_to="home_flash_sale/", blank=True, null=True)

    # Use your existing category/page model here
    # Example:
    category_page = models.ForeignKey(
        "SubCategory",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="flash_sale_sections"
    )

    background_color = models.CharField(max_length=50, default="#f72585")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Home Flash Sale Section"
        verbose_name_plural = "Home Flash Sale Sections"

    def __str__(self):
        return self.title
    
# =========================================================
# NAVBAR
# =========================================================

class NavbarLink(models.Model):
    name = models.CharField(max_length=50)

    url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Example: /, /offers/, /about/, /contact/. Use # for Shop dropdown."
    )

    icon = models.ImageField(max_length=500, 
        upload_to="navbar_icons/",
        null=True,
        blank=True
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


# =========================================================
# CATEGORY / SHOP DROPDOWN / PAGE ITEMS
# =========================================================

class Category(models.Model):
    heading = models.CharField(
        max_length=100,
        default="Category",
        help_text="This heading appears inside the Shop dropdown."
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["order", "id"]

    def __str__(self):
        return self.heading


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category,
        related_name="subcategories",
        on_delete=models.CASCADE
    )

    page_name = models.CharField(
        max_length=100,
        help_text="Example: Eye Make Up, Skin Care, Lipsticks"
    )

    heading = models.CharField(
        max_length=100,
        blank=True,
        help_text="Page heading. Example: Eye Makeup"
    )

    slug = models.SlugField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        help_text="Example: eyemakeup, skincare, lipsticks"
    )

    page_url = models.CharField(
        max_length=255,
        blank=True,
        help_text="Auto generated if empty. Example: /eyemakeup/"
    )

    search_placeholder = models.CharField(
        max_length=100,
        default="Search products...",
        help_text="Navbar search placeholder for this page."
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Page Item"
        verbose_name_plural = "Page Items"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.page_name).replace("-", "") or "page"
            slug = base_slug
            counter = 1

            while Subcategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"

            self.slug = slug

        if not self.heading:
            self.heading = self.page_name

        if not self.page_url:
            self.page_url = f"/{self.slug}/"

        super().save(*args, **kwargs)

    def __str__(self):
        return self.page_name


# =========================================================
# SHOP FILTER MODELS
# =========================================================

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    hex_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Example: #ff3366"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DiscountOption(models.Model):
    label = models.CharField(
        max_length=100,
        help_text="Example: 10-20%, Buy 1 Get 1, Flat ₹100 Off"
    )

    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.label)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label


class PriceRange(models.Model):
    label = models.CharField(
        max_length=100,
        help_text="Example: ₹0 - ₹499"
    )

    slug = models.SlugField(unique=True, blank=True)

    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave empty for 'and above'. Example: ₹1,100 & Above"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["min_price", "id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.label)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.label


# =========================================================
# FEATURED PRODUCT SECTION HEADING
# =========================================================

class FeaturedProductSection(models.Model):
    heading = models.CharField(
        max_length=150,
        default="Featured Products"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Featured Product Section"
        verbose_name_plural = "Featured Product Section"

    def __str__(self):
        return self.heading


# =========================================================
# PRODUCT
# =========================================================

class Product(models.Model):
    BADGE_CHOICES = [
        ("best_seller", "Best Seller"),
        ("new", "New"),
        ("trending", "Trending"),
        ("hair_pick", "Hair Pick"),
        ("skin_loving", "Skin Loving"),
    ]

    page_item = models.ForeignKey(
        Subcategory,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        help_text="Select Page Item like Eye Make Up, Skin Care, Lipsticks."
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    colors = models.ManyToManyField(
        Color,
        blank=True,
        related_name="products",
        help_text="Select product colors for Color filter."
    )

    discount_options = models.ManyToManyField(
        DiscountOption,
        blank=True,
        related_name="products",
    )

    image = models.ImageField(max_length=500, 
        upload_to="products/",
        null=True,
        blank=True
    )

    name = models.CharField(max_length=150)

    shade_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Example: Rose Blush, Ruby Desire"
    )

    description = models.TextField(
        blank=True,
        default="",
        help_text="Full product description shown on the product detail page."
    )

    tagline = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Short bold sentence shown below the rating. Example: Luxury. Comfort. Timeless Color."
    )

    how_to_use = models.TextField(
        blank=True,
        default="",
        help_text="Steps or guidance for the How to Use tab on the product detail page."
    )

    benefits = models.TextField(
        blank=True,
        default="",
        help_text="One benefit per line. These lines appear in the Benefits tab."
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal("4.8")
    )

    reviews_count = models.PositiveIntegerField(default=214)

    badge = models.CharField(
        max_length=30,
        choices=BADGE_CHOICES,
        blank=True,
        null=True,
        help_text="Optional badge for home featured products."
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower number shows first."
    )

    is_active = models.BooleanField(default=True)

    is_featured = models.BooleanField(
        default=False,
        help_text="Turn on to show this product on home page Featured Products section."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at", "-id"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    @property
    def title(self):
        return self.name

    @property
    def review_count(self):
        return self.reviews_count

    @property
    def short_description(self):
        if self.description:
            return self.description[:55]
        return ""

    @property
    def display_tagline(self):
        if self.tagline:
            return self.tagline
        return "Luxury. Comfort. Timeless Glow."

    @property
    def display_description(self):
        if self.description:
            return self.description

        category_name = self.page_item.page_name if self.page_item else "beauty"
        brand_name = self.brand.name if self.brand else "Glowify"

        return (
            f"{brand_name} {self.name} is designed for daily {category_name.lower()} routines. "
            "It gives a soft, polished finish while keeping your look fresh and comfortable."
        )

    @property
    def display_how_to_use(self):
        if self.how_to_use:
            return self.how_to_use
        return (
            "1. Start with clean and dry skin.\n"
            "2. Apply a small amount evenly.\n"
            "3. Blend gently until smooth.\n"
            "4. Reapply when needed for a fresh finish."
        )

    @property
    def benefits_list(self):
        source = self.benefits or (
            "Deep hydration\n"
            "Smooth comfortable finish\n"
            "Soft glowing look\n"
            "Lightweight feel\n"
            "Suitable for daily beauty routines"
        )

        return [line.strip(" -•\t") for line in source.splitlines() if line.strip()]

    def __str__(self):
        return self.name


# =========================================================
# USER PROFILE
# =========================================================

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    wishlist = models.ManyToManyField(
        Product,
        blank=True,
        related_name="wishlisted_by_profiles"
    )

    cart = models.ManyToManyField(
        Product,
        related_name="cart_user_profiles",
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} Profile"


# =========================================================
# CART ITEM
# Supports normal products and exclusive claimed offer products.
# =========================================================

class CartItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    claimed_offer = models.ForeignKey(
        "ExclusiveOffer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items",
        help_text="If this cart item came from Claim This Offer, store that offer here."
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items"
    )

    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Used for guest users before login."
    )

    quantity = models.PositiveIntegerField(default=1)

    is_offer_claimed = models.BooleanField(
        default=False,
        help_text="True when user clicked Claim This Offer."
    )

    voucher_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Voucher code applied for this offer product."
    )

    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Offer price saved at claim time."
    )

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price saved at claim time."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=Q(user__isnull=False),
                name="unique_cart_product_per_user"
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"],
                condition=Q(user__isnull=True, session_key__isnull=False),
                name="unique_cart_product_per_guest"
            ),
        ]

    @property
    def unit_price(self):
        if self.is_offer_claimed and self.offer_price is not None:
            return self.offer_price
        return self.product.price

    @property
    def item_original_price(self):
        if self.is_offer_claimed and self.original_price is not None:
            return self.original_price
        return self.product.price

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def total_price(self):
        return self.line_total

    @property
    def line_original_total(self):
        return self.item_original_price * self.quantity

    @property
    def line_discount(self):
        if self.is_offer_claimed:
            return self.line_original_total - self.line_total
        return Decimal("0.00")

    def __str__(self):
        if self.is_offer_claimed:
            return f"{self.product.title} - Offer Claimed - Qty {self.quantity}"
        return f"{self.product.title} - Qty {self.quantity}"


# =========================================================
# WISHLIST ITEM
# =========================================================

class WishlistItem(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="wishlist_items"
    )

    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Used for guest users before login."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=Q(user__isnull=False),
                name="unique_wishlist_product_per_user"
            ),
            models.UniqueConstraint(
                fields=["session_key", "product"],
                condition=Q(user__isnull=True, session_key__isnull=False),
                name="unique_wishlist_product_per_guest"
            ),
        ]

    def __str__(self):
        return self.product.title


# =========================================================
# SITE LOGO
# =========================================================

class SiteLogo(models.Model):
    image = models.ImageField(max_length=500, 
        upload_to="site_logo/",
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "Site Logo"


# =========================================================
# BANNER
# =========================================================

class Banner(models.Model):
    image = models.ImageField(max_length=500, 
        upload_to="banners/",
        null=True,
        blank=True
    )

    button_text = models.CharField(
        max_length=100,
        default="Shop Now"
    )

    button_link = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Banner {self.id}"


# =========================================================
# HOME CONTENT
# =========================================================

class HomeContent(models.Model):
    heading = models.CharField(max_length=255)
    content_text = models.TextField()

    left_image = models.ImageField(max_length=500, upload_to="images/")
    right_image = models.ImageField(max_length=500, upload_to="images/")

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Home Content"
        verbose_name_plural = "Home Contents"

    def __str__(self):
        return self.heading


# =========================================================
# PERFORMANCE SECTION
# =========================================================

class PerformanceSection(models.Model):
    heading = models.CharField(
        max_length=200,
        default="Powered by Performance Ingredients"
    )

    autoplay_seconds = models.PositiveIntegerField(
        default=15,
        help_text="Time taken for one full auto-scroll loop"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.heading


class PerformanceIngredient(models.Model):
    section = models.ForeignKey(
        PerformanceSection,
        on_delete=models.CASCADE,
        related_name="ingredients",
        null=True,
        blank=True
    )

    image = models.ImageField(max_length=500, upload_to="performance_ingredients/")
    title = models.CharField(max_length=150)
    description = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


# =========================================================
# CART / CHECKOUT SETTINGS
# =========================================================

class StoreSetting(models.Model):
    name = models.CharField(
        max_length=100,
        default="Default Setting"
    )

    estimated_shipping = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("50.00")
    )

    gst = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("50.00")
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)

    subtitle = models.CharField(
        max_length=100,
        default="3-5 Business Day"
    )

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("50.00")
    )

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.name} - ₹{self.cost}"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)

    code = models.SlugField(
        unique=True,
        blank=True,
        help_text="Example: credit-card, net-banking, upi"
    )

    icon_image = models.ImageField(max_length=500, 
        upload_to="payment_icons/",
        null=True,
        blank=True,
        help_text="Upload payment icon image like Credit Card, Net Banking, UPI."
    )

    icon_text = models.CharField(
        max_length=20,
        blank=True,
        help_text="Optional fallback text/icon. Example: 💳"
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================================================
# ORDER
# =========================================================

class Order(models.Model):


    STATUS_CHOICES = (
        ("ordered", "Ordered"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="processing"
    )

    shipping_method = models.CharField(
        max_length=100,
        default="Standard Delivery (3-5 Business days)"
    )


    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)

    mobile = models.CharField(max_length=20)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=20)

    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )

    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending"
    )

    phonepe_merchant_order_id = models.CharField(
        max_length=63,
        unique=True,
        null=True,
        blank=True,
        help_text="Unique merchant order ID sent to PhonePe."
    )

    phonepe_transaction_id = models.CharField(
        max_length=120,
        blank=True,
        default=""
    )

    phonepe_response = models.TextField(
        blank=True,
        default="",
        help_text="Raw PhonePe status/callback response saved for debugging."
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    offer_discount_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total discount applied from claimed offers."
    )

    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    gst = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"Order #{self.id} - {self.first_name}"

    @property
    def mobile_no(self):
        return self.mobile
    
    @property
    def order_number(self):
        # format: YYYYMMDD + 6 random digits
        return f"{self.created_at.strftime('%Y%m%d')}{str(uuid.uuid4().int)[:6]}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)

    shade_name = models.CharField(
        max_length=120,
        blank=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Original price before offer discount."
    )

    quantity = models.PositiveIntegerField(default=1)

    line_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Discount amount for this item."
    )

    is_offer_item = models.BooleanField(
        default=False,
        help_text="True if this order item came from claimed offer."
    )

    voucher_code = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Voucher code used for this offer item."
    )

    def __str__(self):
        return self.title


# =========================================================
# SUBSCRIBE / BEAUTY CIRCLE BANNER
# Used on Home page and Category pages.
# Home page will not show image.
# Category pages will show left_image.
# =========================================================

class SubscribeBanner(models.Model):
    left_image = models.ImageField(max_length=500, 
        upload_to="subscribe_banner/",
        blank=True,
        null=True,
        help_text="Left side image for category page subscribe banner only."
    )

    heading = models.CharField(
        max_length=150,
        default="Join our Beauty Circle"
    )

    description = models.TextField(
        default="Be the first to know about new arrivals, exclusive discounts, and special flash sales."
    )

    email_placeholder = models.CharField(
        max_length=100,
        default="Enter You Email"
    )

    button_text = models.CharField(
        max_length=50,
        default="Register"
    )

    background_color = models.CharField(
        max_length=100,
        default="linear-gradient(135deg, #f58fba, #f72585)",
        help_text="Example: #F72585 or linear-gradient(135deg, #f58fba, #f72585)"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Subscribe Banner"
        verbose_name_plural = "Subscribe Banner"

    def __str__(self):
        return self.heading


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-subscribed_at"]
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return self.email

# =========================================================
# ABOUT PAGE
# =========================================================

class AboutHero(models.Model):
    title = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    subtitle = models.TextField(
        blank=True,
        null=True
    )

    background_image = models.ImageField(max_length=500, 
        upload_to="about/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Hero"
        verbose_name_plural = "About Heroes"

    def __str__(self):
        return self.title if self.title else "About Hero"


class AboutStorySection(models.Model):
    story_title = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    story_text = models.TextField(
        blank=True,
        null=True
    )

    mission_title = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    mission_text = models.TextField(
        blank=True,
        null=True
    )

    side_image = models.ImageField(max_length=500, 
        upload_to="about/story/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Story Section"
        verbose_name_plural = "About Story Sections"

    def __str__(self):
        return self.story_title if self.story_title else "About Story Section"


class AboutCoreValueSection(models.Model):
    heading = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Core Value Heading"
        verbose_name_plural = "About Core Value Headings"

    def __str__(self):
        return self.heading if self.heading else "About Core Values"


class AboutCoreValueCard(models.Model):
    section = models.ForeignKey(
        AboutCoreValueSection,
        on_delete=models.CASCADE,
        related_name="cards",
        blank=True,
        null=True
    )

    icon = models.ImageField(max_length=500, 
        upload_to="about/core-values/icons/",
        blank=True,
        null=True
    )

    title = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Core Value Card"
        verbose_name_plural = "About Core Value Cards"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title if self.title else "Core Value Card"


class AboutFounderSection(models.Model):
    image = models.ImageField(
        max_length=500,
        upload_to="about/founder/",
        blank=True,
        null=True,
        help_text="Upload founder image. Increased max_length to support long Cloudinary file paths."
    )

    title = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Founder Section"
        verbose_name_plural = "About Founder Sections"

    def __str__(self):
        return self.title if self.title else "About Founder Section"


class AboutCommitmentSection(models.Model):
    heading = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    button_text = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    button_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Example: /sustainability/ or https://example.com/report"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Commitment Section"
        verbose_name_plural = "About Commitment Sections"

    def __str__(self):
        return self.heading if self.heading else "About Commitment Section"


# =========================================================
# CONTACT PAGE
# =========================================================



class ContactHero(models.Model):
    title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    background_image = models.ImageField(max_length=500, 
        upload_to="contact/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Contact Hero"
        verbose_name_plural = "Contact Hero"

    def __str__(self):
        return self.title if self.title else "Contact Hero"


class ContactServiceInfo(models.Model):
    heading = models.CharField(
        max_length=150,
        default="Customer Services"
    )

    email_title = models.CharField(
        max_length=100,
        default="Email Us"
    )

    service_email = models.EmailField(
        default="padmavathyprasanna4@gmail.com",
        help_text="Contact form messages will be sent to this email."
    )

    call_title = models.CharField(
        max_length=100,
        default="Call Us"
    )

    phone_number_1 = models.CharField(
        max_length=30,
        default="+91-1234567890"
    )

    phone_number_2 = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        default="+91-1234567890"
    )

    track_order_text = models.CharField(
        max_length=100,
        default="Track You Order"
    )

    track_order_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="#"
    )

    cancel_order_text = models.CharField(
        max_length=100,
        default="Cancel Order"
    )

    cancel_order_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="#"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Contact Service Info"
        verbose_name_plural = "Contact Service Info"

    def __str__(self):
        return self.heading


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    mobile = models.CharField(max_length=30)
    message = models.TextField()

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.full_name} - {self.email}"
    


# =========================================================
# CONTACT PAGE FAQ SECTION
# Heading, questions, and answers are added from Django Admin.
# =========================================================

class ContactFAQSection(models.Model):
    heading = models.CharField(
        max_length=150,
        default="Frequently Asked Questions"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Contact FAQ Heading"
        verbose_name_plural = "Contact FAQ Heading"

    def __str__(self):
        return self.heading


class ContactFAQItem(models.Model):
    section = models.ForeignKey(
        ContactFAQSection,
        on_delete=models.CASCADE,
        related_name="faq_items",
        null=True,
        blank=True
    )

    question = models.CharField(
        max_length=255,
        help_text="Example: Is Cream Luxe Finish lipstick long-lasting?"
    )

    answer = models.TextField(
        help_text="Example: Yes, it lasts up to 6–8 hours with minimal touch-ups."
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower number shows first."
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Contact FAQ Item"
        verbose_name_plural = "Contact FAQ Items"

    def __str__(self):
        return self.question


# =========================================================
# TOP CATEGORIES CAROUSEL
# =========================================================

class TopCategorySection(models.Model):
    heading = models.CharField(
        max_length=150,
        default="Top Categories"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Top Category Section"
        verbose_name_plural = "Top Category Section"

    def __str__(self):
        return self.heading


class TopCategoryCard(models.Model):
    section = models.ForeignKey(
        TopCategorySection,
        on_delete=models.CASCADE,
        related_name="cards",
        null=True,
        blank=True
    )

    category_page = models.ForeignKey(
        Subcategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="top_category_cards",
        help_text="Select category page. Shop Now will navigate to this category."
    )

    image = models.ImageField(max_length=500, 
        upload_to="top_categories/"
    )

    title = models.CharField(
        max_length=100,
        help_text="Example: Lipsticks, Skincare, Eye Makeup"
    )

    subtitle = models.CharField(
        max_length=150,
        blank=True,
        help_text="Example: Vibrant & Bold Color"
    )

    button_text = models.CharField(
        max_length=50,
        default="Shop Now"
    )

    custom_link = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional. Example: /shop/eyemakeup/. If empty, selected category page link is used."
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Top Category Card"
        verbose_name_plural = "Top Category Cards"

    def __str__(self):
        return self.title


# =========================================================
# WHY GLOWIFY SECTION
# =========================================================

class WhyGlowifySection(models.Model):
    heading = models.CharField(
        max_length=150,
        default="Why Glowify"
    )

    main_image = models.ImageField(max_length=500, 
        upload_to="why_glowify/",
        help_text="Left side girl/product image"
    )

    flower_color = models.CharField(
        max_length=20,
        default="#F72585",
        help_text="Flower background color. Example: #F72585"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Why Glowify Section"
        verbose_name_plural = "Why Glowify Section"

    def __str__(self):
        return self.heading


class WhyGlowifyPoint(models.Model):
    section = models.ForeignKey(
        WhyGlowifySection,
        on_delete=models.CASCADE,
        related_name="points"
    )

    number = models.CharField(
        max_length=10,
        help_text="Example: 01, 02, 03, 04"
    )

    title = models.CharField(
        max_length=120,
        help_text="Example: Clean Beauty Promise"
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Why Glowify Point"
        verbose_name_plural = "Why Glowify Points"

    def __str__(self):
        return f"{self.number} - {self.title}"


# =========================================================
# HAPPY CUSTOMERS / TESTIMONIAL CAROUSEL
# =========================================================

class HappyCustomerSection(models.Model):
    heading = models.CharField(
        max_length=150,
        default="Happy Customers"
    )

    autoplay_seconds = models.PositiveIntegerField(
        default=4,
        help_text="Carousel auto-change time in seconds."
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Happy Customer Section"
        verbose_name_plural = "Happy Customer Section"

    def __str__(self):
        return self.heading


class HappyCustomerReview(models.Model):
    section = models.ForeignKey(
        HappyCustomerSection,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
        blank=True
    )

    customer_image = models.ImageField(max_length=500, 
        upload_to="happy_customers/",
        help_text="Customer profile image"
    )

    customer_name = models.CharField(
        max_length=120,
        help_text="Example: Ananya R."
    )

    location = models.CharField(
        max_length=120,
        blank=True,
        help_text="Example: Bangalore"
    )

    rating = models.PositiveIntegerField(
        default=5,
        help_text="Enter rating from 1 to 5"
    )

    review_text = models.TextField(
        help_text="Customer feedback text"
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Happy Customer Review"
        verbose_name_plural = "Happy Customer Reviews"

    def __str__(self):
        return self.customer_name

    @property
    def star_range(self):
        rating = max(0, min(int(self.rating), 5))
        return range(rating)

    @property
    def empty_star_range(self):
        rating = max(0, min(int(self.rating), 5))
        return range(5 - rating)


# =========================================================
# OFFERS PAGE IMAGE CAROUSEL
# Images are added from Django Admin.
# =========================================================

class OfferBanner(models.Model):
    image = models.ImageField(max_length=500, 
        upload_to="offers/banners/",
        help_text="Upload full offer banner image"
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower number shows first"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Offer Banner"
        verbose_name_plural = "Offer Banners"

    def __str__(self):
        return f"Offer Banner {self.id}"


# =========================================================
# OFFERS PAGE BUY 1 GET 1 FREE HEADING
# Heading is added from Django Admin.
# =========================================================

class OfferSection(models.Model):
    heading = models.CharField(
        max_length=150,
        default="Buy 1 Get 1 Free",
        help_text="Example: Buy 1 Get 1 Free"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Offer Section Heading"
        verbose_name_plural = "Offer Section Heading"

    def __str__(self):
        return self.heading


# =========================================================
# OFFERS PAGE PRODUCT CARDS
# Add three offer products from Django Admin.
# Shows image, name, description, discounted price,
# original price strikeout, and Add to Cart button.
# =========================================================

class OfferProduct(models.Model):
    image = models.ImageField(max_length=500, 
        upload_to="offers/products/",
        help_text="Upload offer product image"
    )

    image_name = models.CharField(
        max_length=150,
        help_text="Product name shown below image"
    )

    description = models.TextField(
        help_text="Product description shown below image name"
    )

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Original price. This will show with strikeout."
    )

    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Discounted price. This price will be added to cart."
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower number shows first. Add 3 active products for offer page."
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Offer Product"
        verbose_name_plural = "Offer Products"

    def clean(self):
        if self.discounted_price and self.original_price:
            if self.discounted_price > self.original_price:
                raise ValidationError(
                    "Discounted price cannot be greater than original price."
                )

    @property
    def title(self):
        return self.image_name

    @property
    def name(self):
        return self.image_name

    @property
    def price(self):
        return self.discounted_price

    @property
    def short_description(self):
        if self.description:
            return self.description[:55]
        return ""

    def __str__(self):
        return self.image_name


# =========================================================
# EXCLUSIVE CLAIM OFFER SECTION
# Big offer layout:
# Left image, right heading, description, price, old price,
# voucher, and Claim This Offer button.
# This offer is linked to ONE specific Product only.
# =========================================================

class ExclusiveOffer(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="exclusive_offers"
    )

    offer_image = models.ImageField(max_length=500, 
        upload_to="exclusive_offers/",
        blank=True,
        null=True,
        help_text="Upload image for exclusive offer section and cart page."
    )

    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    voucher_code = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Exclusive Claim Offer"
        verbose_name_plural = "Exclusive Claim Offers"

    def __str__(self):
        return self.product.name if self.product else "Exclusive Offer"

    @property
    def discount_percentage(self):
        if self.original_price and self.offer_price:
            try:
                discount = ((self.original_price - self.offer_price) / self.original_price) * 100
                return round(discount)
            except ZeroDivisionError:
                return 0
        return 0

    @property
    def display_image(self):
        if self.offer_image:
            return self.offer_image

        if self.product and self.product.image:
            return self.product.image

        return None





class FooterSetting(models.Model):
    logo = models.ImageField(max_length=500, upload_to="footer/logo/", blank=True, null=True)

    address = models.TextField(
        default="3rd Floor, Valasaravakam,\nChennai - 600800"
    )

    quick_links_title = models.CharField(
        max_length=100,
        default="Quick Links"
    )

    support_title = models.CharField(
        max_length=100,
        default="Support"
    )

    social_media_title = models.CharField(
        max_length=100,
        default="Social Media"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Footer Setting"
        verbose_name_plural = "Footer Settings"

    def __str__(self):
        return "Footer Setting"


class FooterLink(models.Model):
    SECTION_CHOICES = (
        ("quick_links", "Quick Links"),
        ("support", "Support"),
    )

    section = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES
    )

    title = models.CharField(max_length=100)

    url = models.CharField(
        max_length=255,
        help_text="Example: /shop/ or https://example.com"
    )

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Footer Link"
        verbose_name_plural = "Footer Links"

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"


class FooterSocialMedia(models.Model):
    name = models.CharField(max_length=100)

    url = models.URLField(
        help_text="Example: https://instagram.com/yourpage"
    )

    icon_class = models.CharField(
        max_length=100,
        blank=True,
        help_text="Font Awesome class. Example: fab fa-facebook-f or fab fa-instagram"
    )

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]
        verbose_name = "Footer Social Media"
        verbose_name_plural = "Footer Social Media"

    def __str__(self):
        return self.name
