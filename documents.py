"""
Synthetic sample legal-insurance policy documents, for demo/testing purposes.
These are invented text, not real policy language — replace with real
(anonymized) documents if you deploy this against an actual use case.
"""

POLICY_DOCUMENTS = [
    {
        "id": "policy_001_liability",
        "title": "Standard Liability Coverage — Section 4: Exclusions",
        "text": (
            "This policy excludes coverage for damages arising from intentional acts "
            "by the insured, claims filed more than 24 months after the incident date, "
            "and any incident occurring while the insured was operating a vehicle "
            "without a valid license. Coverage is capped at CHF 500,000 per incident."
        ),
    },
    {
        "id": "policy_002_legal_defense",
        "title": "Legal Defense Coverage — Section 2: Scope",
        "text": (
            "Legal defense coverage applies to civil disputes involving contracts, "
            "employment matters, and property disputes where the insured is the "
            "defendant. Criminal proceedings and disputes between the insured and "
            "an immediate family member are explicitly excluded from this coverage."
        ),
    },
    {
        "id": "policy_003_claim_process",
        "title": "Claims Process — Section 1: Filing Requirements",
        "text": (
            "Claims must be filed within 30 days of the triggering incident. Required "
            "documentation includes a completed claim form, an incident report, and "
            "any relevant correspondence. Claims missing required documentation will "
            "be returned to the claimant with a 14-day window to resubmit."
        ),
    },
    {
        "id": "policy_004_premium_terms",
        "title": "Premium and Deductible Terms — Section 3",
        "text": (
            "The annual premium is CHF 1,200, payable quarterly. The standard "
            "deductible is CHF 500 per claim. Policyholders with three or more "
            "claims in a 12-month period are subject to a deductible increase to "
            "CHF 1,000 upon renewal."
        ),
    },
    {
        "id": "policy_005_dispute_resolution",
        "title": "Dispute Resolution — Section 6",
        "text": (
            "Disputes regarding claim denial must first go through internal appeal "
            "within 60 days of denial notice. If unresolved, disputes proceed to "
            "binding arbitration under Swiss law, with arbitration costs shared "
            "equally between the insurer and the policyholder."
        ),
    },
]
