VALIDATOR_SUGGESTION_PROMPT = """
Given the following clinical summary data (in JSON) and a list of missing or invalid fields, determine if the data is valid for insurance purposes. If not, provide a clear, friendly explanation for a user about what is missing or needs to be fixed, and suggest how to correct it.

Return your answer in the following JSON format:
{{
  "is_valid": true/false,
  "missing_fields": ["..."],
  "suggestions": ["...", "..."]
}}

Data:
{data}

Missing/Invalid fields:
{missing_fields}

Your response should be concise and easy to understand.
""" 