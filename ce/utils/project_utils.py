from datetime import date
from datetime import timedelta

# current_project = 21
# project_start = date(2024, 10, 14)


""" >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  CALCULATE AND VALIDATE PROJECT DATES <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< """


# noinspection PyShadowingNames
def calculate_project_dates(project_start):
    """
    Input:      Project start date

    Output:     1) Project end date
                2) Start date of following years project
                3) End date of following years project
    """
    project_end = project_start + timedelta(weeks=52) - timedelta(days=3)
    next_project_start = project_end + timedelta(days=3)
    next_project_end = next_project_start + timedelta(weeks=52) - timedelta(days=3)

    return project_end, next_project_start, next_project_end


def validate_participant_start_date(participant_start, project_start, current_project):
    """
    Input:          Participant start date

    Validations:    1)  Checks that the start date falls within current years project
                        elif: following years project.
                    2)  Checks that start date falls on a Monday
    """

    # Get date ranges from the above 'calculate_project_dates' function
    project_end, next_project_start, next_project_end = calculate_project_dates(project_start)

    # Validate user entered a valid date within range
    if project_start <= participant_start <= project_end:
        # Participant belongs to current project: Continue silently
        pass
    elif next_project_start <= participant_start <= next_project_end:
        print(f"⚠️ Participant start date falls within Project {current_project + 1} "
              f"({next_project_start} to {next_project_end}). Is this correct?")
        return
    else:
        print("❌ Participant start date is invalid")
        return

    # Check if participant starts on a Monday
    if participant_start.weekday() != 0:
        print("❌ Error: Participant must start on a Monday.")
    else:
        print("✅ Participant start date is valid.")
