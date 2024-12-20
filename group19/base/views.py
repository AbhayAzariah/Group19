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
from django.http import JsonResponse
import openai
import json
import logging


# View for home page
def home(request):
    return render(request, 'base/home.html')

def room_list(request):
    query = request.GET.get('q', '')  # Get the search query from GET
    rooms = Room.objects.all()

    if query:
        rooms = rooms.filter(name__icontains=query) | rooms.filter(description__icontains=query)

    rooms = rooms.order_by('-created_at')

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
    form = None
    profile_form = None


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


    # Handling GET request or when POST fails
    else:
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
    
    # Initialize the ProfileForm with the current user's profile
    profile_form = ProfileForm(instance=user.profile)

    if request.method == 'POST':
        # Handling the username change
        if 'username' in request.POST:
            username = request.POST.get('username').lower()
            if username != user.username:
                user.username = username
                user.save()
                messages.success(request, 'Username updated successfully.')
                return redirect('profile')
            else:
                messages.error(request, 'The new username is the same as the current one.')

        # Handling the password change
        elif 'password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password updated successfully.')
                return redirect('profile')
            else:
                messages.error(request, 'Error updating password.')

        # Handling the profile update
        elif 'profile' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user.profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile')
            else:
                messages.error(request, 'Error updating profile.')

    return render(request, 'base/profile.html', {
        'user': user,
        'password_form': password_form,
        'profile_form': profile_form,
        'rooms': rooms,
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

#AA Views 
openai.api_key = "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"

logger = logging.getLogger(__name__)

def generate_recommendation(request):
    if request.method == "POST":
        try:
            # Attempt to retrieve the stored comparison index from the session
            comparison_index = request.session.get('stored_comparison_index', [])

            # If there is no stored data, try to load it from the request body
            if not comparison_index:
                body = json.loads(request.body)
                incoming_index = body.get("comparison_index", [])
                if incoming_index:
                    # Store the incoming comparison index in the session
                    request.session['stored_comparison_index'] = incoming_index
                    comparison_index = incoming_index
                else:
                    # No stored data and no data in the request
                    return JsonResponse({"success": False, "message": "No stored data found. Please store data first."})

            # Prepare the GPT-4 prompt using the comparison index
            prompt = (
                "You are an expert academic advisor. Based on the user's profile and the comparison index of graduate schools, "
                "generate tailored recommendations. Mention likelihoods based on their GPAs and overall profile. Mention pros and cons of the school, "
                "based on factors such as location and campus type (urban, suburban, rural). Try to be as quantitative as possible and use the data provided. "
                "Here is the data:\n\n"
                f"Comparison Index: {comparison_index}"
            )

            # Call GPT-4
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an academic advisor assistant."},
                    {"role": "user", "content": prompt},
                ],
            )

            recommendations = response.choices[0].message.content
            logger.debug(f"OpenAI response: {recommendations}")
            return JsonResponse({"success": True, "recommendations": recommendations})

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)

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

def compare(request):
    return render(request, 'base/compare.html')

def room_list(request):
    query = request.GET.get('q', '')  
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

def store_comparison_data(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            comparison_index = body.get("comparison_index", [])

            if not comparison_index:
                return JsonResponse({"success": False, "message": "Comparison index is empty."})

            # Store comparison_index in the session
            request.session['stored_comparison_index'] = comparison_index
            return JsonResponse({"success": True, "message": "Data stored successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)