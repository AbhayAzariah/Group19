from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from .models import Room, Message
from .forms import MessageForm


# View for home page
def home(request):
    return render(request, 'base/home.html')

# View for finding a room
def find(request):
    return render(request, 'base/find.html')

# View for comparing rooms
def compare(request):
    return render(request, 'base/compare.html')

# View for listing rooms with pagination
def room_list(request):
    rooms = Room.objects.all().order_by('id')
    paginator = Paginator(rooms, 5)  # 5 rooms per page
    page = request.GET.get('page')
    rooms_paginated = paginator.get_page(page)
    return render(request, 'base/room_list.html', {'rooms': rooms_paginated})

# View for creating a room
@login_required(login_url='login_register')
def create_room(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        room = Room.objects.create(name=name, description=description, creator=request.user)
        return redirect('room_list')
    return render(request, 'base/create_room.html')

# View for chatroom with messages
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

# View for editing room details
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

# View for deleting a room
@login_required(login_url='login_register')
def delete_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if room.creator != request.user:
        return HttpResponseForbidden("You are not authorized to delete this room")

    room.delete()
    messages.success(request, 'Room deleted successfully')
    return redirect('room_list')

# View for editing message content
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

# View for deleting a message
@login_required(login_url='login_register')
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this message")

    message.delete()
    messages.success(request, 'Message deleted successfully')
    return redirect('chatroom', room_id=message.room.id)

# View for login and registration
def login_register(request):
    if request.user.is_authenticated:
        return redirect('profile')
   
    page = request.GET.get('page', 'login')

    if request.method == 'POST':
        if page == 'login':
            username = request.POST.get('username').lower()
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Incorrect username or password')


        elif page == 'register':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.save()
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'An error occurred during registration')

    else:
        if page == 'register':
            form = UserCreationForm()
        else:
            form = None

    return render(request, 'base/login_register.html', {'form': form, 'page': page})


# View for logging out the user
def logout_user(request):
    logout(request)
    return redirect('home')

# View for updating user profile
@login_required(login_url='login_register')
def profile(request):
    user = request.user
    password_form = PasswordChangeForm(user)

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

    return render(request, 'base/profile.html', {'user': user, 'password_form': password_form})