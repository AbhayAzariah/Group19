from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from .models import Room, Message, Profile
from .forms import MessageForm, ProfileForm
from static.py.program_logic import fetch_school_details


# View for home page
def home(request):
    return render(request, 'base/home.html')

# View for finding universities
def find(request):
    """
    Handles the search for universities and displays the results.
    """
    search_results = []

    if request.method == "POST":
        # Get the search query from the form
        search_query = request.POST.get("search_query", "").strip()
        if search_query:
            # Call the fetch_school_details function to get university data
            search_results = fetch_school_details(search_query)

            # Handle cases where no results are found
            if not search_results:
                messages.info(request, f"No results found for '{search_query}'. Please try another search.")
        else:
            messages.error(request, "Please enter a university name to search.")

    return render(request, "base/find.html", {"search_results": search_results})

# Other views remain unchanged
def compare(request):
    return render(request, 'base/compare.html')

def room_list(request):
    query = request.GET.get('q', '')  # Get the search query from GET
    rooms = Room.objects.all()

    if query:
        rooms = rooms.filter(name__icontains=query) | rooms.filter(description__icontains=query)

    paginator = Paginator(rooms, 5)  # 5 rooms per page
    page = request.GET.get('page')
    rooms_paginated = paginator.get_page(page)

    context = {
        'rooms': rooms_paginated,
        'query': query,
    }
    return render(request, 'base/room_list.html', context)

@login_required(login_url='login_register')
def create_room(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        room = Room.objects.create(name=name, description=description, creator=request.user)
        return redirect('room_list')
    return render(request, 'base/create_room.html')

@login_required(login_url='login_register')
def chatroom(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    messages = room.messages.order_by('timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            Message.objects.create(room=room, content=content, user=request.user)
            return redirect('chatroom', room_id=room.id)
    else:
        form = MessageForm()

    return render(request, 'base/chatroom.html', {'room': room, 'messages': messages, 'form': form})

@login_required(login_url='login_register')
def edit_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if room.creator != request.user:
        return HttpResponseForbidden("You are not authorized to edit this room")

    if request.method == 'POST':
        room.name = request.POST['name']
        room.description = request.POST['description']
        room.save()
        messages.success(request, 'Room updated successfully')
        return redirect('chatroom', room_id=room.id)

    return render(request, 'base/edit_room.html', {'room': room})

@login_required(login_url='login_register')
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if room.creator != request.user:
        return HttpResponseForbidden("You are not authorized to delete this room")

    if request.method == "POST":
        room.delete()
        messages.success(request, 'Room deleted successfully')
        return redirect('room_list')

    return render(request, 'base/confirm_delete.html', {
        'object': room,
        'type': 'room',
        'confirm_url': request.path
    })

@login_required(login_url='login_register')
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.user != request.user:
        return HttpResponseForbidden("You are not authorized to edit this message")

    if request.method == 'POST':
        message.content = request.POST['content']
        message.save()
        messages.success(request, 'Message updated successfully')
        return redirect('chatroom', room_id=message.room.id)

    return render(request, 'base/edit_message.html', {'message': message})

@login_required(login_url='login_register')
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this message")

    if request.method == "POST":
        room_id = message.room.id
        message.delete()
        messages.success(request, 'Message deleted successfully')
        return redirect('chatroom', room_id=room_id)

    return render(request, 'base/confirm_delete.html', {
        'object': message,
        'type': 'message',
        'confirm_url': request.path
    })

def login_register(request):
    if request.user.is_authenticated:
        return redirect('profile')  # Redirect authenticated users to the profile page

    page = request.GET.get('page', 'login')  # Default to login page

    # Handling POST request
    if request.method == 'POST':
        if page == 'login':  # Handling login form submission
            username = request.POST.get('username').lower()
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after successful login
            else:
                messages.error(request, 'Incorrect username or password')

        elif page == 'register':  # Handling registration form submission
            form = UserCreationForm(request.POST)
            profile_form = ProfileForm(request.POST)

            if form.is_valid() and profile_form.is_valid():
                # Create user from the form
                user = form.save(commit=False)
                user.username = user.username.lower()  # Ensure username is lowercase
                user.save()
                login(request, user)  # Log the user in immediately after registration

                # Create the profile for the user after registration
                profile = profile_form.save(commit=False)
                profile.user = user  # Link the profile to the user
                profile.save()

                messages.success(request, 'Registration successful!')
                return redirect('home')  # Redirect to home page after successful registration
            else:
                messages.error(request, 'An error occurred during registration.')

    else:  # Handling GET request
        form = None
        profile_form = None

        if page == 'register':
            form = UserCreationForm()  # Form for registration
            profile_form = ProfileForm()  # Form for the user's profile

    return render(request, 'base/login_register.html', {
        'form': form,               # Pass the form for registration or login
        'profile_form': profile_form,  # Pass the profile form if registering
        'page': page                # Keep track of the page (login or register)
    })

def logout_user(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login_register')
def profile(request):
    user = request.user
    password_form = PasswordChangeForm(user)
    rooms = Room.objects.filter(creator=user)

    if request.method == 'POST':
        if 'username' in request.POST:
            username = request.POST.get('username').lower()
            user.username = username
            user.save()
            messages.success(request, 'Username updated successfully.')
            return redirect('profile')

        if 'password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password updated successfully.')
                return redirect('profile')
            else:
                messages.error(request, 'Error updating password.')

    return render(request, 'base/profile.html', {
        'user': user, 
        'password_form': password_form, 
        'rooms': rooms 
    })

def add_to_comparison(request):
    """Handles adding a university to the comparison index."""
    if request.method == "POST":
        comparison_index = request.session.get('comparison_index', [])

        university = {
            "name": request.POST.get("name"),
            "city": request.POST.get("city"),
            "state": request.POST.get("state"),
            "acceptance_rate": request.POST.get("acceptance_rate"),
            "tuition": request.POST.get("tuition"),
            "size": request.POST.get("size"),
            "earnings_5yr": request.POST.get("earnings_5yr"),
            "earnings_10yr": request.POST.get("earnings_10yr"),
            "earn_count_3yr": request.POST.get("earn_count_3yr"),
        }

        if university not in comparison_index:
            comparison_index.append(university)
            request.session['comparison_index'] = comparison_index
            messages.success(request, f"{university['name']} added to comparison index.")
        else:
            messages.info(request, f"{university['name']} is already in the comparison index.")

    return redirect('find')