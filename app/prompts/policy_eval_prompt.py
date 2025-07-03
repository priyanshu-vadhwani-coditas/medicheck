POLICY_EVAL_PROMPT = """
You are an expert insurance policy evaluator. Given the following insurance policy and a patient's clinical summary (in JSON), determine if the patient is eligible for insurance approval under the policy. 

Return your answer in the following JSON format:
{{
  "policy_approved": true/false,
  "failed_criteria": ["..."],
  "policy_message": "A clear message for the user about approval or denial and why."
}}

Insurance Policy:
{policy}

Patient Clinical Summary:
{patient_json}
""" 