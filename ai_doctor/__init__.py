"""
AI Doctor - General Physician Assistant
A comprehensive AI-powered medical assistant that collects symptoms, identifies red flags,
generates differential diagnoses, recommends investigations, and provides safe preliminary management.
"""

__version__ = "1.0.0"
__author__ = "AI Doctor Team"

from .physician_assistant import PhysicianAssistant
from .models import PatientInput, MedicalAssessment

__all__ = ["PhysicianAssistant", "PatientInput", "MedicalAssessment"]
