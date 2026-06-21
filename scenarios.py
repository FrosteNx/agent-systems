SCENARIOS = [
    {
        "name": "Baseline seasonal flu",
        "description": "Reference baseline scenario with default interventions.",
        "overrides": {
            "SCENARIO_NAME": "Baseline seasonal flu",
        },
    },

    {
        "name": "No interventions",
        "description": "No masks, no quarantine, no testing, and no adaptive restrictions.",
        "overrides": {
            "SCENARIO_NAME": "No interventions",

            "MASKS_ENABLED": False,
            "QUARANTINE_ENABLED": False,

            "TESTING_RATE": 0.0,
            "ISOLATION_RATE": 0.0,

            "AUTO_SCHOOL_CLOSURE": False,
            "AUTO_SCHOOL_REOPEN": False,

            "AUTO_MASK_COMPLIANCE": False,
            "AUTO_MASK_RELAXATION": False,

            "AUTO_TESTING_RATE": False,
            "AUTO_TESTING_RELAXATION": False,

            "AUTO_QUARANTINE_COMPLIANCE": False,
            "AUTO_QUARANTINE_RELAXATION": False,

            "AUTO_SENIOR_MOBILITY_REDUCTION": False,
            "AUTO_SENIOR_MOBILITY_RESTORE": False,

            "AUTO_CHILD_MOBILITY_REDUCTION": False,
            "AUTO_CHILD_MOBILITY_RESTORE": False,

            "AUTO_LOCKDOWN": False,
            "AUTO_LOCKDOWN_RELEASE": False,

            "AUTO_WORK_CLOSURE": False,
            "AUTO_WORK_REOPEN": False,
        },
    },

    {
        "name": "Masks only",
        "description": "Masks are enabled, but other major interventions are disabled.",
        "overrides": {
            "SCENARIO_NAME": "Masks only",

            "MASKS_ENABLED": True,
            "MASK_COMPLIANCE": 0.50,
            "MASK_TRANSMISSION_REDUCTION": 0.40,

            "QUARANTINE_ENABLED": False,
            "TESTING_RATE": 0.0,
            "ISOLATION_RATE": 0.0,

            "AUTO_SCHOOL_CLOSURE": False,
            "AUTO_SCHOOL_REOPEN": False,

            "AUTO_MASK_COMPLIANCE": False,
            "AUTO_MASK_RELAXATION": False,

            "AUTO_TESTING_RATE": False,
            "AUTO_TESTING_RELAXATION": False,

            "AUTO_QUARANTINE_COMPLIANCE": False,
            "AUTO_QUARANTINE_RELAXATION": False,

            "AUTO_SENIOR_MOBILITY_REDUCTION": False,
            "AUTO_SENIOR_MOBILITY_RESTORE": False,

            "AUTO_CHILD_MOBILITY_REDUCTION": False,
            "AUTO_CHILD_MOBILITY_RESTORE": False,

            "AUTO_LOCKDOWN": False,
            "AUTO_LOCKDOWN_RELEASE": False,

            "AUTO_WORK_CLOSURE": False,
            "AUTO_WORK_REOPEN": False,
        },
    },

    {
        "name": "High mask compliance",
        "description": "High mask compliance and stronger mask protection.",
        "overrides": {
            "SCENARIO_NAME": "High mask compliance",

            "MASKS_ENABLED": True,
            "MASK_COMPLIANCE": 0.75,
            "MASK_TRANSMISSION_REDUCTION": 0.50,

            "AUTO_MASK_COMPLIANCE": False,
            "AUTO_MASK_RELAXATION": False,
        },
    },

    {
        "name": "No vaccination",
        "description": "Scenario without initial vaccination.",
        "overrides": {
            "SCENARIO_NAME": "No vaccination",

            "VACCINATION_RATE": 0.0,
            "VACCINE_EFFECTIVENESS": 0.0,
        },
    },

    {
        "name": "High vaccination coverage",
        "description": "Higher vaccination coverage and better vaccine effectiveness.",
        "overrides": {
            "SCENARIO_NAME": "High vaccination coverage",

            "VACCINATION_RATE": 0.70,
            "VACCINE_EFFECTIVENESS": 0.70,
        },
    },

    {
        "name": "Strong school control",
        "description": "Earlier school closure and stronger reduction of child mobility.",
        "overrides": {
            "SCENARIO_NAME": "Strong school control",

            "AUTO_SCHOOL_CLOSURE": True,
            "SCHOOL_CLOSURE_THRESHOLD": 50,
            "AUTO_SCHOOL_REOPEN": True,
            "SCHOOL_REOPEN_THRESHOLD": 5,

            "AUTO_CHILD_MOBILITY_REDUCTION": True,
            "CHILD_MOBILITY_THRESHOLD": 50,
            "LOW_CHILD_MOBILITY": 0.25,
            "AUTO_CHILD_MOBILITY_RESTORE": True,
            "CHILD_MOBILITY_RESTORE_THRESHOLD": 5,
        },
    },

    {
        "name": "No school closure",
        "description": "Schools remain open and child mobility is not reduced.",
        "overrides": {
            "SCENARIO_NAME": "No school closure",

            "AUTO_SCHOOL_CLOSURE": False,
            "AUTO_SCHOOL_REOPEN": False,

            "AUTO_CHILD_MOBILITY_REDUCTION": False,
            "AUTO_CHILD_MOBILITY_RESTORE": False,
        },
    },

    {
        "name": "Senior protection",
        "description": "Stronger protection of seniors through reduced senior mobility.",
        "overrides": {
            "SCENARIO_NAME": "Senior protection",

            "SENIOR_MOBILITY": 0.40,

            "AUTO_SENIOR_MOBILITY_REDUCTION": True,
            "SENIOR_MOBILITY_THRESHOLD": 20,
            "LOW_SENIOR_MOBILITY": 0.15,
            "AUTO_SENIOR_MOBILITY_RESTORE": True,
            "SENIOR_MOBILITY_RESTORE_THRESHOLD": 5,
        },
    },

    {
        "name": "No senior protection",
        "description": "Seniors have higher mobility and no adaptive senior protection.",
        "overrides": {
            "SCENARIO_NAME": "No senior protection",

            "SENIOR_MOBILITY": 0.85,

            "AUTO_SENIOR_MOBILITY_REDUCTION": False,
            "AUTO_SENIOR_MOBILITY_RESTORE": False,
        },
    },

    {
        "name": "Strong testing and quarantine",
        "description": "Higher testing rate and stronger quarantine compliance.",
        "overrides": {
            "SCENARIO_NAME": "Strong testing and quarantine",

            "TESTING_RATE": 0.45,
            "QUARANTINE_COMPLIANCE": 0.75,
            "DETECTED_TRANSMISSION_MULTIPLIER": 0.25,

            "AUTO_TESTING_RATE": True,
            "TESTING_RATE_THRESHOLD": 50,
            "HIGH_TESTING_RATE": 0.70,
            "AUTO_TESTING_RELAXATION": True,
            "TESTING_RELAXATION_THRESHOLD": 10,

            "AUTO_QUARANTINE_COMPLIANCE": True,
            "QUARANTINE_COMPLIANCE_THRESHOLD": 50,
            "HIGH_QUARANTINE_COMPLIANCE": 0.85,
            "AUTO_QUARANTINE_RELAXATION": True,
            "QUARANTINE_RELAXATION_THRESHOLD": 10,
        },
    },

    {
        "name": "Weak testing and quarantine",
        "description": "Lower testing rate and weaker quarantine compliance.",
        "overrides": {
            "SCENARIO_NAME": "Weak testing and quarantine",

            "TESTING_RATE": 0.05,
            "QUARANTINE_COMPLIANCE": 0.10,
            "DETECTED_TRANSMISSION_MULTIPLIER": 0.80,

            "AUTO_TESTING_RATE": False,
            "AUTO_TESTING_RELAXATION": False,

            "AUTO_QUARANTINE_COMPLIANCE": False,
            "AUTO_QUARANTINE_RELAXATION": False,
        },
    },

    {
        "name": "More transmissible strain",
        "description": "A more transmissible influenza strain with higher infection probability.",
        "overrides": {
            "SCENARIO_NAME": "More transmissible strain",

            "INFECTION_PROBABILITY": 0.00090,
            "ASYMPTOMATIC_TRANSMISSION_MULTIPLIER": 0.45,
        },
    },

    {
        "name": "Mild flu strain",
        "description": "A milder influenza strain with lower infection probability.",
        "overrides": {
            "SCENARIO_NAME": "Mild flu strain",

            "INFECTION_PROBABILITY": 0.00055,
            "ASYMPTOMATIC_TRANSMISSION_MULTIPLIER": 0.30,
        },
    },
]