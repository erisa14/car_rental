# from django.contrib import admin
# from .models import Car, Message, Rental
# from .models import UserProfile

# admin.site.register(Car)
# admin.site.register(UserProfile)
# admin.site.register(Message)
# admin.site.register(Rental)
from django.contrib import admin
from .models import Car, UserProfile, Rental, Message
from django.contrib.auth.models import User


# Për të fshehur fushat sensitive nga admin paneli
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ('username', 'email')  # Shfaq vetëm username dhe email
    search_fields = ('username', 'email')  # Kërko sipas username dhe email

    # Fsheh fushën e password-it në formën e admin-it
    fieldsets = (
        (None, {'fields': ('username', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'license_plate', 'price_per_day', 'image_tag')
    list_filter = ('year', 'brand')
    search_fields = ('brand', 'model', 'license_plate')

    def image_tag(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="border-radius:5px;" />'
        return "No Image"
    
    image_tag.allow_tags = True
    image_tag.short_description = 'Car Image'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'address')
    search_fields = ('user__username', 'phone_number')


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('user', 'car__brand', 'car__license_plate', 'rental_date', 'return_date', 'is_cancelled')  # Shtuar statusin e anulimit
    list_filter = ('rental_date', 'car__brand', 'is_cancelled')  # Filtrimi për anulimin e rezervimit
    search_fields = ('user__username', 'car__model')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('content', 'timestamp', 'read')
    list_filter = ('timestamp', 'recipient', 'sender')  # Filtron sipas sender dhe recipient
    search_fields = ('sender__username', 'recipient__username', 'content')

     # Mundësitë për të shënuar mesazhet si të lexuara ose të pa lexuara
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)

    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)

    mark_as_read.short_description = "Mark selected messages as read"
    mark_as_unread.short_description = "Mark selected messages as unread"

    def get_queryset(self, request):
        # Sigurohemi që admini të shohë vetëm mesazhet nga përdoruesit, dhe jo ato nga sistemi
        queryset = super().get_queryset(request)
        return queryset.filter(sender__isnull=False)  # Filtron mesazhet që janë dërguar nga përdoruesi
