from django.contrib.auth.models import User
from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError

class Car(models.Model):
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    license_plate = models.CharField(max_length=20, unique=True)  
    image = models.ImageField(upload_to='car_images/', blank=False, null=False) 
    
    def get_reserved_dates(self):
        """Kthen një listë me të gjitha datat e rezervuara për këtë makinë."""
        reservations = self.rental_set.all()
        reserved_dates = []
        for rental in reservations:
            if rental.return_date:
                reserved_dates.extend([rental.rental_date + timedelta(days=i)
                                       for i in range((rental.return_date - rental.rental_date).days + 1)])
        return reserved_dates


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
    

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    rental_date = models.DateField()  
    return_date = models.DateField() 
    is_cancelled = models.BooleanField(default=False)  # Fusha për anulimin e rezervimit

    def cancel(self):
        """Funksioni për të anuluar rezervimin."""
        self.is_cancelled = True
        self.save()
 
    def __str__(self):
        return f"{self.user.username} rented {self.car.brand} {self.car.model} from {self.rental_date} to {self.return_date}"
    
    def save(self, *args, **kwargs):
        self.clean()  # Thirrja e metodës 'clean' për validim manual
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.car.model} ({self.rental_date} to {self.return_date})"

class Message(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message to {self.recipient.username} from {self.sender.username if self.sender else 'System'}"


