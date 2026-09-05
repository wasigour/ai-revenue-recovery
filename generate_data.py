import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
N = 1000

error_profiles = [
    {"code": "INSUFFICIENT_FUNDS", "type": "soft_user", "weight": 0.40, "base_rec_prob": 0.65},
    {"code": "ISSUER_DOWN", "type": "soft_tech", "weight": 0.25, "base_rec_prob": 0.85},
    {"code": "GATEWAY_TIMEOUT", "type": "soft_tech", "weight": 0.15, "base_rec_prob": 0.80},
    {"code": "MANDATE_REVOKED", "type": "hard_failure", "weight": 0.10, "base_rec_prob": 0.10},
    {"code": "EXPIRED_CARD", "type": "hard_failure", "weight": 0.10, "base_rec_prob": 0.05},
]

payment_methods = ["UPI_AUTOPAY", "CARD_RECURRING", "NACH", "NETBANKING"]
banks = ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK"]

records = []
now = datetime.now()

for i in range(N):
    err = np.random.choice(error_profiles, p=[e["weight"] for e in error_profiles])
    amount = round(random.choice([299, 499, 999, 1499, 2999, 4999, 9999]), 2)
    method = random.choice(payment_methods)
    bank = random.choice(banks)
    tenure_months = random.randint(1, 36)
    failure_time = now - timedelta(days=random.randint(1, 14), hours=random.randint(0, 23))
    
    records.append({
        "transaction_id": f"txn_{10000+i}",
        "customer_id": f"cust_{2000+random.randint(1, 400)}",
        "amount": amount,
        "payment_method": method,
        "bank_code": bank,
        "failure_code": err["code"],
        "failure_type": err["type"],
        "customer_tenure_months": tenure_months,
        "failure_timestamp": failure_time.strftime("%Y-%m-%d %H:%M:%S"),
        "customer_reply_intent": random.choice(["NONE", "PAY_LATER", "CANCEL_REQUEST", "ALREADY_PAID", "FAILED_AGAIN"])
    })

df = pd.DataFrame(records)
df.to_csv("failed_transactions.csv", index=False)
print("Generated 1,000 synthetic failed transactions in failed_transactions.csv")
