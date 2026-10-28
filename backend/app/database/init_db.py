import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database.session import engine, Base, SessionLocal
from app.models.customer import Customer
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.product import BankingProduct
from app.models.faq import FAQ
from app.core.security import hash_password

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

def seed_database(db: Session):
    # Check if already seeded
    existing_customer = db.query(Customer).filter_by(id="cust_rajesh").first()
    if existing_customer:
        return

    # Seed Customers
    customers_data = [
        {
            "id": "cust_rajesh",
            "name": "Rajesh Kumar",
            "email": "demo.rajesh@nexabank.internal",
            "hashed_password": hash_password("demo123"),
            "phone": "+91 98765 43210",
            "occupation": "Lead Cloud Architect",
            "monthly_income": 145000.0,
            "credit_score": 785,
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"
        },
        {
            "id": "cust_priya",
            "name": "Priya Sharma",
            "email": "demo.priya@nexabank.internal",
            "hashed_password": hash_password("demo123"),
            "phone": "+91 98123 45678",
            "occupation": "Principal Product Designer",
            "monthly_income": 95000.0,
            "credit_score": 735,
            "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80"
        },
        {
            "id": "cust_vikram",
            "name": "Vikram Patel",
            "email": "demo.vikram@nexabank.internal",
            "hashed_password": hash_password("demo123"),
            "phone": "+91 99001 12233",
            "occupation": "Managing Consultant",
            "monthly_income": 210000.0,
            "credit_score": 810,
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"
        }
    ]

    for c_data in customers_data:
        db.add(Customer(**c_data))
    db.commit()

    # Seed Accounts
    accounts_data = [
        # Rajesh Accounts
        {
            "id": "acc_rajesh_sal",
            "customer_id": "cust_rajesh",
            "account_number_masked": "•••• 4821",
            "account_type": "CHECKING",
            "account_name": "NexaPriority Salary Checking",
            "currency": "INR",
            "balance": 94520.50,
            "available_balance": 92000.00,
            "status": "ACTIVE",
            "interest_rate": 3.5
        },
        {
            "id": "acc_rajesh_sav",
            "customer_id": "cust_rajesh",
            "account_number_masked": "•••• 9104",
            "account_type": "SAVINGS",
            "account_name": "NexaYield High-Interest Savings",
            "currency": "INR",
            "balance": 480000.00,
            "available_balance": 480000.00,
            "status": "ACTIVE",
            "interest_rate": 6.8
        },
        # Priya Accounts
        {
            "id": "acc_priya_chk",
            "customer_id": "cust_priya",
            "account_number_masked": "•••• 3392",
            "account_type": "CHECKING",
            "account_name": "NexaClassic Checking",
            "currency": "INR",
            "balance": 34200.00,
            "available_balance": 32500.00,
            "status": "ACTIVE",
            "interest_rate": 3.0
        },
        {
            "id": "acc_priya_sav",
            "customer_id": "cust_priya",
            "account_number_masked": "•••• 8821",
            "account_type": "SAVINGS",
            "account_name": "NexaGrowth Savings",
            "currency": "INR",
            "balance": 165000.00,
            "available_balance": 165000.00,
            "status": "ACTIVE",
            "interest_rate": 5.5
        },
        # Vikram Accounts
        {
            "id": "acc_vikram_chk",
            "customer_id": "cust_vikram",
            "account_number_masked": "•••• 1045",
            "account_type": "CHECKING",
            "account_name": "NexaWealth Elite Checking",
            "currency": "INR",
            "balance": 215400.00,
            "available_balance": 210000.00,
            "status": "ACTIVE",
            "interest_rate": 4.0
        },
        {
            "id": "acc_vikram_inv",
            "customer_id": "cust_vikram",
            "account_number_masked": "•••• 5529",
            "account_type": "INVESTMENT",
            "account_name": "NexaLiquid Treasury Deposit",
            "currency": "INR",
            "balance": 1500000.00,
            "available_balance": 1500000.00,
            "status": "ACTIVE",
            "interest_rate": 7.4
        }
    ]

    for acc in accounts_data:
        db.add(Account(**acc))
    db.commit()

    # Seed Transactions
    now = datetime.now(timezone.utc)
    
    # Days calculation for realistic "this month" and "last month"
    # Rajesh Transactions
    rajesh_txns = [
        # Recent this week / this month
        ("txn_r_01", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=1, hours=2), "Swiggy Gourmet Delivery", "DINING", 1240.00, "DEBIT"),
        ("txn_r_02", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=2, hours=5), "DMart Supermarket Koramangala", "GROCERIES", 4850.00, "DEBIT"),
        ("txn_r_03", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=3, hours=1), "Uber Premier City Ride", "TRAVEL", 450.00, "DEBIT"),
        ("txn_r_04", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=4, hours=8), "Tata Power Electricity Bill", "UTILITIES", 2680.00, "DEBIT"),
        ("txn_r_05", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=6, hours=3), "Amazon Retail Electronics", "SHOPPING", 8999.00, "DEBIT"),
        ("txn_r_06", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=7, hours=4), "Barbeque Nation Dinner", "DINING", 3450.00, "DEBIT"),
        ("txn_r_07", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=8, hours=2), "ACT Fibernet Broadband Bill", "UTILITIES", 1199.00, "DEBIT"),
        ("txn_r_08", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=10, hours=10), "Cult.fit Annual Fitness Plan", "HEALTHCARE", 4200.00, "DEBIT"),
        ("txn_r_09", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=12, hours=1), "Starbucks Reserve Coffee", "DINING", 680.00, "DEBIT"),
        ("txn_r_10", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=14, hours=6), "Nature's Basket Organic Groceries", "GROCERIES", 3120.00, "DEBIT"),
        ("txn_r_11", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=18, hours=12), "Monthly Salary Credit - TCS Solutions", "SALARY", 145000.00, "CREDIT"),
        ("txn_r_12", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=20, hours=4), "HP Fuel Station Petrol", "TRAVEL", 3200.00, "DEBIT"),
        ("txn_r_13", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=22, hours=3), "BookMyShow IMAX Movie Tickets", "ENTERTAINMENT", 1100.00, "DEBIT"),
        # Last Month (approx 35 to 55 days ago)
        ("txn_r_14", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=35, hours=2), "Zomato Dineout Bistro", "DINING", 2850.00, "DEBIT"),
        ("txn_r_15", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=38, hours=5), "BigBasket Monthly Pantry", "GROCERIES", 6400.00, "DEBIT"),
        ("txn_r_16", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=40, hours=3), "Bespoke Tailoring & Apparel", "SHOPPING", 6500.00, "DEBIT"),
        ("txn_r_17", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=44, hours=8), "Bangalore Water Supply & Sewerage", "UTILITIES", 1450.00, "DEBIT"),
        ("txn_r_18", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=48, hours=12), "Monthly Salary Credit - TCS Solutions", "SALARY", 145000.00, "CREDIT"),
        ("txn_r_19", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=50, hours=6), "Apollo Pharmacy Medications", "HEALTHCARE", 1750.00, "DEBIT"),
        ("txn_r_20", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=52, hours=1), "McDonalds Burger Order", "DINING", 920.00, "DEBIT"),
        ("txn_r_21", "acc_rajesh_sal", "cust_rajesh", now - timedelta(days=55, hours=3), "IndiGo Airlines Flight BLR-DEL", "TRAVEL", 7450.00, "DEBIT"),
        ("txn_r_22", "acc_rajesh_sav", "cust_rajesh", now - timedelta(days=15, hours=1), "Quarterly Savings Interest Credit", "INVESTMENTS", 7820.00, "CREDIT"),
        ("txn_r_23", "acc_rajesh_sav", "cust_rajesh", now - timedelta(days=45, hours=1), "Mutual Fund SIP Dividend Credit", "INVESTMENTS", 3450.00, "CREDIT"),
    ]

    # Priya Transactions
    priya_txns = [
        ("txn_p_01", "acc_priya_chk", "cust_priya", now - timedelta(days=1, hours=4), "Zomato Online Food Delivery", "DINING", 850.00, "DEBIT"),
        ("txn_p_02", "acc_priya_chk", "cust_priya", now - timedelta(days=2, hours=3), "Nature's Basket Provisions", "GROCERIES", 2400.00, "DEBIT"),
        ("txn_p_03", "acc_priya_chk", "cust_priya", now - timedelta(days=3, hours=7), "JioFiber Broadband Recharges", "UTILITIES", 999.00, "DEBIT"),
        ("txn_p_04", "acc_priya_chk", "cust_priya", now - timedelta(days=5, hours=2), "Zara Fashion Apparel", "SHOPPING", 4590.00, "DEBIT"),
        ("txn_p_05", "acc_priya_chk", "cust_priya", now - timedelta(days=8, hours=5), "Third Wave Coffee Roasters", "DINING", 480.00, "DEBIT"),
        ("txn_p_06", "acc_priya_chk", "cust_priya", now - timedelta(days=12, hours=4), "Bescom Power Utility", "UTILITIES", 1850.00, "DEBIT"),
        ("txn_p_07", "acc_priya_chk", "cust_priya", now - timedelta(days=15, hours=12), "Monthly Salary Credit - Studio Design", "SALARY", 95000.00, "CREDIT"),
        ("txn_p_08", "acc_priya_chk", "cust_priya", now - timedelta(days=17, hours=3), "Instamart Midnight Delivery", "GROCERIES", 1120.00, "DEBIT"),
        ("txn_p_09", "acc_priya_chk", "cust_priya", now - timedelta(days=21, hours=8), "Urban Company Salon Services", "HEALTHCARE", 1950.00, "DEBIT"),
        ("txn_p_10", "acc_priya_chk", "cust_priya", now - timedelta(days=25, hours=2), "PVR Inox Cinemas IMAX", "ENTERTAINMENT", 900.00, "DEBIT"),
        ("txn_p_11", "acc_priya_chk", "cust_priya", now - timedelta(days=36, hours=4), "Blue Tokai Coffee", "DINING", 620.00, "DEBIT"),
        ("txn_p_12", "acc_priya_chk", "cust_priya", now - timedelta(days=40, hours=2), "Spencers Supermarket", "GROCERIES", 3800.00, "DEBIT"),
        ("txn_p_13", "acc_priya_chk", "cust_priya", now - timedelta(days=45, hours=12), "Monthly Salary Credit - Studio Design", "SALARY", 95000.00, "CREDIT"),
        ("txn_p_14", "acc_priya_chk", "cust_priya", now - timedelta(days=48, hours=6), "FabIndia Ethnic Kurtis", "SHOPPING", 3200.00, "DEBIT"),
        ("txn_p_15", "acc_priya_sav", "cust_priya", now - timedelta(days=20, hours=1), "High Yield Savings Interest", "INVESTMENTS", 2250.00, "CREDIT"),
    ]

    # Vikram Transactions
    vikram_txns = [
        ("txn_v_01", "acc_vikram_chk", "cust_vikram", now - timedelta(days=1, hours=6), "Taj West End Business Lunch", "DINING", 4800.00, "DEBIT"),
        ("txn_v_02", "acc_vikram_chk", "cust_vikram", now - timedelta(days=2, hours=1), "Apple Store UB City (Accessories)", "SHOPPING", 14900.00, "DEBIT"),
        ("txn_v_03", "acc_vikram_chk", "cust_vikram", now - timedelta(days=4, hours=4), "Air India Flight Tickets BLR-BOM", "TRAVEL", 9800.00, "DEBIT"),
        ("txn_v_04", "acc_vikram_chk", "cust_vikram", now - timedelta(days=7, hours=2), "Grand Hyatt Mumbai Accommodation", "TRAVEL", 18500.00, "DEBIT"),
        ("txn_v_05", "acc_vikram_chk", "cust_vikram", now - timedelta(days=10, hours=5), "Adani Gas & Electricity Utilities", "UTILITIES", 4200.00, "DEBIT"),
        ("txn_v_06", "acc_vikram_chk", "cust_vikram", now - timedelta(days=14, hours=12), "Consulting Retainer - Tech Advisory", "SALARY", 210000.00, "CREDIT"),
        ("txn_v_07", "acc_vikram_chk", "cust_vikram", now - timedelta(days=18, hours=3), "Whole Foods Market Provisions", "GROCERIES", 5400.00, "DEBIT"),
        ("txn_v_08", "acc_vikram_chk", "cust_vikram", now - timedelta(days=22, hours=1), "Smoke House Deli Dinner", "DINING", 3900.00, "DEBIT"),
        ("txn_v_09", "acc_vikram_inv", "cust_vikram", now - timedelta(days=15, hours=2), "Treasury Quarterly Yield Credit", "INVESTMENTS", 27750.00, "CREDIT"),
        ("txn_v_10", "acc_vikram_chk", "cust_vikram", now - timedelta(days=35, hours=4), "Leela Palace Executive Dining", "DINING", 6200.00, "DEBIT"),
        ("txn_v_11", "acc_vikram_chk", "cust_vikram", now - timedelta(days=42, hours=12), "Consulting Retainer - Tech Advisory", "SALARY", 210000.00, "CREDIT"),
        ("txn_v_12", "acc_vikram_chk", "cust_vikram", now - timedelta(days=46, hours=5), "Samsung Smart Display", "SHOPPING", 24999.00, "DEBIT"),
    ]

    all_txns = rajesh_txns + priya_txns + vikram_txns
    for tid, aid, cid, ts, desc, cat, amt, dirc in all_txns:
        db.add(Transaction(
            id=tid,
            account_id=aid,
            customer_id=cid,
            timestamp=ts,
            merchant_or_description=desc,
            category=cat,
            amount=amt,
            direction=dirc,
            status="COMPLETED",
            reference_number=f"REF-{tid.upper()}-NX"
        ))
    db.commit()

    # Seed Banking Products
    products_data = [
        {
            "id": "prod_pl_flexi",
            "product_type": "PERSONAL_LOAN",
            "name": "NexaFlexi Personal Loan",
            "headline": "Instant collateral-free personal financing with flexible repayment",
            "interest_rate": 10.75,
            "rate_type": "Fixed",
            "min_amount": 50000.0,
            "max_amount": 4000000.0,
            "min_tenure_months": 12,
            "max_tenure_months": 60,
            "processing_fee_pct": 1.0,
            "eligibility_criteria_summary": "Minimum age 21, net monthly income >= ₹35,000, credit score >= 700, maximum DTI <= 50%.",
            "min_income_monthly": 35000.0,
            "min_credit_score": 700
        },
        {
            "id": "prod_hl_dream",
            "product_type": "HOME_LOAN",
            "name": "NexaDream Home Loan",
            "headline": "Realize your home ownership dream with benchmark-linked affordable rates",
            "interest_rate": 8.40,
            "rate_type": "Floating",
            "min_amount": 500000.0,
            "max_amount": 30000000.0,
            "min_tenure_months": 24,
            "max_tenure_months": 360,
            "processing_fee_pct": 0.35,
            "eligibility_criteria_summary": "Salaried/self-employed, net monthly income >= ₹50,000, credit score >= 720, property verification required.",
            "min_income_monthly": 50000.0,
            "min_credit_score": 720
        },
        {
            "id": "prod_fd_yield",
            "product_type": "FIXED_DEPOSIT",
            "name": "NexaYield Fixed Deposit",
            "headline": "Guaranteed attractive returns with compounding interest choices",
            "interest_rate": 7.25,
            "rate_type": "Fixed",
            "min_amount": 10000.0,
            "max_amount": 50000000.0,
            "min_tenure_months": 6,
            "max_tenure_months": 120,
            "processing_fee_pct": 0.0,
            "eligibility_criteria_summary": "All existing NexaBank account holders. Premature withdrawal allowed with 0.5% rate adjustment.",
            "min_income_monthly": 0.0,
            "min_credit_score": 300
        },
        {
            "id": "prod_sa_max",
            "product_type": "SAVINGS_ACCOUNT",
            "name": "NexaMax Savings Account",
            "headline": "Zero-maintenance smart digital savings with daily interest accrual",
            "interest_rate": 4.00,
            "rate_type": "Tiered",
            "min_amount": 1000.0,
            "max_amount": 100000000.0,
            "min_tenure_months": 0,
            "max_tenure_months": 0,
            "processing_fee_pct": 0.0,
            "eligibility_criteria_summary": "Residents with valid KYC, instant digital onboarding.",
            "min_income_monthly": 0.0,
            "min_credit_score": 300
        }
    ]

    for p in products_data:
        db.add(BankingProduct(**p))
    db.commit()

    # Seed FAQs
    faqs_data = [
        {
            "id": "faq_01",
            "category": "STATEMENTS",
            "question": "How do I download my monthly account statement?",
            "answer": "You can download monthly statements by visiting 'My Accounts' > selecting your account > and clicking 'Download Statement (PDF/Excel)'. Alternatively, say 'Download my statement' in chat.",
            "keywords": "statement download pdf excel account transactions"
        },
        {
            "id": "faq_02",
            "category": "CARDS",
            "question": "How can I block or reset my debit card PIN?",
            "answer": "Go to 'Profile & Security' > 'Card Management'. You can instantly freeze your card or set a new 4-digit PIN using biometric or secure OTP verification.",
            "keywords": "debit card pin reset block freeze lost stolen"
        },
        {
            "id": "faq_03",
            "category": "LOANS",
            "question": "What documents are required for home loan tax benefit certificates?",
            "answer": "Tax exemption certificates under Section 24 (interest component up to ₹2 Lakh) and Section 80C (principal repayment up to ₹1.5 Lakh) are automatically generated at financial year end and downloadable in 'Loans & Interest Rates'.",
            "keywords": "tax certificate home loan section 24 section 80c interest principal"
        },
        {
            "id": "faq_04",
            "category": "TRANSFERS",
            "question": "What are the daily UPI and NEFT transfer limits?",
            "answer": "NexaBank standard limits are: UPI up to ₹1,00,000 per day; IMPS up to ₹5,00,000 per day; NEFT/RTGS unlimited during banking hours for verified priority accounts.",
            "keywords": "upi limit neft imps transfer maximum money transfer"
        },
        {
            "id": "faq_05",
            "category": "INTEREST",
            "question": "How often is savings account interest calculated and credited?",
            "answer": "Savings account interest is calculated daily on the end-of-day ledger balance and credited to your account on the last day of each calendar quarter.",
            "keywords": "savings interest rate calculation frequency quarterly credit"
        }
    ]

    for f in faqs_data:
        db.add(FAQ(**f))
    db.commit()
    print("NexaBank database initialized and seeded successfully.")

if __name__ == "__main__":
    init_db()
