from datetime import date

def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def calculate_bmi(weight: float, height: float) -> float:
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)

def get_body_type(bmi: float) -> str:
    if bmi < 18.5: return "underweight"
    if bmi < 25:   return "normal"
    if bmi < 30:   return "overweight"
    return "obese"

def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    # Mifflin-St Jeor (consistent with your original code)
    if gender.lower() == "male":
        return round((10 * weight) + (6.25 * height) - (5 * age) + 5, 2)
    return round((10 * weight) + (6.25 * height) - (5 * age) - 161, 2)

def calculate_tedd(bmr: float, activity_level: str) -> float:
    multipliers = {
        "sedentary":  1.2,
        "light":      1.375,
        "moderate":   1.55,
        "active":     1.725,
        "very_active": 1.9
    }
    return round(bmr * multipliers.get(activity_level, 1.2), 2)

def calcutaed_calories_adjustment(tdee: float, goal_type: str) -> float:
    if goal_type == "lose":    return round(tdee - 500, 2)
    if goal_type == "gain":    return round(tdee + 500, 2)
    return round(tdee, 2)