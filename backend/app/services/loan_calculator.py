import math
from typing import Dict, Any
from app.models.product import BankingProduct
from app.models.customer import Customer
from app.schemas.banking import LoanEligibilityResponse

def calculate_emi(principal: float, annual_rate_pct: float, tenure_months: int) -> float:
    """Calculate standard monthly EMI using amortization formula."""
    if tenure_months <= 0 or principal <= 0:
        return 0.0
    r = (annual_rate_pct / 100.0) / 12.0
    if r == 0:
        return principal / tenure_months
    emi = principal * r * ((1 + r) ** tenure_months) / (((1 + r) ** tenure_months) - 1)
    return round(emi, 2)

def evaluate_loan_eligibility(
    customer: Customer,
    product: BankingProduct,
    requested_amount: float,
    tenure_months: int,
    declared_monthly_income: float = None,
    declared_existing_emis: float = 0.0
) -> LoanEligibilityResponse:
    """
    Deterministic rule-based loan eligibility evaluation.
    Enforces strict risk guidelines with transparent explanations.
    """
    income = declared_monthly_income if declared_monthly_income is not None else customer.monthly_income
    existing_emis = declared_existing_emis or 0.0
    credit_score = customer.credit_score
    rate = product.interest_rate

    # Calculate requested EMI
    requested_emi = calculate_emi(requested_amount, rate, tenure_months)
    total_monthly_obligations = existing_emis + requested_emi
    dti_ratio_pct = round((total_monthly_obligations / income * 100.0), 2) if income > 0 else 100.0

    # Rule checks
    income_ok = income >= product.min_income_monthly
    credit_ok = credit_score >= product.min_credit_score
    tenure_ok = product.min_tenure_months <= tenure_months <= product.max_tenure_months
    amount_range_ok = product.min_amount <= requested_amount <= product.max_amount
    dti_ok = dti_ratio_pct <= 50.0  # Max allowable DTI is 50%

    criteria_evaluation = {
        f"Monthly Income >= ₹{product.min_income_monthly:,.0f}": income_ok,
        f"Credit Score >= {product.min_credit_score} (Your score: {credit_score})": credit_ok,
        f"Tenure ({tenure_months} mo) within [{product.min_tenure_months}-{product.max_tenure_months}]": tenure_ok,
        f"Requested amount within limits": amount_range_ok,
        f"Debt-to-Income ratio <= 50% (Calculated: {dti_ratio_pct}%)": dti_ok
    }

    # Max affordable EMI calculation (50% max DTI capacity)
    max_allowable_total_emi = income * 0.50
    available_emi_capacity = max(0.0, max_allowable_total_emi - existing_emis)
    
    # Invert EMI formula to compute max loan amount possible with available EMI capacity
    r = (rate / 100.0) / 12.0
    if r > 0 and tenure_months > 0:
        factor = ((1 + r) ** tenure_months - 1) / (r * ((1 + r) ** tenure_months))
        max_possible_principal = available_emi_capacity * factor
    else:
        max_possible_principal = available_emi_capacity * tenure_months

    max_eligible_amount = min(product.max_amount, round(max_possible_principal, -3))
    if max_eligible_amount < product.min_amount:
        max_eligible_amount = 0.0

    # Determine status & reason
    if not amount_range_ok and requested_amount > product.max_amount:
        eligible = False
        status_val = "REJECTED"
        approved_amount = 0.0
        reason = f"Requested amount ₹{requested_amount:,.2f} exceeds the maximum loan ceiling of ₹{product.max_amount:,.2f} for {product.name}."
    elif income_ok and credit_ok and tenure_ok and amount_range_ok and dti_ok:
        eligible = True
        status_val = "APPROVED"
        approved_amount = requested_amount
        reason = f"Congratulations! You meet all indicative criteria for {product.name}. With a net monthly income of ₹{income:,.2f} and credit score of {credit_score}, your debt-to-income ratio is {dti_ratio_pct}%, comfortably below our 50% risk threshold."
    elif income_ok and credit_ok and tenure_ok and amount_range_ok and not dti_ok and max_eligible_amount >= product.min_amount:
        eligible = True
        status_val = "CONDITIONAL"
        approved_amount = min(requested_amount, max_eligible_amount)
        reason = f"Your requested loan of ₹{requested_amount:,.2f} exceeds the recommended 50% debt-to-income threshold ({dti_ratio_pct}%). However, based on your income and credit profile, you are indicatively eligible for a pre-qualified limit of ₹{approved_amount:,.2f}."
    else:
        eligible = False
        status_val = "REJECTED"
        approved_amount = 0.0
        failures = []
        if not income_ok:
            failures.append(f"monthly income (₹{income:,.2f}) is below minimum required ₹{product.min_income_monthly:,.2f}")
        if not credit_ok:
            failures.append(f"credit score ({credit_score}) is below benchmark {product.min_credit_score}")
        if not dti_ok:
            failures.append(f"projected DTI of {dti_ratio_pct}% exceeds maximum risk ceiling of 50%")
        if not tenure_ok:
            failures.append(f"tenure must be between {product.min_tenure_months} and {product.max_tenure_months} months")
        if not amount_range_ok:
            failures.append(f"amount must be between ₹{product.min_amount:,.2f} and ₹{product.max_amount:,.2f}")
        reason = f"We are unable to recommend approval at this time because: {', '.join(failures)}."

    effective_emi = calculate_emi(approved_amount, rate, tenure_months) if approved_amount > 0 else 0.0

    return LoanEligibilityResponse(
        eligible=eligible,
        status=status_val,
        product_type=product.product_type,
        requested_amount=requested_amount,
        approved_amount=approved_amount,
        tenure_months=tenure_months,
        interest_rate=rate,
        estimated_emi=effective_emi,
        debt_to_income_ratio_pct=dti_ratio_pct,
        reason=reason,
        criteria_evaluation=criteria_evaluation,
        disclaimer="Illustrative demonstration calculation only. Not an actual credit decision or binding financial offer."
    )
