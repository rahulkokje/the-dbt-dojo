import uuid, random
from .base import BaseGenerator

class CustomerAccountMapper(BaseGenerator):
    def __init__(self, customer_ids, account_ids):
        self.customer_ids = customer_ids
        self.account_ids = account_ids

    def generate_mapping(self):
        mappings = []
        for customer_id in self.customer_ids:
            assigned_accounts = random.sample(self.account_ids, random.randint(1, 3))
            for account_id in assigned_accounts:
                mappings.append([str(uuid.uuid4()), customer_id, account_id])
        return mappings

    def generate_and_save(self, filepath):
        rows = self.generate_mapping()
        self.save_to_csv(filepath, ["id", "customer_id", "account_id"], rows)
        return [row[2] for row in rows]
