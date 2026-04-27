# 1. Summarization 
------------------
## Techniques Used
- Role Prompting
- Format Constraint
- Specificity

## Prompt
You are a business analyst. Summarize the following meeting notes into 5 bullet points for senior management. Highlight action items and keep it concise.

Text:
"The team discussed delayed delivery timelines, client concerns, new hiring needs, and automation opportunities."

## Sample Output
- Delivery timelines are delayed.
- Client raised concerns on deadlines.
- Additional hiring is required.
- Automation opportunities identified.
- Follow-up actions needed this week.






# 2. Sentiment Classification
-------------------------------
## Techniques Used
- Role Prompting
- Few-shot Examples
- Output Constraint

## Prompt
You are a sentiment classifier.

Examples:
"Great service" → Positive
"Very slow support" → Negative
"It was okay" → Neutral

Classify:
"The product quality is good but delivery was late."

Output:
One label only.

## Sample Output
Neutral







# 3. Entity Extraction
----------------------

## Techniques Used
- Specificity
- Format Constraint
- Structured Output

## Prompt
Extract the following entities from the text:
- Person Name
- Company
- City
- Date

Return output in JSON format only.

Text:
"Shraddha joined BSC Solutions in Bengaluru on 02nd February 2026."

## Sample Output
{
  "Person Name": "Shraddha",
  "Company": "BSC Solutions",
  "City": "Bengaluru",
  "Date": "02nd February 2026"
}






# 4. Q&A
----------

## Techniques Used
- Role Prompting
- Audience Targeting
- Specificity

## Prompt
You are a technical trainer. Answer the following question for a beginner using simple language and one example.

Question:
What is an API?

## Sample Output
An API is a way for two software systems to communicate. For example, a weather app uses an API to get live weather data from a server.








# 5. Rewriting
-----------------
## Techniques Used
- Role Prompting
- Tone Constraint
- Length Constraint

## Prompt
You are a professional communication assistant. Rewrite the following message in a polite and professional tone under 40 words.

Text:
"I am late because bike problem. Move meeting."

## Sample Output
I’m running late due to a bike issue. Apologies for the inconvenience. Could we please reschedule the meeting to a slightly later time?







