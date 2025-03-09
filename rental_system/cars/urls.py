from django.urls import path
from .views import car_list
from .views import car_detail
from .views import rent_car
from .views import inbox
from .views import cancel_reservation
from .views import user_reservations
from .views import mark_as_read
from .views import reservation_detail
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', car_list, name='car_list'),
    path('<int:car_id>/', car_detail, name='car_detail'),
    path('rent/<int:car_id>/', rent_car, name='rent_car'),
    path('inbox/', inbox, name='inbox'),
    path('reservations/', user_reservations, name='user_reservations'),
    path('reservation/cancel/<int:rental_id>/', cancel_reservation, name='cancel_reservation'),
    path('mark_as_read/<int:message_id>/', mark_as_read, name='mark_as_read'),
    path('reservations/<int:rental_id>/', reservation_detail, name='reservation_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

