# dashboard/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.contrib import admin
from .models import FooterSetting, FooterLink, FooterSocialMedia


@admin.register(FooterSetting)
class FooterSettingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quick_links_title",
        "support_title",
        "social_media_title",
        "is_active",
    )

    list_editable = ("is_active",)


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "section",
        "url",
        "display_order",
        "is_active",
    )

    list_filter = ("section", "is_active")
    search_fields = ("title", "url")
    list_editable = ("display_order", "is_active")


@admin.register(FooterSocialMedia)
class FooterSocialMediaAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
        "icon_class",
        "display_order",
        "is_active",
    )

    search_fields = ("name", "url")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)

from .models import (
    NavbarLink,
    Category,
    Subcategory,

    Brand,
    Color,
    DiscountOption,
    PriceRange,

    FeaturedProductSection,
    Product,
    UserProfile,
    CartItem,
    WishlistItem,

    SiteLogo,
    Banner,
    HomeContent,
    PerformanceSection,
    PerformanceIngredient,

    StoreSetting,
    ShippingMethod,
    PaymentMethod,

    Order,
    OrderItem,

    SubscribeBanner,
    Subscriber,

    AboutHero,
    AboutStorySection,
    AboutCoreValueSection,
    AboutCoreValueCard,
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


    HomeFlashSaleSection,
    ExclusiveOffer,
)

@admin.register(HomeFlashSaleSection)
class HomeFlashSaleSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "sale_text", "button_text", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("title", "sale_text", "quote_text")


# =========================================================
# CATEGORY / PAGE ITEMS
# =========================================================

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1

    fields = (
        "page_name",
        "heading",
        "slug",
        "page_url",
        "search_placeholder",
        "order",
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("page_name",),
    }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    fields = (
        "heading",
        "order",
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )

    inlines = [SubcategoryInline]


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        "page_name",
        "heading",
        "category",
        "slug",
        "page_url",
        "search_placeholder",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "page_name",
        "heading",
        "slug",
        "page_url",
    )

    prepopulated_fields = {
        "slug": ("page_name",),
    }

    fieldsets = (
        ("Basic Page Details", {
            "fields": (
                "category",
                "page_name",
                "heading",
                "slug",
                "page_url",
                "search_placeholder",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
            )
        }),
    )


# =========================================================
# NAVBAR
# =========================================================

@admin.register(NavbarLink)
class NavbarLinkAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "url",
        "icon",
        "order",
        "is_active",
    )

    list_editable = (
        "url",
        "order",
        "is_active",
    )

    search_fields = (
        "name",
        "url",
    )

    list_filter = (
        "is_active",
    )

    fieldsets = (
        ("Navbar Link Details", {
            "fields": (
                "name",
                "url",
                "icon",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
            )
        }),
    )


# =========================================================
# SHOP FILTERS
# =========================================================

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    search_fields = (
        "name",
        "slug",
    )

    list_filter = (
        "is_active",
    )


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "hex_code",
        "is_active",
    )

    list_editable = (
        "hex_code",
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    search_fields = (
        "name",
        "slug",
        "hex_code",
    )

    list_filter = (
        "is_active",
    )


@admin.register(DiscountOption)
class DiscountOptionAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "slug",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("label",),
    }

    search_fields = (
        "label",
        "slug",
    )

    list_filter = (
        "is_active",
    )


@admin.register(PriceRange)
class PriceRangeAdmin(admin.ModelAdmin):
    list_display = (
        "label",
        "slug",
        "min_price",
        "max_price",
        "is_active",
    )

    list_editable = (
        "min_price",
        "max_price",
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("label",),
    }

    search_fields = (
        "label",
        "slug",
    )

    list_filter = (
        "is_active",
    )


# =========================================================
# FEATURED PRODUCT SECTION
# =========================================================

@admin.register(FeaturedProductSection)
class FeaturedProductSectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )


# =========================================================
# PRODUCT
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "name",
        "page_item",
        "brand",
        "price",
        "rating",
        "reviews_count",
        "badge",
        "order",
        "is_featured",
        "is_active",
        "created_at",
    )

    list_editable = (
        "price",
        "rating",
        "reviews_count",
        "badge",
        "order",
        "is_featured",
        "is_active",
    )

    list_filter = (
        "page_item",
        "brand",
        "colors",
        "discount_options",
        "badge",
        "is_featured",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "shade_name",
        "description",
        "tagline",
        "how_to_use",
        "benefits",
        "brand__name",
        "page_item__page_name",
        "page_item__heading",
    )

    readonly_fields = (
        "image_preview",
        "created_at",
    )

    fieldsets = (
        ("Product Page and Basic Info", {
            "fields": (
                "page_item",
                "brand",
                "name",
                "shade_name",
                "tagline",
                "description",
                "how_to_use",
                "benefits",
                "image",
                "image_preview",
            )
        }),
        ("Filter Values", {
            "fields": (
                "colors",
                "discount_options",
            )
        }),
        ("Price and Reviews", {
            "fields": (
                "price",
                "rating",
                "reviews_count",
            )
        }),
        ("Home Featured Product Settings", {
            "fields": (
                "badge",
                "order",
                "is_featured",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
                "created_at",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:70px;height:70px;object-fit:contain;border-radius:8px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Image"


# =========================================================
# USER PROFILE
# =========================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    filter_horizontal = (
        "wishlist",
        "cart",
    )


# =========================================================
# CART ITEM
# =========================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "session_key",
        "quantity",
        "line_total",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "quantity",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "product__name",
        "user__username",
        "user__email",
        "session_key",
    )

    readonly_fields = (
        "line_total",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Cart Details", {
            "fields": (
                "product",
                "user",
                "session_key",
                "quantity",
                "line_total",
            )
        }),
        ("Dates", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


# =========================================================
# WISHLIST ITEM
# =========================================================

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "user",
        "session_key",
        "created_at",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "product__name",
        "user__username",
        "user__email",
        "session_key",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        ("Wishlist Details", {
            "fields": (
                "product",
                "user",
                "session_key",
            )
        }),
        ("Date", {
            "fields": (
                "created_at",
            )
        }),
    )


# =========================================================
# SITE LOGO
# =========================================================

@admin.register(SiteLogo)
class SiteLogoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_preview",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    readonly_fields = (
        "image_preview",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:120px;height:50px;object-fit:contain;border-radius:6px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Logo"


# =========================================================
# BANNER
# =========================================================

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image_preview",
        "button_text",
        "button_link",
        "order",
        "is_active",
    )

    list_editable = (
        "button_text",
        "button_link",
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "button_text",
        "button_link",
    )

    readonly_fields = (
        "image_preview",
    )

    fieldsets = (
        ("Banner Details", {
            "fields": (
                "image",
                "image_preview",
                "button_text",
                "button_link",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:140px;height:65px;object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Banner Image"


# =========================================================
# HOME CONTENT
# =========================================================

@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "heading",
        "content_text",
    )

    list_filter = (
        "is_active",
    )


# =========================================================
# PERFORMANCE SECTION
# =========================================================

class PerformanceIngredientInline(admin.TabularInline):
    model = PerformanceIngredient
    extra = 1

    fields = (
        "image",
        "title",
        "description",
        "order",
        "is_active",
    )


@admin.register(PerformanceSection)
class PerformanceSectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "autoplay_seconds",
        "is_active",
    )

    list_editable = (
        "autoplay_seconds",
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )

    inlines = [PerformanceIngredientInline]


@admin.register(PerformanceIngredient)
class PerformanceIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "section",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "section",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )


# =========================================================
# STORE SETTINGS
# =========================================================

@admin.register(StoreSetting)
class StoreSettingAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "estimated_shipping",
        "gst",
        "is_active",
    )

    list_editable = (
        "estimated_shipping",
        "gst",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
    )


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "subtitle",
        "cost",
        "is_default",
        "is_active",
        "order",
    )

    list_editable = (
        "subtitle",
        "cost",
        "is_default",
        "is_active",
        "order",
    )

    list_filter = (
        "is_default",
        "is_active",
    )

    search_fields = (
        "name",
        "subtitle",
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "icon_preview",
        "name",
        "code",
        "icon_text",
        "is_active",
        "order",
    )

    list_editable = (
        "icon_text",
        "is_active",
        "order",
    )

    fields = (
        "name",
        "code",
        "icon_image",
        "icon_preview",
        "icon_text",
        "is_active",
        "order",
    )

    readonly_fields = (
        "icon_preview",
    )

    def icon_preview(self, obj):
        if obj and obj.icon_image:
            return format_html(
                '<img src="{}" style="width:35px;height:35px;object-fit:contain;" />',
                obj.icon_image.url
            )
        return "No image"

    icon_preview.short_description = "Icon"


# =========================================================
# ORDERS
# =========================================================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = (
        "product",
        "title",
        "shade_name",
        "price",
        "quantity",
        "line_total",
    )

    fields = (
        "product",
        "title",
        "shade_name",
        "price",
        "quantity",
        "line_total",
    )

    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "mobile",
        "city",
        "state",
        "subtotal",
        "shipping_cost",
        "gst",
        "total",
        "payment_status",
        "created_at",
    )

    list_filter = (
        "shipping_method",
        "payment_method",
        "payment_status",
        "city",
        "state",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "mobile",
        "address",
        "city",
        "state",
        "pin_code",
        "items__title",
    )

    readonly_fields = (
        "subtotal",
        "shipping_cost",
        "gst",
        "total",
        "payment_status",
        "created_at",
    )

    fieldsets = (
        ("Customer Details", {
            "fields": (
                "first_name",
                "last_name",
                "mobile",
            )
        }),
        ("Address", {
            "fields": (
                "address",
                "city",
                "state",
                "pin_code",
            )
        }),
        ("Shipping and Payment", {
            "fields": (
                "shipping_method",
                "payment_method",
        "payment_status",
        "phonepe_merchant_order_id",
        "phonepe_transaction_id",
        "phonepe_response",
            )
        }),
        ("Order Amount", {
            "fields": (
                "subtotal",
                "shipping_cost",
                "gst",
                "total",
            )
        }),
        ("Date", {
            "fields": (
                "created_at",
            )
        }),
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "title",
        "shade_name",
        "price",
        "quantity",
        "line_total",
    )

    list_filter = (
        "order__created_at",
    )

    search_fields = (
        "title",
        "shade_name",
        "product__name",
        "order__first_name",
        "order__mobile",
    )

    readonly_fields = (
        "order",
        "product",
        "title",
        "shade_name",
        "price",
        "quantity",
        "line_total",
    )


# =========================================================
# SUBSCRIBE / BEAUTY CIRCLE BANNER
# =========================================================

@admin.register(SubscribeBanner)
class SubscribeBannerAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "heading",
        "button_text",
        "background_color",
        "is_active",
    )

    list_editable = (
        "button_text",
        "background_color",
        "is_active",
    )

    search_fields = (
        "heading",
        "description",
        "button_text",
        "email_placeholder",
        "background_color",
    )

    list_filter = (
        "is_active",
    )

    readonly_fields = (
        "image_preview",
    )

    fieldsets = (
        ("Category Page Left Image", {
            "fields": (
                "left_image",
                "image_preview",
            )
        }),
        ("Subscribe Banner Content", {
            "fields": (
                "heading",
                "description",
                "email_placeholder",
                "button_text",
            )
        }),
        ("Design", {
            "fields": (
                "background_color",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.left_image:
            return format_html(
                '<img src="{}" style="width:120px;height:90px;object-fit:contain;border-radius:8px;" />',
                obj.left_image.url
            )
        return "No image"

    image_preview.short_description = "Left Image"


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "subscribed_at",
    )

    search_fields = (
        "email",
    )

    readonly_fields = (
        "email",
        "subscribed_at",
    )

    list_filter = (
        "subscribed_at",
    )


# =========================================================
# ABOUT PAGE
# =========================================================

@admin.register(AboutHero)
class AboutHeroAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
        "image_preview",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "title",
        "subtitle",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "image_preview",
    )

    def image_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="width:120px;height:50px;object-fit:cover;border-radius:6px;" />',
                obj.background_image.url
            )
        return "No image"

    image_preview.short_description = "Hero Image"


@admin.register(AboutStorySection)
class AboutStorySectionAdmin(admin.ModelAdmin):
    list_display = (
        "story_title",
        "mission_title",
        "is_active",
        "image_preview",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "story_title",
        "story_text",
        "mission_title",
        "mission_text",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "image_preview",
    )

    fieldsets = (
        ("Story Content", {
            "fields": (
                "story_title",
                "story_text",
            )
        }),
        ("Mission Content", {
            "fields": (
                "mission_title",
                "mission_text",
            )
        }),
        ("Right Side Image", {
            "fields": (
                "side_image",
                "image_preview",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.side_image:
            return format_html(
                '<img src="{}" style="width:130px;height:70px;object-fit:cover;border-radius:6px;" />',
                obj.side_image.url
            )
        return "No image"

    image_preview.short_description = "Side Image"


class AboutCoreValueCardInline(admin.TabularInline):
    model = AboutCoreValueCard
    extra = 3

    fields = (
        "order",
        "icon",
        "title",
        "description",
        "is_active",
    )


@admin.register(AboutCoreValueSection)
class AboutCoreValueSectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    inlines = [AboutCoreValueCardInline]


@admin.register(AboutCoreValueCard)
class AboutCoreValueCardAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "section",
        "order",
        "is_active",
        "icon_preview",
        "created_at",
    )

    list_editable = (
        "order",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = (
        "order",
        "id",
    )

    readonly_fields = (
        "icon_preview",
    )

    def icon_preview(self, obj):
        if obj.icon:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;object-fit:contain;border-radius:50%;" />',
                obj.icon.url
            )
        return "No icon"

    icon_preview.short_description = "Icon"


@admin.register(AboutFounderSection)
class AboutFounderSectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
        "image_preview",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "image_preview",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Founder Image"


@admin.register(AboutCommitmentSection)
class AboutCommitmentSectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "button_text",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "heading",
        "description",
        "button_text",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    fieldsets = (
        ("Commitment Content", {
            "fields": (
                "heading",
                "description",
            )
        }),
        ("Button", {
            "fields": (
                "button_text",
                "button_url",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )


# =========================================================
# CONTACT PAGE
# =========================================================

@admin.register(ContactHero)
class ContactHeroAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
        "image_preview",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "is_active",
    )

    readonly_fields = (
        "image_preview",
    )

    fieldsets = (
        ("Contact Hero Content", {
            "fields": (
                "title",
                "description",
            )
        }),
        ("Hero Image", {
            "fields": (
                "background_image",
                "image_preview",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.background_image:
            return format_html(
                '<img src="{}" style="width:180px;height:70px;object-fit:cover;border-radius:8px;" />',
                obj.background_image.url
            )
        return "No image"

    image_preview.short_description = "Hero Image"


@admin.register(ContactServiceInfo)
class ContactServiceInfoAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "service_email",
        "phone_number_1",
        "is_active",
    )

    list_editable = (
        "service_email",
        "phone_number_1",
        "is_active",
    )

    search_fields = (
        "heading",
        "service_email",
        "phone_number_1",
        "phone_number_2",
    )

    list_filter = (
        "is_active",
    )

    fieldsets = (
        ("Heading", {
            "fields": (
                "heading",
            )
        }),
        ("Email Details", {
            "fields": (
                "email_title",
                "service_email",
            )
        }),
        ("Call Details", {
            "fields": (
                "call_title",
                "phone_number_1",
                "phone_number_2",
            )
        }),
        ("Order Links", {
            "fields": (
                "track_order_text",
                "track_order_url",
                "cancel_order_text",
                "cancel_order_url",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "mobile",
        "is_read",
        "created_at",
    )

    list_editable = (
        "is_read",
    )

    search_fields = (
        "full_name",
        "email",
        "mobile",
        "message",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    readonly_fields = (
        "full_name",
        "email",
        "mobile",
        "message",
        "created_at",
    )

    fieldsets = (
        ("User Details", {
            "fields": (
                "full_name",
                "email",
                "mobile",
            )
        }),
        ("Message", {
            "fields": (
                "message",
            )
        }),
        ("Status", {
            "fields": (
                "is_read",
                "created_at",
            )
        }),
    )

# =========================================================
# CONTACT PAGE FAQ SECTION
# =========================================================

class ContactFAQItemInline(admin.TabularInline):
    model = ContactFAQItem
    extra = 1

    fields = (
        "question",
        "answer",
        "order",
        "is_active",
    )


@admin.register(ContactFAQSection)
class ContactFAQSectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )

    fieldsets = (
        ("FAQ Heading", {
            "fields": (
                "heading",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )

    inlines = [ContactFAQItemInline]


@admin.register(ContactFAQItem)
class ContactFAQItemAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "section",
        "order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "section",
        "is_active",
        "created_at",
    )

    search_fields = (
        "question",
        "answer",
    )

    readonly_fields = (
        "created_at",
    )

    fieldsets = (
        ("FAQ Content", {
            "fields": (
                "section",
                "question",
                "answer",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
                "created_at",
            )
        }),
    )
# =========================================================
# TOP CATEGORIES CAROUSEL
# =========================================================

class TopCategoryCardInline(admin.TabularInline):
    model = TopCategoryCard
    extra = 1

    fields = (
        "image",
        "title",
        "subtitle",
        "button_text",
        "category_page",
        "custom_link",
        "order",
        "is_active",
    )


@admin.register(TopCategorySection)
class TopCategorySectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )

    inlines = [TopCategoryCardInline]


@admin.register(TopCategoryCard)
class TopCategoryCardAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "title",
        "subtitle",
        "category_page",
        "button_text",
        "order",
        "is_active",
    )

    list_editable = (
        "subtitle",
        "button_text",
        "order",
        "is_active",
    )

    list_filter = (
        "section",
        "category_page",
        "is_active",
    )

    search_fields = (
        "title",
        "subtitle",
        "category_page__page_name",
    )

    readonly_fields = (
        "image_preview",
        "created_at",
    )

    fieldsets = (
        ("Card Content", {
            "fields": (
                "section",
                "image",
                "image_preview",
                "title",
                "subtitle",
                "button_text",
            )
        }),
        ("Navigation", {
            "fields": (
                "category_page",
                "custom_link",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
                "created_at",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:90px;height:70px;object-fit:contain;border-radius:8px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Image"


# =========================================================
# WHY GLOWIFY SECTION
# =========================================================

class WhyGlowifyPointInline(admin.TabularInline):
    model = WhyGlowifyPoint
    extra = 1

    fields = (
        "number",
        "title",
        "order",
        "is_active",
    )


@admin.register(WhyGlowifySection)
class WhyGlowifySectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "image_preview",
        "flower_color",
        "is_active",
    )

    list_editable = (
        "flower_color",
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )

    readonly_fields = (
        "image_preview",
    )

    fieldsets = (
        ("Section Content", {
            "fields": (
                "heading",
                "main_image",
                "image_preview",
                "flower_color",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )

    inlines = [WhyGlowifyPointInline]

    def image_preview(self, obj):
        if obj.main_image:
            return format_html(
                '<img src="{}" style="width:110px;height:110px;object-fit:contain;border-radius:10px;" />',
                obj.main_image.url
            )
        return "No image"

    image_preview.short_description = "Main Image"


@admin.register(WhyGlowifyPoint)
class WhyGlowifyPointAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "title",
        "section",
        "order",
        "is_active",
    )

    list_editable = (
        "title",
        "order",
        "is_active",
    )

    list_filter = (
        "section",
        "is_active",
    )

    search_fields = (
        "number",
        "title",
        "section__heading",
    )


# =========================================================
# HAPPY CUSTOMERS / TESTIMONIAL CAROUSEL
# =========================================================

class HappyCustomerReviewInline(admin.TabularInline):
    model = HappyCustomerReview
    extra = 1

    fields = (
        "customer_image",
        "customer_name",
        "location",
        "rating",
        "review_text",
        "order",
        "is_active",
    )


@admin.register(HappyCustomerSection)
class HappyCustomerSectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "autoplay_seconds",
        "is_active",
    )

    list_editable = (
        "autoplay_seconds",
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )

    inlines = [HappyCustomerReviewInline]


@admin.register(HappyCustomerReview)
class HappyCustomerReviewAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "customer_name",
        "location",
        "rating",
        "order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "rating",
        "order",
        "is_active",
    )

    list_filter = (
        "section",
        "rating",
        "is_active",
    )

    search_fields = (
        "customer_name",
        "location",
        "review_text",
    )

    readonly_fields = (
        "image_preview",
        "created_at",
    )

    fieldsets = (
        ("Customer Details", {
            "fields": (
                "section",
                "customer_image",
                "image_preview",
                "customer_name",
                "location",
            )
        }),
        ("Review", {
            "fields": (
                "rating",
                "review_text",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
                "created_at",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.customer_image:
            return format_html(
                '<img src="{}" style="width:70px;height:70px;object-fit:cover;border-radius:50%;border:2px solid #F72585;" />',
                obj.customer_image.url
            )
        return "No image"

    image_preview.short_description = "Customer Image"


# =========================================================
# OFFERS PAGE IMAGE CAROUSEL
# =========================================================

@admin.register(OfferBanner)
class OfferBannerAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "image_preview",
        "created_at",
    )

    fieldsets = (
        ("Carousel Image", {
            "fields": (
                "image",
                "image_preview",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
                "created_at",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:220px;height:80px;object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Preview"


# =========================================================
# OFFERS PAGE BUY 1 GET 1 FREE HEADING
# =========================================================

@admin.register(OfferSection)
class OfferSectionAdmin(admin.ModelAdmin):
    list_display = (
        "heading",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    search_fields = (
        "heading",
    )

    list_filter = (
        "is_active",
    )

    fieldsets = (
        ("Offer Heading", {
            "fields": (
                "heading",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
    )


# =========================================================
# OFFERS PAGE PRODUCT CARDS
# =========================================================

@admin.register(OfferProduct)
class OfferProductAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "image_name",
        "original_price",
        "discounted_price",
        "order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "original_price",
        "discounted_price",
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "image_name",
        "description",
    )

    readonly_fields = (
        "image_preview",
        "created_at",
    )

    fieldsets = (
        ("Offer Product Image", {
            "fields": (
                "image",
                "image_preview",
            )
        }),
        ("Product Content", {
            "fields": (
                "image_name",
                "description",
            )
        }),
        ("Price Details", {
            "fields": (
                "original_price",
                "discounted_price",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
                "created_at",
            )
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:90px;height:90px;object-fit:cover;border-radius:10px;border:1px solid #ffd6e6;" />',
                obj.image.url
            )
        return "No image"

    image_preview.short_description = "Product Image"



    # =========================================================
# EXCLUSIVE OFFERS
# Example: Exclusive Kit - Midnight Repair Set
# =========================================================



@admin.register(ExclusiveOffer)
class ExclusiveOfferAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "product",
        "original_price",
        "offer_price",
        "discount_value",
        "voucher_code",
        "order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "original_price",
        "offer_price",
        "voucher_code",
        "order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__description",
        "voucher_code",
    )

    readonly_fields = (
        "image_preview",
        "discount_value",
        "created_at",
    )

    fieldsets = (
        ("Exclusive Offer Product", {
            "fields": (
                "product",
            )
        }),
        ("Offer Image", {
            "fields": (
                "offer_image",
                "image_preview",
            )
        }),
        ("Price Details", {
            "fields": (
                "original_price",
                "offer_price",
                "discount_value",
                "voucher_code",
            )
        }),
        ("Status and Order", {
            "fields": (
                "order",
                "is_active",
                "created_at",
            )
        }),
    )

    def image_preview(self, obj):
        image = None

        if obj.offer_image:
            image = obj.offer_image
        elif obj.product and obj.product.image:
            image = obj.product.image

        if image:
            return format_html(
                '<img src="{}" style="width:180px;height:95px;object-fit:cover;border-radius:12px;border:1px solid #ffd6e6;" />',
                image.url
            )

        return "No image"

    image_preview.short_description = "Offer Image"

    def discount_value(self, obj):
        if obj.original_price and obj.offer_price:
            try:
                discount = ((obj.original_price - obj.offer_price) / obj.original_price) * 100
                return f"Save {discount:.0f}%"
            except ZeroDivisionError:
                return "Save 0%"
        return "Save 0%"

    discount_value.short_description = "Discount"