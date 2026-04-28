import json
import pandas as pd

# Input Text
text = "Shraddha joined BSC Solutions in Bengaluru on 02 February 2026 as a Boomi Developer."

# 3 Prompt Versions
prompts = {
    "Version 1": "Extract details from this text.",
    
    "Version 2": "Extract name, company, city, date, and role from the text. Return in JSON format.",
    
    "Version 3": """   You are an information extraction assistant.
                    Extract:name, company, city, date, role

                        Rules:
                        - Return valid JSON only
                        - Use exact values
                        - If missing, use null
                        """
}


# Simulated Outputs
# (Normally these would come from an LLM API)- I am predicting the outputs based on the prompts and input text
outputs = {
    "Version 1": {
        "name": "Shraddha",
        "company": "BSC Solutions",
        "city": "Bengaluru"
    },

    "Version 2": {
        "name": "Shraddha",
        "company": "BSC Solutions",
        "city": "Bengaluru",
        "date": "02 February 2026",
        "role": "Boomi Developer"
    },

    "Version 3": {
        "name": "Shraddha",
        "company": "BSC Solutions",
        "city": "Bengaluru",
        "date": "02 February 2026",
        "role": "Boomi Developer"
    }
}

# Expected Fields
required_fields = ["name", "company", "city", "date", "role"]

# Scoring Function
def evaluate(output):
    # Accuracy = number of correct fields
    accuracy = sum(1 for field in required_fields if field in output)

    # Scale to 5
    accuracy_score = round((accuracy / 5) * 5)

    # Format score
    format_score = 5 if isinstance(output, dict) else 2

    # Consistency score
    consistency_score = 5 if len(output.keys()) == len(set(output.keys())) else 3

    return accuracy_score, format_score, consistency_score

# Evaluate All Versions
results = []

for version, output in outputs.items():
    acc, fmt, cons = evaluate(output)
    total = acc + fmt + cons

    results.append({
        "Prompt Version": version,
        "Accuracy": acc,
        "Format": fmt,
        "Consistency": cons,
        "Total": total
    })

# Create DataFrame
df = pd.DataFrame(results)

print("\n=== Evaluation Table ===")
print(df)

# Save CSV
df.to_csv("scores.csv", index=False)

# Save JSON Outputs
with open("results.json", "w", encoding="utf-8") as f:
    json.dump(outputs, f, indent=4)

