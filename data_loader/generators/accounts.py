import uuid, random
from .base import BaseGenerator

class AccountGenerator(BaseGenerator):
    def __init__(self, num_accounts):
        self.num_accounts = num_accounts

    def generate_account(self):
        return [
            str(uuid.uuid4()),
            "DE" + str(random.randint(10**20, 10**21 - 1)),
            random.choice(["CURRENT", "SAVINGS"]),
            random.choice(["CREATED", "OPEN", "CLOSED", "SEIZED"])
        ]

    def generate_and_save(self, filepath):
        rows = [self.generate_account() for _ in range(self.num_accounts)]
        self.save_to_csv(filepath, ["account_id", "iban", "account_type", "account_status"], rows)
        return [row[0] for row in rows]
