from pydantic import BaseModel, Field
from typing import List, Optional

class Vitals(BaseModel):
    blood_pressure: str
    heart_rate: int
    temperature: float

class PatientDemographics(BaseModel):
    full_name: str
    age: int
    gender: str
    weight: float
    insurance_id: str
    alcohol_use: Optional[bool] = False
    smoking: Optional[bool] = False
    substance_addiction: Optional[bool] = False

class HPI(BaseModel):
    chief_complaint: str
    duration: str
    onset: str
    associated_symptoms: List[str]
    documentation_date: str  # Required, not optional
    vitals: Optional[Vitals] = None

class PastMedicalHistory(BaseModel):
    chronic_illnesses: List[str]
    surgical_history: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    medication_history: Optional[List[str]] = []

class ProcedureOrTreatment(BaseModel):
    date: str
    procedure_name: str
    performing_physician: str
    justification: str
    referral_note_attached: Optional[bool] = False

class ImagingLabResult(BaseModel):
    type: str  # e.g., X-Ray, CT, MRI, CBC
    date: str
    findings: str
    interpretation: Optional[str] = None

class DiagnosisDischargeSummary(BaseModel):
    final_diagnosis: str
    icd_10_code: str = Field(..., min_length=1)  # Required non-empty string
    treatment_summary: str
    discharge_plan: str

class PhysicianSignature(BaseModel):
    attending_physician: str
    date_of_report: str
    digital_signature: str

class ClinicalSummary(BaseModel):
    patient_demographics: PatientDemographics
    hpi: HPI
    past_medical_history: PastMedicalHistory
    procedures_treatments: List[ProcedureOrTreatment] = Field(..., min_items=1)  # Require at least one
    imaging_lab_results: List[ImagingLabResult]
    diagnosis_discharge_summary: DiagnosisDischargeSummary
    physician_signature: PhysicianSignature 