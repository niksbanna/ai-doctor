"""
Main Physician Assistant that combines LLM reasoning with rule-based safety checks.
Provides comprehensive medical assessment with structured output.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

from .models import (
    PatientInput, MedicalAssessment, RedFlag, Diagnosis, Investigation,
    Management, MedicationSafety, ClinicalEvidence, UrgencyLevel, Severity
)
from .safety_checker import SafetyChecker

# Load environment variables
load_dotenv()


class PhysicianAssistant:
    """
    AI-powered physician assistant that provides comprehensive medical assessments.
    Combines LLM reasoning with rule-based safety checks.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the Physician Assistant.
        
        Args:
            api_key: OpenAI API key (if not provided, loads from environment)
            model: Model to use for LLM reasoning
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.safety_checker = SafetyChecker()
        
        # Initialize OpenAI client if API key is available
        self.use_llm = bool(self.api_key)
        if self.use_llm:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("Warning: OpenAI package not installed. Running in rule-based mode only.")
                self.use_llm = False
        else:
            print("Warning: No OpenAI API key provided. Running in rule-based mode only.")
            self.use_llm = False
    
    def assess_patient(self, patient_input: PatientInput) -> MedicalAssessment:
        """
        Perform comprehensive patient assessment.
        
        Args:
            patient_input: Patient data including symptoms and history
            
        Returns:
            Complete medical assessment with structured output
        """
        # Step 1: Rule-based safety checks (always performed)
        red_flags = self.safety_checker.check_patient_safety(patient_input)
        
        # Step 2: Determine if emergency escalation is needed
        escalation_required = any(
            flag.urgency == UrgencyLevel.LIFE_THREATENING 
            for flag in red_flags
        )
        
        # Determine overall urgency
        if escalation_required:
            overall_urgency = UrgencyLevel.LIFE_THREATENING
        elif any(flag.urgency == UrgencyLevel.EMERGENCY for flag in red_flags):
            overall_urgency = UrgencyLevel.EMERGENCY
        elif any(flag.urgency == UrgencyLevel.URGENT for flag in red_flags):
            overall_urgency = UrgencyLevel.URGENT
        else:
            overall_urgency = UrgencyLevel.ROUTINE
        
        # Step 3: If LLM is available, enhance assessment with AI reasoning
        if self.use_llm and not escalation_required:
            assessment = self._llm_enhanced_assessment(patient_input, red_flags, overall_urgency)
        else:
            # Fallback to rule-based only assessment
            assessment = self._rule_based_assessment(patient_input, red_flags, overall_urgency)
        
        # Step 4: Check medication safety for any recommended medications
        medication_safety_checks = []
        for management in assessment.preliminary_management:
            if management.category == "medication":
                med_name = management.intervention.split()[0]  # Extract medication name
                safety_check = self.safety_checker.check_medication_safety(med_name, patient_input)
                medication_safety_checks.append(MedicationSafety(**safety_check))
        
        assessment.medication_safety_checks = medication_safety_checks
        
        # Step 5: Add emergency indicators if present
        if escalation_required:
            assessment.emergency_indicators = [flag.flag for flag in red_flags if flag.urgency == UrgencyLevel.LIFE_THREATENING]
        
        return assessment
    
    def _llm_enhanced_assessment(
        self, 
        patient_input: PatientInput, 
        red_flags: List[RedFlag],
        overall_urgency: UrgencyLevel
    ) -> MedicalAssessment:
        """Generate assessment enhanced by LLM reasoning"""
        
        # Prepare prompt for LLM
        prompt = self._create_medical_prompt(patient_input, red_flags)
        
        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent medical reasoning
                max_tokens=2000
            )
            
            llm_output = response.choices[0].message.content
            
            # Parse LLM output and structure it
            assessment = self._parse_llm_output(
                llm_output, 
                patient_input, 
                red_flags, 
                overall_urgency
            )
            
        except Exception as e:
            print(f"Error calling LLM: {e}. Falling back to rule-based assessment.")
            assessment = self._rule_based_assessment(patient_input, red_flags, overall_urgency)
        
        return assessment
    
    def _rule_based_assessment(
        self,
        patient_input: PatientInput,
        red_flags: List[RedFlag],
        overall_urgency: UrgencyLevel
    ) -> MedicalAssessment:
        """Generate assessment using rule-based logic only"""
        
        # Generate basic differential diagnoses based on symptoms
        differential_diagnoses = self._generate_rule_based_diagnoses(patient_input)
        
        # Generate basic investigation recommendations
        investigations = self._generate_rule_based_investigations(patient_input, overall_urgency)
        
        # Generate basic management recommendations
        management = self._generate_rule_based_management(patient_input, overall_urgency)
        
        # Generate clinical reasoning
        reasoning = self._generate_rule_based_reasoning(patient_input, red_flags, differential_diagnoses)
        
        # Generate summary
        summary = self._generate_summary(patient_input, red_flags, differential_diagnoses, overall_urgency)
        
        # Create evidence citations (basic rule-based)
        evidence = [
            ClinicalEvidence(
                statement="Assessment based on clinical presentation and established medical guidelines",
                evidence_level="C",
                source="Clinical Practice Guidelines",
                reference="Standard medical practice"
            )
        ]
        
        return MedicalAssessment(
            timestamp=datetime.now(timezone.utc),
            patient_id=patient_input.patient_id,
            red_flags=red_flags,
            differential_diagnoses=differential_diagnoses,
            recommended_investigations=investigations,
            preliminary_management=management,
            clinical_reasoning=reasoning,
            evidence_citations=evidence,
            overall_urgency=overall_urgency,
            escalation_required=(overall_urgency == UrgencyLevel.LIFE_THREATENING),
            summary=summary
        )
    
    def _generate_rule_based_diagnoses(self, patient_input: PatientInput) -> List[Diagnosis]:
        """Generate differential diagnoses based on symptom patterns"""
        diagnoses = []
        
        symptoms_text = " ".join([s.name.lower() for s in patient_input.symptoms])
        chief_complaint_lower = patient_input.chief_complaint.lower()
        
        # Common cold/URI pattern
        if any(s in symptoms_text for s in ['cough', 'runny nose', 'sore throat', 'congestion']):
            diagnoses.append(Diagnosis(
                condition="Viral Upper Respiratory Infection",
                icd10_code="J06.9",
                snomed_code="82272006",
                confidence=0.70,
                reasoning="Symptoms consistent with viral URI: cough, congestion, and/or sore throat",
                supporting_evidence=["Symptom cluster typical of viral infection", "Usually self-limiting"]
            ))
        
        # Flu pattern
        if any(s in symptoms_text for s in ['fever', 'body ache', 'fatigue', 'cough']):
            diagnoses.append(Diagnosis(
                condition="Influenza",
                icd10_code="J11.1",
                snomed_code="6142004",
                confidence=0.60,
                reasoning="Fever with body aches and respiratory symptoms suggests influenza",
                supporting_evidence=["Systemic symptoms with fever", "Respiratory involvement"]
            ))
        
        # Gastroenteritis pattern
        if any(s in symptoms_text for s in ['nausea', 'vomiting', 'diarrhea', 'abdominal pain']):
            diagnoses.append(Diagnosis(
                condition="Acute Gastroenteritis",
                icd10_code="K52.9",
                snomed_code="25374005",
                confidence=0.65,
                reasoning="GI symptoms suggest acute gastroenteritis",
                supporting_evidence=["Nausea/vomiting/diarrhea pattern", "Common self-limiting condition"]
            ))
        
        # Headache patterns
        if 'headache' in symptoms_text:
            diagnoses.append(Diagnosis(
                condition="Tension Headache",
                icd10_code="G44.209",
                snomed_code="398057008",
                confidence=0.55,
                reasoning="Headache presentation, most commonly tension-type",
                supporting_evidence=["Most common headache type", "Usually bilateral pressure"]
            ))
        
        # If no specific pattern, add a general diagnosis
        if not diagnoses:
            diagnoses.append(Diagnosis(
                condition="Undifferentiated Illness",
                icd10_code="R69",
                confidence=0.40,
                reasoning="Symptom pattern does not match common presentations; requires further evaluation",
                supporting_evidence=["Non-specific symptoms", "Requires clinical correlation"]
            ))
        
        # Sort by confidence
        diagnoses.sort(key=lambda x: x.confidence, reverse=True)
        
        return diagnoses
    
    def _generate_rule_based_investigations(
        self, 
        patient_input: PatientInput, 
        urgency: UrgencyLevel
    ) -> List[Investigation]:
        """Generate investigation recommendations based on symptoms and urgency"""
        investigations = []
        
        symptoms_text = " ".join([s.name.lower() for s in patient_input.symptoms])
        
        # If emergency/urgent, recommend basic workup
        if urgency in [UrgencyLevel.EMERGENCY, UrgencyLevel.LIFE_THREATENING]:
            investigations.extend([
                Investigation(
                    test_name="Complete Blood Count (CBC)",
                    loinc_code="58410-2",
                    urgency=UrgencyLevel.URGENT,
                    reasoning="Basic screening for infection, anemia, or hematologic abnormalities"
                ),
                Investigation(
                    test_name="Basic Metabolic Panel (BMP)",
                    loinc_code="51990-0",
                    urgency=UrgencyLevel.URGENT,
                    reasoning="Assess electrolytes, kidney function, and glucose"
                )
            ])
        
        # Respiratory symptoms
        if any(s in symptoms_text for s in ['cough', 'shortness of breath', 'chest pain']):
            investigations.append(Investigation(
                test_name="Chest X-ray",
                urgency=UrgencyLevel.URGENT if 'shortness of breath' in symptoms_text else UrgencyLevel.ROUTINE,
                reasoning="Evaluate for pneumonia, heart failure, or other pulmonary pathology"
            ))
        
        # Fever
        if 'fever' in symptoms_text:
            investigations.append(Investigation(
                test_name="Blood cultures",
                urgency=UrgencyLevel.URGENT,
                reasoning="Rule out bacteremia if fever is significant"
            ))
        
        # GI symptoms
        if any(s in symptoms_text for s in ['diarrhea', 'vomiting', 'abdominal pain']):
            investigations.append(Investigation(
                test_name="Stool studies",
                urgency=UrgencyLevel.ROUTINE,
                reasoning="Identify infectious etiology if diarrhea persists"
            ))
        
        return investigations
    
    def _generate_rule_based_management(
        self,
        patient_input: PatientInput,
        urgency: UrgencyLevel
    ) -> List[Management]:
        """Generate management recommendations"""
        management_plans = []
        
        # If life-threatening, immediate transfer
        if urgency == UrgencyLevel.LIFE_THREATENING:
            management_plans.append(Management(
                intervention="Immediate transfer to emergency department",
                category="referral",
                safety_considerations=["Call 911 or emergency services", "Do not delay transport"]
            ))
            return management_plans
        
        # If emergency, urgent referral
        if urgency == UrgencyLevel.EMERGENCY:
            management_plans.append(Management(
                intervention="Urgent emergency department evaluation",
                category="referral",
                safety_considerations=["Seek emergency care within hours", "Do not wait"]
            ))
        
        symptoms_text = " ".join([s.name.lower() for s in patient_input.symptoms])
        
        # Supportive care for common symptoms
        if any(s in symptoms_text for s in ['fever', 'pain', 'headache']):
            management_plans.append(Management(
                intervention="Acetaminophen 500-1000mg every 6 hours as needed",
                category="medication",
                safety_considerations=[
                    "Maximum 4000mg per day",
                    "Avoid if liver disease",
                    "Check for contraindications"
                ]
            ))
        
        if any(s in symptoms_text for s in ['cough', 'congestion']):
            management_plans.append(Management(
                intervention="Increase fluid intake, humidified air, rest",
                category="lifestyle",
                safety_considerations=["Supportive care for viral illness"]
            ))
        
        if any(s in symptoms_text for s in ['nausea', 'vomiting']):
            management_plans.append(Management(
                intervention="Clear liquids, advance diet as tolerated, oral rehydration",
                category="lifestyle",
                safety_considerations=["Monitor for dehydration signs"]
            ))
        
        # Always add monitoring
        management_plans.append(Management(
            intervention="Monitor symptoms and return if worsening",
            category="monitoring",
            safety_considerations=[
                "Return if symptoms worsen",
                "Seek immediate care for red flag symptoms",
                "Follow up in 3-5 days if not improving"
            ]
        ))
        
        return management_plans
    
    def _generate_rule_based_reasoning(
        self,
        patient_input: PatientInput,
        red_flags: List[RedFlag],
        diagnoses: List[Diagnosis]
    ) -> str:
        """Generate clinical reasoning text"""
        reasoning_parts = []
        
        # Patient presentation
        reasoning_parts.append(
            f"Patient is a {patient_input.age}-year-old {patient_input.sex} presenting with {patient_input.chief_complaint}."
        )
        
        # Symptoms summary
        if patient_input.symptoms:
            symptom_list = ", ".join([s.name for s in patient_input.symptoms])
            reasoning_parts.append(f"Associated symptoms include: {symptom_list}.")
        
        # Medical history
        if patient_input.medical_history.chronic_conditions:
            conditions = ", ".join(patient_input.medical_history.chronic_conditions)
            reasoning_parts.append(f"Relevant medical history: {conditions}.")
        
        # Red flags
        if red_flags:
            reasoning_parts.append(
                f"IMPORTANT: {len(red_flags)} red flag(s) identified requiring attention."
            )
        
        # Differential diagnosis reasoning
        if diagnoses:
            top_diagnosis = diagnoses[0]
            reasoning_parts.append(
                f"Most likely diagnosis is {top_diagnosis.condition} with {top_diagnosis.confidence*100:.0f}% confidence. "
                f"{top_diagnosis.reasoning}"
            )
        
        return " ".join(reasoning_parts)
    
    def _generate_summary(
        self,
        patient_input: PatientInput,
        red_flags: List[RedFlag],
        diagnoses: List[Diagnosis],
        urgency: UrgencyLevel
    ) -> str:
        """Generate human-readable summary"""
        summary_parts = []
        
        # Header
        summary_parts.append(f"=== MEDICAL ASSESSMENT SUMMARY ===\n")
        summary_parts.append(f"Patient: {patient_input.age}-year-old {patient_input.sex}")
        summary_parts.append(f"Chief Complaint: {patient_input.chief_complaint}\n")
        
        # Urgency level
        summary_parts.append(f"URGENCY LEVEL: {urgency.value.upper()}\n")
        
        # Red flags if present
        if red_flags:
            summary_parts.append("⚠️ RED FLAGS IDENTIFIED:")
            for flag in red_flags[:3]:  # Show top 3
                summary_parts.append(f"  - {flag.flag} (Urgency: {flag.urgency.value})")
            summary_parts.append("")
        
        # Top diagnoses
        if diagnoses:
            summary_parts.append("DIFFERENTIAL DIAGNOSES:")
            for i, dx in enumerate(diagnoses[:3], 1):  # Show top 3
                summary_parts.append(
                    f"  {i}. {dx.condition} ({dx.confidence*100:.0f}% confidence)"
                )
                if dx.icd10_code:
                    summary_parts.append(f"     ICD-10: {dx.icd10_code}")
            summary_parts.append("")
        
        # Action items
        summary_parts.append("RECOMMENDED ACTIONS:")
        if urgency == UrgencyLevel.LIFE_THREATENING:
            summary_parts.append("  🚨 CALL 911 IMMEDIATELY")
        elif urgency == UrgencyLevel.EMERGENCY:
            summary_parts.append("  ⚠️ GO TO EMERGENCY DEPARTMENT NOW")
        elif urgency == UrgencyLevel.URGENT:
            summary_parts.append("  ⚠️ SEEK URGENT MEDICAL ATTENTION TODAY")
        else:
            summary_parts.append("  - Schedule follow-up with healthcare provider")
            summary_parts.append("  - Continue supportive care")
        
        summary_parts.append("\n" + "="*50)
        summary_parts.append("⚠️ CLINICIAN VERIFICATION REQUIRED")
        summary_parts.append("This AI-generated assessment must be verified by a")
        summary_parts.append("qualified healthcare professional before any clinical action.")
        summary_parts.append("="*50)
        
        return "\n".join(summary_parts)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """You are an AI medical assistant helping to assess patient presentations.
Your role is to:
1. Analyze patient symptoms and medical history
2. Generate differential diagnoses with confidence scores
3. Recommend appropriate investigations
4. Suggest safe preliminary management
5. Explain your clinical reasoning
6. Cite evidence where appropriate

You must:
- Use ICD-10, SNOMED CT, and LOINC codes where applicable
- Consider patient safety as top priority
- Explain your reasoning clearly
- Acknowledge uncertainty when appropriate
- Always emphasize that clinician verification is required

Provide structured, evidence-based assessments suitable for review by healthcare professionals."""
    
    def _create_medical_prompt(self, patient_input: PatientInput, red_flags: List[RedFlag]) -> str:
        """Create detailed prompt for LLM assessment"""
        prompt_parts = [
            "Please assess the following patient:\n",
            f"Age: {patient_input.age} years",
            f"Sex: {patient_input.sex}",
            f"Chief Complaint: {patient_input.chief_complaint}\n",
            "Symptoms:"
        ]
        
        for symptom in patient_input.symptoms:
            prompt_parts.append(
                f"  - {symptom.name} (Duration: {symptom.duration}, Severity: {symptom.severity.value})"
            )
            if symptom.additional_details:
                prompt_parts.append(f"    Details: {symptom.additional_details}")
        
        if patient_input.medical_history.chronic_conditions:
            prompt_parts.append(f"\nMedical History: {', '.join(patient_input.medical_history.chronic_conditions)}")
        
        if patient_input.medical_history.current_medications:
            prompt_parts.append(f"Current Medications: {', '.join(patient_input.medical_history.current_medications)}")
        
        if patient_input.medical_history.allergies:
            prompt_parts.append(f"Allergies: {', '.join(patient_input.medical_history.allergies)}")
        
        if red_flags:
            prompt_parts.append(f"\n⚠️ Rule-based safety system identified {len(red_flags)} red flag(s):")
            for flag in red_flags:
                prompt_parts.append(f"  - {flag.flag} ({flag.urgency.value})")
        
        prompt_parts.append("\nProvide:")
        prompt_parts.append("1. Top 3-5 differential diagnoses with confidence scores and ICD-10 codes")
        prompt_parts.append("2. Recommended investigations with LOINC codes where applicable")
        prompt_parts.append("3. Safe preliminary management recommendations")
        prompt_parts.append("4. Clinical reasoning")
        prompt_parts.append("5. Relevant evidence citations")
        
        return "\n".join(prompt_parts)
    
    def _parse_llm_output(
        self,
        llm_output: str,
        patient_input: PatientInput,
        red_flags: List[RedFlag],
        overall_urgency: UrgencyLevel
    ) -> MedicalAssessment:
        """Parse LLM output and create structured assessment"""
        # For now, use rule-based as fallback and enhance with LLM reasoning
        # A full implementation would parse the LLM output more thoroughly
        
        assessment = self._rule_based_assessment(patient_input, red_flags, overall_urgency)
        
        # Enhance reasoning with LLM output
        assessment.clinical_reasoning = (
            assessment.clinical_reasoning + "\n\nAI-Enhanced Analysis:\n" + llm_output[:1000]
        )
        
        return assessment
    
    def to_json(self, assessment: MedicalAssessment) -> str:
        """
        Convert assessment to JSON string.
        
        Args:
            assessment: Medical assessment to convert
            
        Returns:
            JSON string representation
        """
        return assessment.model_dump_json(indent=2)
    
    def to_dict(self, assessment: MedicalAssessment) -> Dict:
        """
        Convert assessment to dictionary.
        
        Args:
            assessment: Medical assessment to convert
            
        Returns:
            Dictionary representation
        """
        return assessment.model_dump()
