from django.shortcuts import render
from django.http import JsonResponse
from .program_logic import fetch_school_details

def compare_view(request):
    # Get or initialize the comparison index
    comparison_index = request.session.get("comparison_index", [])

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add":
            # Add a university to the comparison index
            university_name = request.POST.get("university")
            if university_name:
                details = fetch_school_details(university_name)
                if details:  # Add only if results are returned
                    comparison_index.append(details[0])  # Use the first matching result
                    request.session["comparison_index"] = comparison_index

        elif action == "clear":
            # Clear the comparison index
            comparison_index = []
            request.session["comparison_index"] = comparison_index

    return render(request, "base/compare.html", {
        "comparison_index": comparison_index,
    })
