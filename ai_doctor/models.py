"""
Data models for the AI physician assistant.
Uses Pydantic for data validation and FHIR/SNOMED/ICD-10 standards.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timezone
from enum import Enum


class Severity(str, Enum):
    """Severity levels for symptoms and conditions"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class UrgencyLevel(str, Enum):
    """Urgency levels for medical attention"""
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    LIFE_THREATENING = "life_threatening"


class Symptom(BaseModel):
    """Represents a patient symptom with SNOMED CT coding"""
    name: str = Field(..., description="Name of the symptom")
    duration: str = Field(..., description="Duration of the symptom")
    severity: Severity = Field(default=Severity.MILD, description="Severity of the symptom")
    snomed_code: Optional[str] = Field(None, description="SNOMED CT code")
    additional_details: Optional[str] = Field(None, description="Additional symptom details")


class MedicalHistory(BaseModel):
    """Patient's medical history"""
    chronic_conditions: List[str] = Field(default_factory=list, description="Chronic medical conditions")
    past_surgeries: List[str] = Field(default_factory=list, description="Past surgical procedures")
    allergies: List[str] = Field(default_factory=list, description="Known allergies")
    current_medications: List[str] = Field(default_factory=list, description="Current medications")
    family_history: List[str] = Field(default_factory=list, description="Relevant family medical history")


class PatientInput(BaseModel):
    """Complete patient input data"""
    patient_id: Optional[str] = Field(None, description="Anonymized patient identifier")
    age: int = Field(..., ge=0, le=150, description="Patient age in years")
    sex: str = Field(..., description="Patient biological sex (M/F/Other)")
    chief_complaint: str = Field(..., description="Primary reason for consultation")
    symptoms: List[Symptom] = Field(..., description="List of symptoms")
    medical_history: MedicalHistory = Field(default_factory=MedicalHistory, description="Patient medical history")
    vital_signs: Optional[Dict[str, Any]] = Field(None, description="Current vital signs if available")

    @field_validator('sex')
    @classmethod
    def validate_sex(cls, v):
        allowed = ['M', 'F', 'Male', 'Female', 'Other', 'Unknown']
        if v not in allowed:
            raise ValueError(f'Sex must be one of {allowed}')
        return v


class RedFlag(BaseModel):
    """Represents a medical red flag (warning sign)"""
    flag: str = Field(..., description="Description of the red flag")
    severity: Severity = Field(..., description="Severity level")
    urgency: UrgencyLevel = Field(..., description="Required urgency of action")
    reasoning: str = Field(..., description="Why this is a red flag")


class Diagnosis(BaseModel):
    """Differential diagnosis with confidence scoring"""
    condition: str = Field(..., description="Name of the condition")
    icd10_code: Optional[str] = Field(None, description="ICD-10 code")
    snomed_code: Optional[str] = Field(None, description="SNOMED CT code")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Reasoning for this diagnosis")
    supporting_evidence: List[str] = Field(default_factory=list, description="Supporting clinical evidence")


class Investigation(BaseModel):
    """Recommended medical investigation"""
    test_name: str = Field(..., description="Name of the test/investigation")
    loinc_code: Optional[str] = Field(None, description="LOINC code for laboratory tests")
    urgency: UrgencyLevel = Field(..., description="Urgency of the investigation")
    reasoning: str = Field(..., description="Why this investigation is recommended")


class Management(BaseModel):
    """Preliminary management recommendation"""
    intervention: str = Field(..., description="Recommended intervention")
    category: str = Field(..., description="Category (medication/lifestyle/monitoring/referral)")
    safety_considerations: List[str] = Field(default_factory=list, description="Safety considerations")
    contraindications_checked: bool = Field(default=True, description="Whether contraindications were checked")


class MedicationSafety(BaseModel):
    """Medication safety check results"""
    medication: str = Field(..., description="Medication name")
    is_safe: bool = Field(..., description="Whether medication is safe for this patient")
    interactions: List[str] = Field(default_factory=list, description="Potential drug interactions")
    contraindications: List[str] = Field(default_factory=list, description="Contraindications found")
    warnings: List[str] = Field(default_factory=list, description="Important warnings")


class ClinicalEvidence(BaseModel):
    """Clinical evidence and citations"""
    statement: str = Field(..., description="Clinical statement")
    evidence_level: str = Field(..., description="Level of evidence (A/B/C)")
    source: str = Field(..., description="Source of evidence")
    reference: Optional[str] = Field(None, description="Reference citation")


class MedicalAssessment(BaseModel):
    """Complete medical assessment output"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "timestamp": "2024-01-01T12:00:00Z",
            "patient_id": "ANON-12345",
            "red_flags": [],
            "differential_diagnoses": [
                {
                    "condition": "Viral Upper Respiratory Infection",
                    "icd10_code": "J06.9",
                    "confidence": 0.75,
                    "reasoning": "Consistent with symptoms and duration"
                }
            ],
            "overall_urgency": "routine",
            "summary": "Assessment summary here"
        }
    })
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Assessment timestamp")
    patient_id: Optional[str] = Field(None, description="Anonymized patient identifier")
    
    # Core assessment components
    red_flags: List[RedFlag] = Field(default_factory=list, description="Identified red flags")
    differential_diagnoses: List[Diagnosis] = Field(..., description="Differential diagnoses ranked by confidence")
    recommended_investigations: List[Investigation] = Field(default_factory=list, description="Recommended tests")
    preliminary_management: List[Management] = Field(default_factory=list, description="Preliminary management plan")
    
    # Safety and reasoning
    medication_safety_checks: List[MedicationSafety] = Field(default_factory=list, description="Medication safety results")
    clinical_reasoning: str = Field(..., description="Detailed clinical reasoning")
    evidence_citations: List[ClinicalEvidence] = Field(default_factory=list, description="Evidence and citations")
    
    # Urgency and escalation
    overall_urgency: UrgencyLevel = Field(..., description="Overall urgency level")
    emergency_indicators: List[str] = Field(default_factory=list, description="Emergency indicators if present")
    escalation_required: bool = Field(default=False, description="Whether immediate escalation is required")
    
    # Mandatory disclaimers
    clinician_verification_required: str = Field(
        default="⚠️ CLINICIAN VERIFICATION REQUIRED: This assessment is generated by an AI system and must be verified by a qualified healthcare professional before any clinical decision-making.",
        description="Mandatory clinician verification disclaimer"
    )
    
    # Privacy and compliance
    privacy_notice: str = Field(
        default="Patient privacy protected. All data handled according to HIPAA/GDPR standards.",
        description="Privacy notice"
    )
    
    # Summary
    summary: str = Field(..., description="Human-readable summary of the assessment")
