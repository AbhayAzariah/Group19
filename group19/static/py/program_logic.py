import requests
import openai


# Configure the OpenAI API key
openai.api_key = "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"


API_KEY = "gVaGW1IWY2gYQtinNU1z2aXQ5YxAfOM6175bQzmt"
BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"




def fetch_school_details(name):
    """
    Fetches detailed information about schools filtered by name, ensuring they offer graduate degrees.
    :param name: School name (partial or full).
    :return: List of schools matching the name with details.
    """
    params = {
        "api_key": API_KEY,
        "fields": "id,school.name,school.city,school.state,latest.admissions.admission_rate.overall,"
                  "latest.cost.tuition.out_of_state,latest.student.size,"
                  "latest.earnings.EARN_MDN_5YR,latest.earnings.10_yrs_after_entry.median,"
                  "latest.earnings.EARN_COUNT_WNE_3YR",
        "school.name": name,
        "school.degrees_awarded.highest": 4  # Filter for schools offering graduate degrees
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the API: {e}")
        return []




def rank_campus_preferences():
    """Prompts the user to rank their campus type preferences."""
    print("\nRank your preferences for campus type:")
    options = ["Rural", "Suburban", "Urban"]
    rankings = {}


    for i in range(1, 4):
        while True:
            choice = input(f"Enter your choice for rank {i} ({', '.join(options)}): ").strip()
            if choice in options:
                rankings[f"Rank {i}"] = choice
                options.remove(choice)
                break
            else:
                print("Invalid choice. Please choose from the remaining options.")


    return rankings




def create_profile():
    """Creates and stores a user profile with GPA, test scores, campus preferences, recommendation letters, and desired major."""
    print("\nCreate Your Profile:")
    profile = {}


    while True:
        gpa = input("Enter your undergraduate GPA (0.0 - 4.0): ").strip()
        try:
            gpa = float(gpa)
            if 0.0 <= gpa <= 4.0:
                profile['GPA'] = gpa
                break
            else:
                print("GPA must be between 0.0 and 4.0.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


    print("\nDo you want to include test scores?")
    print("1. GRE")
    print("2. GMAT")
    print("3. Neither")
    test_choice = input("Choose an option: ").strip()
    if test_choice == "1":
        while True:
            try:
                verbal = int(input("Enter your GRE Verbal score (130-170): ").strip())
                quant = int(input("Enter your GRE Quantitative score (130-170): ").strip())
                if 130 <= verbal <= 170 and 130 <= quant <= 170:
                    profile['GRE'] = {"Verbal": verbal, "Quantitative": quant, "Total": verbal + quant}
                    break
                else:
                    print("Scores must be between 130 and 170.")
            except ValueError:
                print("Invalid input.")
    elif test_choice == "2":
        while True:
            try:
                data_insight = int(input("Enter your GMAT Data Insight score (60-90): ").strip())
                verbal = int(input("Enter your GMAT Verbal Reasoning score (60-90): ").strip())
                quant = int(input("Enter your GMAT Quantitative Reasoning score (60-90): ").strip())
                if 60 <= data_insight <= 90 and 60 <= verbal <= 90 and 60 <= quant <= 90:
                    profile['GMAT'] = {"Data Insight": data_insight, "Verbal Reasoning": verbal, "Quantitative Reasoning": quant, "Total": data_insight + verbal + quant}
                    break
                else:
                    print("Scores must be between 60 and 90.")
            except ValueError:
                print("Invalid input.")
    else:
        profile['Test Optional'] = True


    while True:
        try:
            letters = int(input("How many letters of recommendation will you have (0-5)? ").strip())
            if 0 <= letters <= 5:
                profile['Letters of Recommendation'] = letters
                break
            else:
                print("Number of letters must be between 0 and 5.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


    profile['Campus Preferences'] = rank_campus_preferences()


    major = input("Enter your desired Graduate Program: ").strip()
    profile['Major'] = major


    print("\nProfile created successfully!")
    for key, value in profile.items():
        print(f"{key}: {value}")


    return profile




def display_schools(schools):
    """Displays a list of schools with detailed information."""
    if not schools:
        print("No schools found offering graduate degrees.")
    else:
        print("\nMatching Schools:")
        for index, school in enumerate(schools, start=1):
            name = school.get("school.name", "N/A")
            location = f"{school.get('school.city', 'N/A')}, {school.get('school.state', 'N/A')}"
            acceptance_rate = school.get("latest.admissions.admission_rate.overall")
            cost = school.get("latest.cost.tuition.out_of_state", "N/A")
            size = school.get("latest.student.size", "N/A")
            earnings_5yr = school.get("latest.earnings.EARN_MDN_5YR", "N/A")
            earnings_10yr = school.get("latest.earnings.10_yrs_after_entry.median", "N/A")
            earn_count_3yr = school.get("latest.earnings.EARN_COUNT_WNE_3YR", "N/A")


            if acceptance_rate is not None:
                acceptance_rate = f"{acceptance_rate * 100:.2f}%"
            else:
                acceptance_rate = "N/A"


            if earnings_5yr != "N/A":
                earnings_5yr = f"${earnings_5yr:,}"
            if earnings_10yr != "N/A":
                earnings_10yr = f"${earnings_10yr:,}"
            if earn_count_3yr != "N/A":
                earn_count_3yr = f"{earn_count_3yr:,} graduates working and not enrolled"


            print(f"{index}. {name}")
            print(f"   Location: {location}")
            print(f"   Acceptance Rate: {acceptance_rate}")
            print(f"   Cost (Out-of-State): ${cost:,} (if available)")
            print(f"   Student Body Size: {size}")
            print(f"   Median Earnings (5 years after graduation): {earnings_5yr}")
            print(f"   Median Earnings (10 years after entry): {earnings_10yr}")
            print(f"   Graduates Working (Not Enrolled, 3 Years): {earn_count_3yr}\n")




def add_to_comparison(comparison_index, school):
    """Adds a school to the comparison index."""
    comparison_index.append(school)
    print(f"Added {school['school.name']} to the comparison index.")




def display_comparison_index(comparison_index):
    """Displays the comparison index with detailed information."""
    if not comparison_index:
        print("The comparison index is empty.")
    else:
        print("\nComparison Index:")
        for index, school in enumerate(comparison_index, start=1):
            name = school.get("school.name", "N/A")
            location = f"{school.get('school.city', 'N/A')}, {school.get('school.state', 'N/A')}"
            acceptance_rate = school.get("latest.admissions.admission_rate.overall")
            cost = school.get("latest.cost.tuition.out_of_state", "N/A")
            size = school.get("latest.student.size", "N/A")
            earnings_5yr = school.get("latest.earnings.EARN_MDN_5YR", "N/A")
            earnings_10yr = school.get("latest.earnings.10_yrs_after_entry.median", "N/A")
            earn_count_3yr = school.get("latest.earnings.EARN_COUNT_WNE_3YR", "N/A")


            if acceptance_rate is not None:
                acceptance_rate = f"{acceptance_rate * 100:.2f}%"
            else:
                acceptance_rate = "N/A"


            if earnings_5yr != "N/A":
                earnings_5yr = f"${earnings_5yr:,}"
            if earnings_10yr != "N/A":
                earnings_10yr = f"${earnings_10yr:,}"
            if earn_count_3yr != "N/A":
                earn_count_3yr = f"{earn_count_3yr:,} graduates working and not enrolled"


            print(f"{index}. {name}")
            print(f"   Location: {location}")
            print(f"   Acceptance Rate: {acceptance_rate}")
            print(f"   Cost (Out-of-State): ${cost:,} (if available)")
            print(f"   Student Body Size: {size}")
            print(f"   Median Earnings (5 years after graduation): {earnings_5yr}")
            print(f"   Median Earnings (10 years after entry): {earnings_10yr}")
            print(f"   Graduates Working (Not Enrolled, 3 Years): {earn_count_3yr}\n")




def generate_recommendations(comparison_index, user_profile):
    """
    Sends the comparison index and user profile to GPT-4 to generate recommendations.
    """
    try:
        prompt = (
            "You are an expert academic advisor. Based on the user's profile and the comparison index of graduate schools, "
            "generate tailored recommendations. Mention likelihoods based on their GPAs and overall profile. Mention pros and cons of the school, based on things like Location, the type of campus (urban, etc). Try to be as quantitative as possible. Reference mostly objective Metrics. The acceptance rate I gave you is for undergraduate, it is not super relevant here. I only provided it as a point of reference for the school's selectivity. Same with salary, it is only a point of reference to gauge how successful the graduates are. Based on their profile and desired goals, mention 3 other recommendations. One reach, one target and one safety. Remember, these are grad school admissions."
            f"{comparison_index}, {user_profile}"
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
        return recommendations


    except openai.error.OpenAIError as e:
        print(f"Error communicating with GPT-4: {e}")
        return None




def main():
    print("Welcome to the Grad School Comparison Program!")
    print("\nBefore proceeding, you need to create your profile.")


    # Force user to create a profile
    user_profile = create_profile()


    comparison_index = []


    while True:
        print("\nMenu:")
        print("1. Search for a university")
        print("2. View comparison index")
        print("3. Generate recommendations")
        print("4. Exit")
        choice = input("Choose an option: ").strip()


        if choice == "1":
            name = input("Enter the university name (or part of it): ").strip()
            schools = fetch_school_details(name)
            display_schools(schools)


            if schools:
                selection = input("Enter the number of the university to add to the comparison index (or 'q' to cancel): ").strip()
                if selection.isdigit() and 1 <= int(selection) <= len(schools):
                    add_to_comparison(comparison_index, schools[int(selection) - 1])
                elif selection.lower() != 'q':
                    print("Invalid selection.")


        elif choice == "2":
            display_comparison_index(comparison_index)


        elif choice == "3":
            if not comparison_index:
                print("Comparison index is empty. Add schools before generating recommendations.")
            else:
                recommendations = generate_recommendations(comparison_index, user_profile)
                if recommendations:
                    print("\nRecommendations:\n")
                    print(recommendations)


        elif choice == "4":
            print("Goodbye!")
            break


        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()