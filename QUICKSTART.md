# Quick Start Guide

This guide will help you get started with AI Doctor quickly.

## Installation

```bash
# Clone the repository
git clone https://github.com/niksbanna/ai-doctor.git
cd ai-doctor

# Install dependencies
pip install -r requirements.txt
```

## Your First Assessment

Create a file `my_assessment.py`:

```python
from ai_doctor import PhysicianAssistant, PatientInput
from ai_doctor.models import Symptom, Severity

# Create a patient
patient = PatientInput(
    age=30,
    sex="M",
    chief_complaint="Fever and cough",
    symptoms=[
        Symptom(name="Fever", duration="2 days", severity=Severity.MODERATE),
        Symptom(name="Cough", duration="3 days", severity=Severity.MILD)
    ]
)

# Initialize the assistant
assistant = PhysicianAssistant()

# Get assessment
assessment = assistant.assess_patient(patient)

# View summary
print(assessment.summary)

# Get JSON output
print("\nStructured JSON:")
print(assistant.to_json(assessment))
```

Run it:
```bash
python my_assessment.py
```

## Run Examples

See comprehensive examples:
```bash
python examples.py
```

## Understanding the Output

### Key Components

1. **Red Flags**: Safety warnings requiring attention
2. **Differential Diagnoses**: Possible conditions with confidence scores
3. **Investigations**: Recommended tests
4. **Management**: Treatment recommendations
5. **Urgency Level**: How quickly patient needs care
6. **Clinician Verification**: Always present - professional review required

### Urgency Levels

- `routine`: Standard follow-up
- `urgent`: Seek care today
- `emergency`: Go to ER now
- `life_threatening`: Call 911 immediately

## Using OpenAI for Enhanced Reasoning (Optional)

1. Get an OpenAI API key from https://platform.openai.com/

2. Create `.env` file:
```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
```

3. The assistant will automatically use AI-enhanced reasoning

**Note**: The system works without OpenAI - it falls back to rule-based assessment.

## Safety Features

The system includes built-in safety checks:
- Emergency symptom detection
- Vital signs monitoring
- Medication interaction checking
- Age-specific considerations
- All assessments include verification requirement

## Common Use Cases

### 1. Primary Care Triage
```python
# Assess urgency and route to appropriate care level
assessment = assistant.assess_patient(patient)
if assessment.overall_urgency == UrgencyLevel.LIFE_THREATENING:
    print("Call 911!")
```

### 2. Medication Safety Check
```python
from ai_doctor.models import MedicalHistory

patient = PatientInput(
    age=65,
    sex="F",
    chief_complaint="Pain",
    symptoms=[...],
    medical_history=MedicalHistory(
        current_medications=["Warfarin"],
        allergies=["Penicillin"]
    )
)

assessment = assistant.assess_patient(patient)
# Check medication_safety_checks in output
```

### 3. Pediatric Assessment
```python
# System automatically applies pediatric-specific rules
patient = PatientInput(
    age=2,  # Pediatric patient
    sex="F",
    chief_complaint="Fever",
    symptoms=[...]
)
```

## Integration with Healthcare Systems

### JSON API
```python
# Convert to JSON for API responses
json_output = assistant.to_json(assessment)

# Or to dictionary
dict_output = assistant.to_dict(assessment)
```

### FHIR Compatibility
The data models use FHIR-compatible structures. Patient data includes:
- SNOMED CT codes for symptoms
- ICD-10 codes for diagnoses
- LOINC codes for investigations

## Best Practices

1. **Always Include Medical History**: More data = better assessment
2. **Record Vital Signs**: Critical for safety checks
3. **Be Specific**: Detailed symptom descriptions help
4. **Review Red Flags First**: Check for emergency conditions
5. **Professional Verification**: Never skip the verification step

## Testing

Run tests to verify installation:
```bash
pytest tests/
```

## Next Steps

1. Read the full README.md for detailed documentation
2. Explore examples.py for comprehensive use cases
3. Review the API reference in README
4. Check CONTRIBUTING.md if you want to contribute

## Getting Help

- Open an issue on GitHub
- Review the examples
- Check the test cases for usage patterns

## Important Reminders

⚠️ **ALWAYS**: This system requires clinician verification
⚠️ **NEVER**: Use for actual medical decisions without professional review
⚠️ **IN EMERGENCIES**: Call 911 immediately - don't use this system

---

Happy coding! Remember: this is a tool to ASSIST healthcare professionals, not replace them.
