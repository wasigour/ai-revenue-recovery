import pandas as pd
from datetime import datetime

class RecoveryAgent:
    def __init__(self):
        # Strict hardcoded guardrails
        self.max_retries = 2
        self.compliant_start_hour = 8
        self.compliant_end_hour = 19
        
    def check_compliance_window(self):
        """Ensures we only send messages between 8 AM and 7 PM IST."""
        current_hour = datetime.now().hour
        return self.compliant_start_hour <= current_hour < self.compliant_end_hour

    def diagnose_and_route(self, transaction):
        """
        Takes a single failed transaction dictionary and routes it to the correct action.
        """
        # Guardrail 1: Check for explicit opt-outs immediately
        if transaction['customer_reply_intent'] == "CANCEL_REQUEST":
            return self._terminate(transaction['transaction_id'], "Customer requested cancellation. Halting recovery.")

        failure_type = transaction['failure_type']
        
        # Route 1: Hard Failures (Cannot be fixed by silent retries)
        if failure_type == "hard_failure":
            if self.check_compliance_window():
                return self._trigger_user_nudge(transaction, urgency="high")
            else:
                return self._queue_for_morning(transaction)

        # Route 2: Soft Technical Failures (Gateway/Bank issues)
        elif failure_type == "soft_tech":
            return self._trigger_silent_retry(transaction)

        # Route 3: Soft User Failures (Insufficient Funds)
        elif failure_type == "soft_user":
            # Here we would normally check if today is payday (1st-5th of month)
            if self.check_compliance_window():
                return self._trigger_user_nudge(transaction, urgency="medium")
            else:
                return self._queue_for_morning(transaction)

        return self._terminate(transaction['transaction_id'], "Unknown failure type.")
        

    def _trigger_silent_retry(self, txn):
        # In production, this hits the Razorpay API to retry the mandate
        return {
            "action": "SILENT_RETRY",
            "transaction_id": txn['transaction_id'],
            "reason": f"Algorithmic retry for {txn['failure_code']}",
            "cost_incurred": 0.50 # Simulated API cost in INR
        }

    def _trigger_user_nudge(self, txn, urgency):
        # This is where we will inject our LLM to write a contextual WhatsApp message
        return {
            "action": "DISPATCH_WHATSAPP_NUDGE",
            "transaction_id": txn['transaction_id'],
            "reason": f"Requires alternative payment method for {txn['failure_code']}",
            "context": urgency
        }
        
    def _queue_for_morning(self, txn):
        return {
            "action": "QUEUED_FOR_COMPLIANT_WINDOW",
            "transaction_id": txn['transaction_id'],
            "reason": "Outside allowed RBI communication hours (8 AM - 7 PM)."
        }

    def _terminate(self, txn_id, reason):
        return {
            "action": "TERMINATED",
            "transaction_id": txn_id,
            "reason": reason
        }

if __name__ == "__main__":
    df = pd.read_csv("failed_transactions.csv")
    
    agent = RecoveryAgent()
    
    print("Testing the routing logic on the first 5 transactions...\n")
    for index, row in df.head(5).iterrows():
        decision = agent.diagnose_and_route(row.to_dict())
        print(f"TXN: {decision['transaction_id']} | ACTION: {decision['action']} | REASON: {decision['reason']}")
