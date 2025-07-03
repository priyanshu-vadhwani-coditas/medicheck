VALIDATOR_SUGGESTION_PROMPT = """
Given the following clinical summary data (in JSON) and a list of missing or invalid fields, 
write a clear, friendly explanation for a user about what is missing or needs to be fixed, 
and suggest how to correct it.

Data:
{data}

Missing/Invalid fields:
{missing_fields}

Your response should be concise and easy to understand.
""" 