from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Rental
from .models import Car
from datetime import date

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    phone_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phone_number', 'address']

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone_number = self.cleaned_data["phone_number"]
        if UserProfile.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is already in use.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            
            # Kontrollojmë nëse ekziston një profil për këtë user
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data['phone_number'],
                    'address': self.cleaned_data['address']
                }
            )
            
            # Nëse profili ekziston tashmë, përditësojmë të dhënat
            if not created:
                profile.phone_number = self.cleaned_data['phone_number']
                profile.address = self.cleaned_data['address']
                profile.save()
        
        return user


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['rental_date', 'return_date']

    rental_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    return_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        car = kwargs.pop('car', None)
        super().__init__(*args, **kwargs)

        today = date.today()
        self.fields['rental_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
        self.fields['return_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')

        if car:
            reserved_dates = car.get_reserved_dates()
            self.fields['rental_date'].widget.attrs['data-reserved'] = reserved_dates
            self.fields['return_date'].widget.attrs['data-reserved'] = reserved_dates

    def clean(self):
        cleaned_data = super().clean()
        rental_date = cleaned_data.get('rental_date')
        return_date = cleaned_data.get('return_date')

        # Sigurohuni që data e kthimit të jetë pas datës së qiramarrjes
        if rental_date and return_date:
            if return_date <= rental_date:
                raise forms.ValidationError("The return date must be after the rental date.")

        return cleaned_data