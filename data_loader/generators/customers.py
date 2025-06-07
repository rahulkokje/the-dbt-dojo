import uuid, random
from datetime import datetime
from .base import BaseGenerator

class CustomerGenerator(BaseGenerator):
    def __init__(self, num_customers):
        self.num_customers = num_customers
        self.kyc_statuses = ["VERIFIED", "PENDING", "FAILED"]
        self.country_codes = ["US", "CA", "GB", "IN", "AU"]

    def generate_customer(self):
        return [
            str(uuid.uuid4()),
            random.choice(["John", "Jane", "Emma"]),
            random.choice(["Smith", "Brown", "Johnson"]),
            datetime.strptime(f"{random.randint(1960, 2005)}-{random.randint(1,12)}-{random.randint(1,28)}", "%Y-%m-%d").strftime("%Y-%m-%d"),
            random.choice(self.kyc_statuses),
            random.choice(self.country_codes)
        ]

    def generate_and_save(self, filepath):
        rows = [self.generate_customer() for _ in range(self.num_customers)]
        self.save_to_csv(filepath, ["customer_id", "first_name", "last_name", "date_of_birth", "kyc_status", "tnc_country_code"], rows)
        return [row[0] for row in rows]
