"""
Rule-based safety checker for medical red flags and emergency conditions.
This provides a safety layer independent of LLM reasoning.
"""

from typing import List, Dict, Set
from .models import PatientInput, RedFlag, Severity, UrgencyLevel


class SafetyChecker:
    """
    Rule-based safety checker for identifying red flags and emergency conditions.
    This provides deterministic safety checks independent of AI reasoning.
    """
    
    # Emergency red flag keywords for immediate attention
    EMERGENCY_KEYWORDS = {
        'chest pain', 'crushing chest pain', 'chest pressure',
        'difficulty breathing', 'shortness of breath', 'can\'t breathe',
        'severe headache', 'worst headache', 'thunderclap headache',
        'stroke', 'facial drooping', 'slurred speech', 'arm weakness',
        'seizure', 'convulsion',
        'severe bleeding', 'hemorrhage', 'massive bleeding',
        'unconscious', 'unresponsive', 'loss of consciousness',
        'suicide', 'suicidal thoughts', 'want to die',
        'severe abdominal pain',
        'anaphylaxis', 'severe allergic reaction',
        'severe trauma', 'major injury',
        'overdose', 'poisoning'
    }
    
    # Urgent warning signs requiring prompt attention
    URGENT_KEYWORDS = {
        'fever', 'high fever',
        'persistent vomiting', 'can\'t keep fluids down',
        'severe pain',
        'dehydration',
        'confusion', 'disoriented',
        'rapid heartbeat', 'palpitations',
        'blood in stool', 'blood in urine', 'coughing blood',
        'sudden vision loss', 'vision changes',
        'pregnancy complications', 'pregnant and bleeding'
    }
    
    # Medication interaction warning keywords
    MEDICATION_WARNING_KEYWORDS = {
        'warfarin', 'coumadin',
        'insulin',
        'chemotherapy',
        'immunosuppressant',
        'steroid', 'prednisone'
    }
    
    def __init__(self):
        """Initialize the safety checker with rule-based knowledge"""
        self.red_flags: List[RedFlag] = []
        
    def check_patient_safety(self, patient_input: PatientInput) -> List[RedFlag]:
        """
        Perform comprehensive safety checks on patient input.
        
        Args:
            patient_input: Patient data to check
            
        Returns:
            List of identified red flags
        """
        self.red_flags = []
        
        # Check chief complaint and symptoms for emergency keywords
        self._check_emergency_symptoms(patient_input)
        
        # Check vital signs if available
        if patient_input.vital_signs:
            self._check_vital_signs(patient_input.vital_signs)
        
        # Check for high-risk patient factors
        self._check_high_risk_factors(patient_input)
        
        # Check medication safety
        self._check_medication_risks(patient_input)
        
        # Age-specific checks
        self._check_age_specific_risks(patient_input)
        
        return self.red_flags
    
    def _check_emergency_symptoms(self, patient_input: PatientInput):
        """Check for emergency symptoms in chief complaint and symptom descriptions"""
        text_to_check = [
            patient_input.chief_complaint.lower(),
            *[s.name.lower() for s in patient_input.symptoms],
            *[s.additional_details.lower() if s.additional_details else "" for s in patient_input.symptoms]
        ]
        
        full_text = " ".join(text_to_check)
        
        # Check for emergency keywords
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in full_text:
                self.red_flags.append(RedFlag(
                    flag=f"Emergency symptom detected: {keyword}",
                    severity=Severity.CRITICAL,
                    urgency=UrgencyLevel.LIFE_THREATENING,
                    reasoning=f"Presence of '{keyword}' indicates potential life-threatening condition requiring immediate emergency care"
                ))
                
        # Check for urgent keywords
        for keyword in self.URGENT_KEYWORDS:
            if keyword in full_text:
                self.red_flags.append(RedFlag(
                    flag=f"Urgent symptom detected: {keyword}",
                    severity=Severity.SEVERE,
                    urgency=UrgencyLevel.URGENT,
                    reasoning=f"Presence of '{keyword}' requires prompt medical evaluation"
                ))
    
    def _check_vital_signs(self, vital_signs: Dict):
        """Check vital signs for abnormal values"""
        # Temperature check
        if 'temperature' in vital_signs:
            temp = vital_signs['temperature']
            if isinstance(temp, (int, float)):
                if temp >= 103:  # Fahrenheit
                    self.red_flags.append(RedFlag(
                        flag=f"High fever: {temp}°F",
                        severity=Severity.SEVERE,
                        urgency=UrgencyLevel.URGENT,
                        reasoning="Temperature ≥103°F requires urgent evaluation"
                    ))
                elif temp >= 39.4 and temp <= 45:  # Celsius
                    self.red_flags.append(RedFlag(
                        flag=f"High fever: {temp}°C",
                        severity=Severity.SEVERE,
                        urgency=UrgencyLevel.URGENT,
                        reasoning="Temperature ≥39.4°C requires urgent evaluation"
                    ))
        
        # Blood pressure check
        if 'systolic_bp' in vital_signs:
            systolic = vital_signs['systolic_bp']
            if isinstance(systolic, (int, float)):
                if systolic >= 180:
                    self.red_flags.append(RedFlag(
                        flag=f"Hypertensive crisis: Systolic BP {systolic}",
                        severity=Severity.CRITICAL,
                        urgency=UrgencyLevel.EMERGENCY,
                        reasoning="Systolic BP ≥180 mmHg indicates hypertensive crisis"
                    ))
                elif systolic < 90:
                    self.red_flags.append(RedFlag(
                        flag=f"Hypotension: Systolic BP {systolic}",
                        severity=Severity.SEVERE,
                        urgency=UrgencyLevel.URGENT,
                        reasoning="Systolic BP <90 mmHg may indicate shock or severe hypotension"
                    ))
        
        # Heart rate check
        if 'heart_rate' in vital_signs:
            hr = vital_signs['heart_rate']
            if isinstance(hr, (int, float)):
                if hr > 120:
                    self.red_flags.append(RedFlag(
                        flag=f"Tachycardia: Heart rate {hr}",
                        severity=Severity.MODERATE,
                        urgency=UrgencyLevel.URGENT,
                        reasoning="Heart rate >120 bpm requires evaluation"
                    ))
                elif hr < 50:
                    self.red_flags.append(RedFlag(
                        flag=f"Bradycardia: Heart rate {hr}",
                        severity=Severity.MODERATE,
                        urgency=UrgencyLevel.URGENT,
                        reasoning="Heart rate <50 bpm requires evaluation"
                    ))
        
        # Oxygen saturation check
        if 'oxygen_saturation' in vital_signs:
            o2_sat = vital_signs['oxygen_saturation']
            if isinstance(o2_sat, (int, float)):
                if o2_sat < 90:
                    self.red_flags.append(RedFlag(
                        flag=f"Low oxygen saturation: {o2_sat}%",
                        severity=Severity.CRITICAL,
                        urgency=UrgencyLevel.EMERGENCY,
                        reasoning="Oxygen saturation <90% indicates severe hypoxemia"
                    ))
    
    def _check_high_risk_factors(self, patient_input: PatientInput):
        """Check for high-risk patient factors"""
        # Check for immunocompromised conditions
        high_risk_conditions = {
            'hiv', 'aids', 'cancer', 'chemotherapy', 
            'transplant', 'immunosuppressed', 'diabetes'
        }
        
        conditions_text = " ".join([c.lower() for c in patient_input.medical_history.chronic_conditions])
        
        for condition in high_risk_conditions:
            if condition in conditions_text:
                self.red_flags.append(RedFlag(
                    flag=f"High-risk patient: {condition}",
                    severity=Severity.MODERATE,
                    urgency=UrgencyLevel.URGENT,
                    reasoning=f"Patient with {condition} requires careful evaluation due to increased risk"
                ))
    
    def _check_medication_risks(self, patient_input: PatientInput):
        """Check for high-risk medications"""
        meds_text = " ".join([m.lower() for m in patient_input.medical_history.current_medications])
        
        for med in self.MEDICATION_WARNING_KEYWORDS:
            if med in meds_text:
                self.red_flags.append(RedFlag(
                    flag=f"High-risk medication: {med}",
                    severity=Severity.MODERATE,
                    urgency=UrgencyLevel.URGENT,
                    reasoning=f"Patient on {med} requires careful medication interaction screening"
                ))
    
    def _check_age_specific_risks(self, patient_input: PatientInput):
        """Check for age-specific risk factors"""
        # Very young patients
        if patient_input.age < 2:
            # Any fever in infants under 3 months is urgent
            symptoms_text = " ".join([s.name.lower() for s in patient_input.symptoms])
            if 'fever' in symptoms_text or 'temperature' in symptoms_text:
                self.red_flags.append(RedFlag(
                    flag="Fever in infant under 2 years",
                    severity=Severity.SEVERE,
                    urgency=UrgencyLevel.URGENT,
                    reasoning="Fever in young infants requires urgent evaluation to rule out serious bacterial infection"
                ))
        
        # Elderly patients (>65) with certain symptoms
        if patient_input.age > 65:
            symptoms_text = " ".join([s.name.lower() for s in patient_input.symptoms])
            if 'fall' in symptoms_text or 'fell' in symptoms_text:
                self.red_flags.append(RedFlag(
                    flag="Fall in elderly patient",
                    severity=Severity.MODERATE,
                    urgency=UrgencyLevel.URGENT,
                    reasoning="Falls in elderly patients require evaluation for fractures and underlying causes"
                ))
    
    def check_medication_safety(self, medication: str, patient_input: PatientInput) -> Dict[str, any]:
        """
        Check if a medication is safe for the patient.
        
        Args:
            medication: Medication name to check
            patient_input: Patient data
            
        Returns:
            Dictionary with safety information
        """
        interactions = []
        contraindications = []
        warnings = []
        
        med_lower = medication.lower()
        
        # Check for allergies
        for allergy in patient_input.medical_history.allergies:
            if allergy.lower() in med_lower or med_lower in allergy.lower():
                contraindications.append(f"Patient is allergic to {allergy}")
        
        # Check for drug-drug interactions with current medications
        current_meds = [m.lower() for m in patient_input.medical_history.current_medications]
        
        # Common interaction patterns
        if 'warfarin' in current_meds or 'coumadin' in current_meds:
            if any(drug in med_lower for drug in ['aspirin', 'nsaid', 'ibuprofen', 'naproxen']):
                interactions.append("Increased bleeding risk with warfarin")
        
        if 'aspirin' in current_meds:
            if any(drug in med_lower for drug in ['ibuprofen', 'naproxen']):
                interactions.append("May reduce cardioprotective effect of aspirin")
        
        # Age-based warnings
        if patient_input.age > 65:
            if any(drug in med_lower for drug in ['benzodiazepine', 'diphenhydramine', 'opioid']):
                warnings.append("Use caution in elderly patients - increased risk of falls and confusion")
        
        # Pregnancy warnings (if applicable)
        # Condition-specific contraindications
        conditions = [c.lower() for c in patient_input.medical_history.chronic_conditions]
        
        if 'kidney disease' in " ".join(conditions) or 'renal' in " ".join(conditions):
            if any(drug in med_lower for drug in ['nsaid', 'ibuprofen', 'naproxen']):
                warnings.append("NSAIDs may worsen kidney function")
        
        is_safe = len(contraindications) == 0
        
        return {
            'medication': medication,
            'is_safe': is_safe,
            'interactions': interactions,
            'contraindications': contraindications,
            'warnings': warnings
        }
