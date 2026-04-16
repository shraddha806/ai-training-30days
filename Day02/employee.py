import json

employees = [
    {"name": "Shraddha", "department": "Engineering", "salary": 90000},
    {"name": "Harshini", "department": "HR", "salary": 50000},
    {"name": "Naresh", "department": "Engineering", "salary": 75000},
    {"name": "Suneel", "department": "Sales", "salary": 60000},                     
]

# 1. Count per department
count = {}

for emp in employees:
    dept = emp["department"]
    count[dept] = count.get(dept, 0) + 1

print("Count:", count)

# 2. Highest salary
highest = max(employees, key=lambda x: x["salary"])
print("Highest Salary:", highest)

# 3. Save Engineering team
engineering = []

for emp in employees:
    if emp["department"] == "Engineering":
        engineering.append(emp)

with open("engineering.json", "w") as file:
    json.dump(engineering, file, indent=4)
