"""
Test cases for the AI Physician Assistant
"""

import pytest
from ai_doctor import PhysicianAssistant, PatientInput
from ai_doctor.models import Symptom, MedicalHistory, Severity, UrgencyLevel


class TestPhysicianAssistant:
    """Test suite for PhysicianAssistant"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.assistant = PhysicianAssistant()
    
    def test_basic_assessment(self):
        """Test basic patient assessment"""
        patient = PatientInput(
            age=30,
            sex="M",
            chief_complaint="Cough",
            symptoms=[
                Symptom(name="Cough", duration="2 days", severity=Severity.MILD)
            ]
        )
        
        assessment = self.assistant.assess_patient(patient)
        
        assert assessment is not None
        assert assessment.patient_id is None
        assert len(assessment.differential_diagnoses) > 0
        assert assessment.overall_urgency is not None
        assert assessment.clinician_verification_required is not None
        assert "CLINICIAN VERIFICATION REQUIRED" in assessment.clinician_verification_required
    
    def test_emergency_detection(self):
        """Test emergency symptom detection"""
        patient = PatientInput(
            age=55,
            sex="M",
            chief_complaint="Chest pain",
            symptoms=[
                Symptom(
                    name="Crushing chest pain",
                    duration="30 minutes",
                    severity=Severity.SEVERE
                )
            ]
        )
        
        assessment = self.assistant.assess_patient(patient)
        
        # Should detect red flags
        assert len(assessment.red_flags) > 0
        
        # Should be life-threatening urgency
        assert assessment.overall_urgency == UrgencyLevel.LIFE_THREATENING
        
        # Should require escalation
        assert assessment.escalation_required is True
    
    def test_pediatric_fever_detection(self):
        """Test pediatric fever red flag"""
        patient = PatientInput(
            age=1,
            sex="F",
            chief_complaint="Fever",
            symptoms=[
                Symptom(name="Fever", duration="6 hours", severity=Severity.MODERATE)
            ]
        )
        
        assessment = self.assistant.assess_patient(patient)
        
        # Should detect fever in infant as red flag
        red_flag_descriptions = [rf.flag for rf in assessment.red_flags]
        assert any("infant" in desc.lower() or "fever" in desc.lower() for desc in red_flag_descriptions)
    
    def test_medication_safety(self):
        """Test medication safety checking"""
        patient = PatientInput(
            age=65,
            sex="F",
            chief_complaint="Pain",
            symptoms=[
                Symptom(name="Back pain", duration="1 week", severity=Severity.MODERATE)
            ],
            medical_history=MedicalHistory(
                current_medications=["Warfarin 5mg daily"],
                allergies=["Penicillin"]
            )
        )
        
        assessment = self.assistant.assess_patient(patient)
        
        # Should detect warfarin as high-risk medication
        red_flag_descriptions = [rf.flag for rf in assessment.red_flags]
        assert any("warfarin" in desc.lower() for desc in red_flag_descriptions)
    
    def test_vital_signs_monitoring(self):
        """Test vital signs red flag detection"""
        patient = PatientInput(
            age=40,
            sex="M",
            chief_complaint="Feeling unwell",
            symptoms=[
                Symptom(name="Fatigue", duration="1 day", severity=Severity.MODERATE)
            ],
            vital_signs={
                "systolic_bp": 190,
                "temperature": 104,
                "oxygen_saturation": 88
            }
        )
        
        assessment = self.assistant.assess_patient(patient)
        
        # Should detect abnormal vital signs
        assert len(assessment.red_flags) > 0
    
    def test_json_output(self):
        """Test JSON serialization"""
        patient = PatientInput(
            age=30,
            sex="M",
            chief_complaint="Test",
            symptoms=[
                Symptom(name="Cough", duration="1 day", severity=Severity.MILD)
            ]
        )
        
        assessment = self.assistant.assess_patient(patient)
        json_output = self.assistant.to_json(assessment)
        
        assert json_output is not None
        assert isinstance(json_output, str)
        assert "differential_diagnoses" in json_output
        assert "clinician_verification_required" in json_output
    
    def test_dict_output(self):
        """Test dictionary conversion"""
        patient = PatientInput(
            age=30,
            sex="M",
            chief_complaint="Test",
            symptoms=[
                Symptom(name="Cough", duration="1 day", severity=Severity.MILD)
            ]
        )
        
        assessment = self.assistant.assess_patient(patient)
        dict_output = self.assistant.to_dict(assessment)
        
        assert dict_output is not None
        assert isinstance(dict_output, dict)
        assert "differential_diagnoses" in dict_output
        assert "clinician_verification_required" in dict_output


class TestPatientInput:
    """Test suite for PatientInput model"""
    
    def test_valid_patient_input(self):
        """Test valid patient input creation"""
        patient = PatientInput(
            age=30,
            sex="M",
            chief_complaint="Cough",
            symptoms=[
                Symptom(name="Cough", duration="2 days", severity=Severity.MILD)
            ]
        )
        
        assert patient.age == 30
        assert patient.sex == "M"
        assert len(patient.symptoms) == 1
    
    def test_invalid_age(self):
        """Test age validation"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            PatientInput(
                age=-1,
                sex="M",
                chief_complaint="Test",
                symptoms=[]
            )
    
    def test_invalid_sex(self):
        """Test sex validation"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            PatientInput(
                age=30,
                sex="Invalid",
                chief_complaint="Test",
                symptoms=[]
            )


class TestSafetyChecker:
    """Test suite for SafetyChecker"""
    
    def test_emergency_keyword_detection(self):
        """Test emergency keyword detection"""
        from ai_doctor.safety_checker import SafetyChecker
        
        checker = SafetyChecker()
        patient = PatientInput(
            age=50,
            sex="M",
            chief_complaint="Severe chest pain",
            symptoms=[
                Symptom(name="Chest pain", duration="1 hour", severity=Severity.SEVERE)
            ]
        )
        
        red_flags = checker.check_patient_safety(patient)
        assert len(red_flags) > 0
        assert any("chest pain" in rf.flag.lower() for rf in red_flags)
    
    def test_medication_safety_check(self):
        """Test medication safety checking"""
        from ai_doctor.safety_checker import SafetyChecker
        
        checker = SafetyChecker()
        patient = PatientInput(
            age=65,
            sex="F",
            chief_complaint="Test",
            symptoms=[],
            medical_history=MedicalHistory(
                current_medications=["Warfarin"],
                allergies=["Aspirin"]
            )
        )
        
        safety_check = checker.check_medication_safety("Aspirin", patient)
        assert safety_check["is_safe"] is False
        assert len(safety_check["contraindications"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
