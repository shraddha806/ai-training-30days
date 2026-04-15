import json

# Load students data from JSON file
with open("students.json", "r") as file:
    students = json.load(file)

# Print names where marks > 70
print("Students with marks > 70:\n")

for student in students:
    if student["marks"] > 70:
        print(student["name"])
        

        