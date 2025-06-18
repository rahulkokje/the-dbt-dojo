import logging
import random
import uuid
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Tuple, Dict

import psycopg2
from psycopg2.extensions import connection as PgConnection
from faker import Faker

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("customers")

fake = Faker()


@dataclass
class CustomerAuditRecord:
    audit_id: str
    customer_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    kyc_status: str
    tnc_country_code: str
    created_at: datetime
    updated_at: datetime
    audit_operation: str  # 'I' (insert) or 'U' (update)

    @classmethod
    def create_new(cls) -> "CustomerAuditRecord":
        customer_id = str(uuid.uuid4())
        timestamp = fake.past_datetime(start_date=datetime(year=2024, month=1, day=1))
        return cls(
            audit_id=str(uuid.uuid4()),
            customer_id=customer_id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            kyc_status=random.choice(["PENDING", "VERIFIED"]),
            tnc_country_code=random.choice(["DE", "FR", "ES", "IT", "AU"]),
            created_at=timestamp,
            updated_at=timestamp,
            audit_operation="I"
        )

    @classmethod
    def create_updated(cls, previous: "CustomerAuditRecord") -> "CustomerAuditRecord":
        updated_fields = {
            "first_name": previous.first_name,
            "last_name": previous.last_name,
            "date_of_birth": previous.date_of_birth,
            "kyc_status": previous.kyc_status
        }

        changeable_fields = list(updated_fields.keys())
        field_changed = False

        for field in changeable_fields:
            if random.random() < 0.3:
                if field == "first_name":
                    updated_fields["first_name"] = fake.first_name()
                elif field == "last_name":
                    updated_fields["last_name"] = fake.last_name()
                elif field == "date_of_birth":
                    updated_fields["date_of_birth"] = fake.date_of_birth(minimum_age=18, maximum_age=80)
                elif field == "kyc_status" and previous.kyc_status == "PENDING":
                    updated_fields["kyc_status"] = "VERIFIED"
                field_changed = True

        if not field_changed:
            field = random.choice(changeable_fields[:3])
            if field == "first_name":
                updated_fields["first_name"] = fake.first_name()
            elif field == "last_name":
                updated_fields["last_name"] = fake.last_name()
            elif field == "date_of_birth":
                updated_fields["date_of_birth"] = fake.date_of_birth(minimum_age=18, maximum_age=80)

        return cls(
            audit_id=str(uuid.uuid4()),
            customer_id=previous.customer_id,
            first_name=updated_fields["first_name"],
            last_name=updated_fields["last_name"],
            date_of_birth=updated_fields["date_of_birth"],
            kyc_status=updated_fields["kyc_status"],
            tnc_country_code=previous.tnc_country_code,
            created_at=previous.created_at,
            updated_at=datetime.now(),
            audit_operation="U"
        )

    def as_tuple(self) -> Tuple:
        return (
            self.audit_id,
            self.customer_id,
            self.first_name,
            self.last_name,
            self.date_of_birth,
            self.kyc_status,
            self.tnc_country_code,
            self.created_at,
            self.updated_at,
            self.audit_operation,
        )


class CustomerGenerator:
    INSERT_SQL = """
        INSERT INTO raw.customer_audit (
            audit_id, customer_id, first_name, last_name,
            date_of_birth, kyc_status, tnc_country_code,
            created_at, updated_at, audit_operation
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    def __init__(self, conn: Optional[PgConnection]):
        self.conn = conn

    def load_initial_data(self, no_of_customers: int = 10) -> None:
        customers: List[CustomerAuditRecord] = [CustomerAuditRecord.create_new() for _ in range(no_of_customers)]
        try:
            self._insert_records(customers)
            logger.info(f"✅ Loaded {no_of_customers} new customers.")
        except Exception as e:
            logger.exception(f"❌ Failed to load initial customer data.")

    def update_random_customers(self, count: int = 5) -> None:
        try:
            customer_ids = self._get_random_customer_ids(count)
            updated_records: List[CustomerAuditRecord] = []

            with self.conn.cursor() as cur:
                for customer_id in customer_ids:
                    cur.execute("""
                        SELECT *
                        FROM raw.customer_audit
                        WHERE customer_id = %s
                        ORDER BY updated_at DESC
                        LIMIT 1
                    """, (customer_id,))
                    row = cur.fetchone()
                    if not row:
                        continue

                    previous = CustomerAuditRecord(*row)
                    updated = CustomerAuditRecord.create_updated(previous)
                    updated_records.append(updated)

            self._insert_records(updated_records)
            logger.info(f"✅ Updated {len(updated_records)} customers.")
        except Exception as e:
            logger.exception("❌ Failed to update customers.")

    def get_all_customers_created_date(self) -> Dict[str, datetime]:
        """
        Returns a dictionary mapping customer_id -> created_at (as datetime object)
        based on the earliest created_at per customer from customer_audit.
        """
        result: Dict[str, datetime] = {}
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT customer_id, MIN(created_at) AS created_at
                    FROM raw.customer_audit
                    GROUP BY customer_id
                """)
                rows = cur.fetchall()
                result = {row[0]: row[1] for row in rows}
        except Exception as e:
            print(f"❌ Error fetching customer IDs: {e}")
        return result

    def _get_random_customer_ids(self, count: int) -> List[str]:
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT customer_id
                    FROM (
                        SELECT customer_id
                        FROM raw.customer_audit
                        GROUP BY customer_id
                        ORDER BY RANDOM()
                        LIMIT %s
                    ) sub;
                """, (count,))
                return [row[0] for row in cur.fetchall()]
        except Exception as e:
            logger.exception("❌ Failed to fetch random customer_ids.")
            raise

    def _insert_records(self, records: List[CustomerAuditRecord]) -> None:
        try:
            with self.conn.cursor() as cur:
                cur.executemany(self.INSERT_SQL, [record.as_tuple() for record in records])
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.exception("❌ Failed to insert customer records.")
            raise


if __name__ == "__main__":
    conn = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="dojo_db",
            user="dojo_user",
            password="dojo_pass"
        )
        customer_generator = CustomerGenerator(conn)
        logger.info(customer_generator.get_all_customers_created_date())
    except Exception as e:
        logger.critical("❌ Could not complete customer data generation.")
    finally:
        if conn:
            conn.close()
