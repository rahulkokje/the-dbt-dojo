import uuid, random
from datetime import datetime, timedelta
from .base import BaseGenerator

class TransactionGenerator(BaseGenerator):
    def __init__(self, account_ids, start_date, num_records):
        self.account_ids = account_ids
        self.start_date = start_date
        self.num_records = num_records

    def generate_transaction(self):
        return [
            str(uuid.uuid4()),
            (self.start_date + timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d"),
            random.choice(["CREDIT", "DEBIT"]),
            random.choice(self.account_ids),
            round(random.uniform(10.0, 5000.0), 2)
        ]

    def generate_and_save(self, filepath):
        rows = [self.generate_transaction() for _ in range(self.num_records)]
        self.save_to_csv(filepath, ["transaction_id", "transaction_date", "type", "account_id", "amount"], rows)
