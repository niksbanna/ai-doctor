"""
Example usage of the AI Physician Assistant
"""

from ai_doctor import PhysicianAssistant, PatientInput
from ai_doctor.models import Symptom, MedicalHistory, Severity

def example_common_cold():
    """Example: Patient with common cold symptoms"""
    print("=" * 60)
    print("EXAMPLE 1: Common Cold")
    print("=" * 60)
    
    # Create patient input
    patient = PatientInput(
        patient_id="ANON-001",
        age=35,
        sex="F",
        chief_complaint="Runny nose and cough for 3 days",
        symptoms=[
            Symptom(
                name="Runny nose",
                duration="3 days",
                severity=Severity.MILD
            ),
            Symptom(
                name="Cough",
                duration="3 days",
                severity=Severity.MILD
            ),
            Symptom(
                name="Sore throat",
                duration="2 days",
                severity=Severity.MILD
            )
        ],
        medical_history=MedicalHistory()
    )
    
    # Perform assessment
    assistant = PhysicianAssistant()
    assessment = assistant.assess_patient(patient)
    
    # Print summary
    print(assessment.summary)
    print("\n" + "=" * 60)
    
    # Save JSON output
    with open('/tmp/example_common_cold.json', 'w') as f:
        f.write(assistant.to_json(assessment))
    print("Full JSON saved to: /tmp/example_common_cold.json")
    
    return assessment


def example_emergency_chest_pain():
    """Example: Emergency presentation with chest pain"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Emergency - Chest Pain")
    print("=" * 60)
    
    patient = PatientInput(
        patient_id="ANON-002",
        age=58,
        sex="M",
        chief_complaint="Severe chest pain",
        symptoms=[
            Symptom(
                name="Crushing chest pain",
                duration="30 minutes",
                severity=Severity.SEVERE,
                additional_details="Pressure-like pain radiating to left arm"
            ),
            Symptom(
                name="Shortness of breath",
                duration="30 minutes",
                severity=Severity.SEVERE
            ),
            Symptom(
                name="Sweating",
                duration="30 minutes",
                severity=Severity.MODERATE
            )
        ],
        medical_history=MedicalHistory(
            chronic_conditions=["Hypertension", "High cholesterol"],
            current_medications=["Lisinopril 10mg daily", "Atorvastatin 40mg daily"]
        ),
        vital_signs={
            "heart_rate": 105,
            "systolic_bp": 160,
            "diastolic_bp": 95,
            "oxygen_saturation": 94
        }
    )
    
    assistant = PhysicianAssistant()
    assessment = assistant.assess_patient(patient)
    
    print(assessment.summary)
    print("\n" + "=" * 60)
    
    with open('/tmp/example_emergency_chest_pain.json', 'w') as f:
        f.write(assistant.to_json(assessment))
    print("Full JSON saved to: /tmp/example_emergency_chest_pain.json")
    
    return assessment


def example_medication_interaction():
    """Example: Patient on warfarin needing pain management"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Medication Safety Check")
    print("=" * 60)
    
    patient = PatientInput(
        patient_id="ANON-003",
        age=72,
        sex="F",
        chief_complaint="Back pain",
        symptoms=[
            Symptom(
                name="Lower back pain",
                duration="1 week",
                severity=Severity.MODERATE
            )
        ],
        medical_history=MedicalHistory(
            chronic_conditions=["Atrial fibrillation", "Osteoarthritis"],
            current_medications=["Warfarin 5mg daily"],
            allergies=[]
        )
    )
    
    assistant = PhysicianAssistant()
    assessment = assistant.assess_patient(patient)
    
    print(assessment.summary)
    
    if assessment.medication_safety_checks:
        print("\n" + "-" * 60)
        print("MEDICATION SAFETY CHECKS:")
        for med_check in assessment.medication_safety_checks:
            print(f"\nMedication: {med_check.medication}")
            print(f"Safe: {'Yes' if med_check.is_safe else 'No'}")
            if med_check.interactions:
                print("Interactions:", ", ".join(med_check.interactions))
            if med_check.warnings:
                print("Warnings:", ", ".join(med_check.warnings))
    
    print("\n" + "=" * 60)
    
    with open('/tmp/example_medication_interaction.json', 'w') as f:
        f.write(assistant.to_json(assessment))
    print("Full JSON saved to: /tmp/example_medication_interaction.json")
    
    return assessment


def example_pediatric_fever():
    """Example: Pediatric patient with fever"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Pediatric Fever")
    print("=" * 60)
    
    patient = PatientInput(
        patient_id="ANON-004",
        age=1,
        sex="M",
        chief_complaint="Fever and irritability",
        symptoms=[
            Symptom(
                name="Fever",
                duration="6 hours",
                severity=Severity.MODERATE,
                additional_details="Temperature 102.5°F"
            ),
            Symptom(
                name="Irritability",
                duration="6 hours",
                severity=Severity.MODERATE
            ),
            Symptom(
                name="Poor feeding",
                duration="6 hours",
                severity=Severity.MODERATE
            )
        ],
        medical_history=MedicalHistory(),
        vital_signs={
            "temperature": 102.5,
            "heart_rate": 145
        }
    )
    
    assistant = PhysicianAssistant()
    assessment = assistant.assess_patient(patient)
    
    print(assessment.summary)
    print("\n" + "=" * 60)
    
    with open('/tmp/example_pediatric_fever.json', 'w') as f:
        f.write(assistant.to_json(assessment))
    print("Full JSON saved to: /tmp/example_pediatric_fever.json")
    
    return assessment


def main():
    """Run all examples"""
    print("\n")
    print("🏥 AI PHYSICIAN ASSISTANT - EXAMPLES")
    print("=" * 60)
    print("Demonstrating comprehensive medical assessment capabilities")
    print("=" * 60)
    
    # Run examples
    example_common_cold()
    example_emergency_chest_pain()
    example_medication_interaction()
    example_pediatric_fever()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
    print("\nKEY FEATURES DEMONSTRATED:")
    print("✓ Symptom collection and analysis")
    print("✓ Red flag detection (rule-based safety)")
    print("✓ Differential diagnosis with confidence scores")
    print("✓ Emergency escalation")
    print("✓ Medication safety checks")
    print("✓ Age-specific considerations")
    print("✓ Structured JSON output")
    print("✓ Human-readable summaries")
    print("✓ FHIR/SNOMED/ICD-10 standards")
    print("✓ Mandatory clinician verification disclaimer")
    print("\n")


if __name__ == "__main__":
    main()
