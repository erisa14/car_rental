
from .forms import UserRegistrationForm, RentalForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Car, Rental, Message
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.utils import timezone
import json


def car_list(request):
    cars = Car.objects.all()  # Shfaq vetëm makinat e disponueshme
    return render(request, 'cars/car_list.html', {'cars': cars})

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'cars/car_detail.html', {'car': car})

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Logon automatikisht përdoruesin pas regjistrimit
            return redirect("car_list")
    else:
        form = UserRegistrationForm()

    return render(request, "cars/register.html", {"form": form})

@login_required
def rent_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    # Get all reserved date intervals for this car
    reserved_intervals = Rental.objects.filter(car=car, is_cancelled=False).values_list("rental_date", "return_date")
    reserved_dates = []
    for rental_date, return_date in reserved_intervals:
        current_date = rental_date
        while current_date <= return_date:
            reserved_dates.append(current_date.strftime("%Y-%m-%d"))
            current_date += timezone.timedelta(days=1)

    if request.method == "POST":
        form = RentalForm(request.POST, car=car)
        if form.is_valid():
            rental_date = form.cleaned_data['rental_date']
            return_date = form.cleaned_data['return_date']

            # Check if selected dates are available
            existing_rentals = Rental.objects.filter(
                car=car,
                rental_date__lte=return_date,
                return_date__gte=rental_date,
                is_cancelled=False
            )

            if existing_rentals.exists():
                messages.error(request, "This car is already booked for the selected dates. Please choose different dates.")
                return redirect('car_detail', car_id=car.id)  # Redirect to car_detail on overlap

            # Create the rental
            rental = Rental.objects.create(
                user=request.user,
                car=car,
                rental_date=rental_date,
                return_date=return_date
            )

            # Message for user
            Message.objects.create(
                recipient=request.user,
                sender=None,
                content=f"You have successfully rented {car.brand} {car.model} from {rental_date} to {return_date}."
            )

            # Message for admin
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                Message.objects.create(
                    recipient=admin_user,
                    sender=request.user,
                    content=f"{request.user.username} has rented {car.brand} {car.model} from {rental_date} to {return_date}."
                )

            messages.success(request, f'You have successfully rented {car.brand} {car.model} from {rental_date} to {return_date}.')
            return redirect('car_detail', car_id=car.id)

        else:
            messages.error(request, "There was an error processing your reservation. Please check your input and try again.")
            return redirect('car_detail', car_id=car.id)  # Redirect to car_detail on invalid form

    else:
        form = RentalForm(car=car)

    return render(request, 'cars/rent_car.html', {
        'form': form,
        'car': car,
        'reserved_dates': json.dumps(reserved_dates)
    })


@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'cars/inbox.html', {'messages': messages})


@login_required
def cancel_reservation(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id)

    # Kontrollo që përdoruesi të jetë ai që ka bërë rezervimin
    if rental.user != request.user:
        messages.error(request, "You cannot cancel this reservation.")
        return redirect('reservation_detail', rental_id=rental.id)

    # Anulo rezervimin
    rental.cancel()

    # rental.delete()

    # Dërgo mesazh për përdoruesin që rezervimi është anuluar
    Message.objects.create(
        recipient=rental.user,
        sender=None,
        content=f"Your reservation for {rental.car.brand} {rental.car.model} from {rental.rental_date} to {rental.return_date} has been successfully cancelled."
    )

    # Dërgo mesazh për adminin për anulimin
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        Message.objects.create(
            recipient=admin_user,
            sender=request.user,
            content=f"{request.user.username} has cancelled the reservation for {rental.car.brand} {rental.car.model} from {rental.rental_date} to {rental.return_date}."
        )

    messages.success(request, "Your reservation has been successfully cancelled.")
    return redirect('car_detail', car_id=rental.car.id)

@login_required
def user_reservations(request):
    # Merr të gjitha rezervimet e përdoruesit aktual që nuk janë anuluar
    reservations = Rental.objects.filter(user=request.user, is_cancelled=False)
    return render(request, 'cars/user_reservations.html', {'reservations': reservations})


def mark_as_read(request, message_id):
    message = get_object_or_404(Message, id=message_id, recipient=request.user)
    message.read = True
    message.save()
    return redirect('inbox') 

def reservation_detail(request, rental_id):
    reservation = get_object_or_404(Rental, id=rental_id)
    return render(request, 'cars/reservation_detail.html', {'reservation': reservation})
