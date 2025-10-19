# AI Doctor - Architecture Documentation

## System Overview

AI Doctor is a comprehensive medical assessment system that combines rule-based safety checks with optional AI-enhanced reasoning to provide structured medical assessments for healthcare professionals.

## Design Principles

1. **Safety First**: Rule-based safety checks are independent of AI and always executed
2. **Standards Compliance**: Uses FHIR, SNOMED CT, ICD-10, and LOINC standards
3. **Professional Verification**: All outputs require clinician verification
4. **Privacy by Design**: No persistent storage, anonymization support
5. **Graceful Degradation**: Works without AI in pure rule-based mode

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│              (examples.py, API endpoints)               │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│              PhysicianAssistant (Core Logic)            │
│  - Orchestrates assessment workflow                     │
│  - Combines rule-based and AI reasoning                 │
│  - Generates structured outputs                         │
└─────────────────────────────────────────────────────────┘
                    │               │
        ┌───────────┴────┐    ┌────┴──────────┐
        │                │    │               │
┌───────▼─────┐  ┌──────▼────────┐  ┌────────▼─────────┐
│ SafetyChecker│  │ LLM Reasoning │  │ Output Formatter │
│              │  │  (Optional)   │  │                  │
│ Rule-based   │  │               │  │ JSON + Summary   │
│ Red flags    │  │ OpenAI GPT-4  │  │                  │
│ Vital signs  │  │               │  │ FHIR compatible  │
│ Medications  │  │               │  │                  │
└──────────────┘  └───────────────┘  └──────────────────┘
        │
┌───────▼─────────────────────────────────────────────────┐
│                   Data Models                            │
│  - PatientInput (Pydantic)                              │
│  - MedicalAssessment (Pydantic)                         │
│  - Medical standards codes                              │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Data Models (`models.py`)

**Purpose**: Define structured data types with validation

**Key Models**:
- `PatientInput`: Patient demographics, symptoms, history
- `Symptom`: Individual symptom with severity and duration
- `MedicalHistory`: Chronic conditions, medications, allergies
- `MedicalAssessment`: Complete assessment output
- `Diagnosis`: Differential diagnosis with confidence
- `RedFlag`: Safety warning
- `Investigation`: Recommended test
- `Management`: Treatment recommendation
- `MedicationSafety`: Drug safety check result

**Standards Integration**:
- SNOMED CT codes for symptoms
- ICD-10 codes for diagnoses
- LOINC codes for lab tests
- FHIR-compatible structure

### 2. Safety Checker (`safety_checker.py`)

**Purpose**: Rule-based safety checks independent of AI

**Key Features**:
- Emergency keyword detection
- Vital signs monitoring
- High-risk patient identification
- Medication interaction checking
- Age-specific risk assessment

**Safety Checks**:

1. **Emergency Symptoms**
   - Chest pain, stroke symptoms
   - Severe bleeding, anaphylaxis
   - Loss of consciousness
   - Suicidal ideation

2. **Vital Signs**
   - Temperature >103°F or <95°F
   - BP: Systolic >180 or <90
   - Heart rate >120 or <50
   - O2 saturation <90%

3. **High-Risk Conditions**
   - Immunocompromised states
   - Active cancer
   - Organ transplant

4. **Medication Risks**
   - Anticoagulants
   - Insulin
   - Chemotherapy
   - Immunosuppressants

5. **Age-Specific**
   - Fever in infants <2 years
   - Falls in elderly >65 years

### 3. Physician Assistant (`physician_assistant.py`)

**Purpose**: Main orchestration and assessment logic

**Workflow**:

```
1. Receive PatientInput
   ↓
2. Run SafetyChecker (always)
   ↓
3. Determine urgency level
   ↓
4. If LLM available → AI-enhanced assessment
   Else → Rule-based assessment
   ↓
5. Generate differential diagnoses
   ↓
6. Recommend investigations
   ↓
7. Create management plan
   ↓
8. Check medication safety
   ↓
9. Generate structured output
   ↓
10. Format human-readable summary
   ↓
11. Return MedicalAssessment
```

**Assessment Modes**:

1. **AI-Enhanced Mode** (with OpenAI API)
   - Rule-based safety checks
   - LLM reasoning for diagnoses
   - Evidence-based recommendations
   - Natural language explanations

2. **Rule-Based Mode** (fallback)
   - Pattern matching on symptoms
   - Deterministic diagnoses
   - Conservative recommendations
   - Always functional

### 4. Output Formats

**JSON Structure**:
```json
{
  "timestamp": "ISO 8601",
  "patient_id": "anonymized",
  "red_flags": [...],
  "differential_diagnoses": [...],
  "recommended_investigations": [...],
  "preliminary_management": [...],
  "medication_safety_checks": [...],
  "clinical_reasoning": "text",
  "evidence_citations": [...],
  "overall_urgency": "enum",
  "escalation_required": bool,
  "clinician_verification_required": "mandatory text",
  "privacy_notice": "text",
  "summary": "human readable"
}
```

**Human-Readable Summary**:
- Patient demographics
- Urgency level (highlighted)
- Red flags (if present)
- Top diagnoses with codes
- Recommended actions
- Mandatory disclaimers

## Data Flow

### Input Processing

```
User Input
    ↓
PatientInput model validation
    ↓
Pydantic validation (age, sex, etc.)
    ↓
Safety checks triggered
```

### Safety Assessment

```
PatientInput
    ↓
SafetyChecker.check_patient_safety()
    ├─→ Check emergency keywords
    ├─→ Check vital signs
    ├─→ Check high-risk factors
    ├─→ Check medication risks
    └─→ Check age-specific risks
    ↓
List[RedFlag]
```

### Diagnosis Generation

**Rule-Based**:
```
Symptom patterns
    ↓
Pattern matching
    ├─→ URI pattern
    ├─→ Flu pattern
    ├─→ GI pattern
    └─→ Other patterns
    ↓
List[Diagnosis] with confidence
```

**AI-Enhanced**:
```
PatientInput + RedFlags
    ↓
Structured prompt
    ↓
OpenAI API
    ↓
Parse response
    ↓
Enhanced List[Diagnosis]
```

### Output Generation

```
Assessment components
    ↓
MedicalAssessment model
    ├─→ JSON serialization
    └─→ Summary generation
    ↓
Return to user
```

## Security & Privacy

### Data Protection
- No persistent storage
- Anonymized patient IDs supported
- Environment-based API key management
- No logging of PHI

### Compliance Features
- HIPAA-compliant design
- GDPR-compatible
- Audit trail capable
- Mandatory disclaimers

### Safety Mechanisms
- Dual-layer safety (rule-based + AI)
- Explicit escalation protocols
- Conservative recommendations
- Professional verification required

## Extensibility Points

### Adding New Safety Rules
```python
# In safety_checker.py
def _check_new_condition(self, patient_input):
    # Add custom safety logic
    if condition_met:
        self.red_flags.append(RedFlag(...))
```

### Adding Diagnosis Patterns
```python
# In physician_assistant.py
def _generate_rule_based_diagnoses(self, patient_input):
    # Add new symptom patterns
    if pattern_matches:
        diagnoses.append(Diagnosis(...))
```

### Custom Output Formats
```python
# Create custom formatter
def custom_format(assessment: MedicalAssessment) -> CustomFormat:
    # Transform to your format
    return custom_output
```

### Integration Points
```python
# API endpoint example
@app.post("/assess")
def assess_patient(patient: PatientInput):
    assistant = PhysicianAssistant()
    assessment = assistant.assess_patient(patient)
    return assessment.model_dump()
```

## Performance Considerations

### Scalability
- Stateless design enables horizontal scaling
- No database dependencies
- Can cache common patterns
- LLM calls are optional

### Response Time
- Rule-based mode: <100ms
- AI-enhanced mode: 2-5 seconds (OpenAI latency)
- Parallel processing possible for batch assessments

### Resource Usage
- Memory: ~50MB base
- CPU: Minimal (no heavy computation)
- Network: Only for OpenAI API calls

## Testing Strategy

### Unit Tests
- Model validation
- Safety checker rules
- Pattern matching logic
- Output formatting

### Integration Tests
- End-to-end assessment flow
- API integration
- Error handling

### Safety Tests
- Emergency detection
- Vital signs thresholds
- Medication interactions
- Age-specific rules

## Deployment Options

### Standalone Application
```bash
python examples.py
```

### Python Package
```bash
pip install .
```

### REST API
```python
from fastapi import FastAPI
from ai_doctor import PhysicianAssistant

app = FastAPI()
assistant = PhysicianAssistant()

@app.post("/assess")
def assess(patient: PatientInput):
    return assistant.assess_patient(patient)
```

### Microservice
- Docker container
- Kubernetes deployment
- Load-balanced instances

## Future Enhancements

### Potential Additions
1. **Enhanced AI Features**
   - Multi-model ensemble
   - Specialized medical LLMs
   - Fine-tuning on medical data

2. **Extended Standards**
   - HL7 FHIR resources
   - DICOM integration
   - Lab result parsing

3. **Clinical Decision Support**
   - Evidence-based guidelines
   - Drug interaction databases
   - Clinical calculators

4. **Integration Features**
   - EHR connectors
   - Lab system interfaces
   - Imaging system integration

5. **Analytics**
   - Outcome tracking
   - Pattern analysis
   - Quality metrics

## Limitations

### Technical
- Requires Python 3.8+
- OpenAI API optional but enhances results
- Rule-based diagnoses are conservative
- Limited to general medical assessment

### Medical
- Not a replacement for clinical judgment
- Requires professional verification
- Limited specialized knowledge
- No longitudinal patient tracking

### Legal
- Not FDA approved
- Research/educational use
- Liability with healthcare provider
- Requires validation for clinical use

## Maintenance

### Code Updates
- Test all safety checks
- Validate medical logic
- Update medical codes
- Review evidence sources

### Dependency Management
- Pin critical versions
- Regular security updates
- OpenAI API compatibility
- Python version support

### Documentation
- Keep examples current
- Update medical references
- Maintain API docs
- Version changelog

## Support

For architecture questions or contributions, see CONTRIBUTING.md or open an issue on GitHub.
