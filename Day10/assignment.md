# Prompt Evaluation Sheet

## Objective
Test 3 versions of the same prompt and evaluate output quality on accuracy, format, and consistency.

# Input Text
Shraddha joined BSC Solutions in Bengaluru on 02 February 2026 as a Boomi Developer.


# Prompt Version 1 (Basic)
--------------------------
## Prompt
Extract details from this text.

## JSON Result
{
  "name": "Shraddha",
  "company": "BSC Solutions",
  "city": "Bengaluru"
}

## Evaluation
- Accuracy: 3
- Format: 2
- Consistency: 2

## Observation
Some fields were missing. Output format was incomplete.


# Prompt Version 2 (Improved)
-----------------------------
## Prompt
Extract name, company, city, date, and role from the text. Return in JSON format.

## JSON Result
{
  "name": "Shraddha",
  "company": "BSC Solutions",
  "city": "Bengaluru",
  "date": "02 February 2026",
  "role": "Boomi Developer"
}

## Evaluation
- Accuracy: 5
- Format: 4
- Consistency: 4

## Observation
All fields were extracted. Format improved due to JSON instruction.


# Prompt Version 3 (Best)
-------------------------
## Prompt
You are an information extraction assistant.

Extract the following fields from the text:
- name
- company
- city
- date
- role

Rules:
- Return valid JSON only
- Use exact values from text
- If missing, use null

Text:
Shraddha joined BSC Solutions in Bengaluru on 02 February 2026 as a Boomi Developer.

## JSON Result
{
  "name": "Shraddha",
  "company": "BSC Solutions",
  "city": "Bengaluru",
  "date": "02 February 2026",
  "role": "Boomi Developer"
}

## Evaluation
- Accuracy: 5
- Format: 5
- Consistency: 5

## Observation
Best result. Role prompting, clear fields, and strict formatting produced reliable structured output.


# Final Evaluation Table

| Prompt Version | Accuracy | Format | Consistency | Total |
|---------------|----------|--------|------------|------|
| Version 1 | 3 | 2 | 2 | 7 |
| Version 2 | 5 | 4 | 4 | 13 |
| Version 3 | 5 | 5 | 5 | 15 |

# What Changed Across Versions

1. Version 1 was vague and incomplete.
2. Version 2 improved by specifying fields and JSON output.
3. Version 3 performed best due to role prompting, explicit rules, and strict output constraints.

---

# Final Conclusion

More specific prompts with structure and constraints lead to higher-quality and more consistent AI outputs.