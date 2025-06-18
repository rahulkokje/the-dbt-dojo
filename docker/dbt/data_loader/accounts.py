import logging
import random
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List

from faker import Faker


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("accounts")

fake = Faker()


@dataclass
class AccountAuditRecord:
    audit_id: str
    account_id: str
    status: str
    type: str
    legal_entity: str
    created_at: datetime
    updated_at: datetime
    audit_operation: str  # 'I' (insert) or 'U' (update)
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    @classmethod
    def create_new(cls, account_type: str, customer_created_at: datetime) -> "AccountAuditRecord":
        account_id = str(uuid.uuid4())
        timestamp = fake.past_datetime(start_date=customer_created_at)
        return cls(
            audit_id=str(uuid.uuid4()),
            account_id=account_id,
            status="OPEN",
            opened_at=timestamp,
            type=account_type,
            legal_entity=random.choice(["EU", "IT", "FR", "ES"]),
            created_at=timestamp,
            updated_at=timestamp,
            audit_operation="I"
        )

    def as_tuple(self) -> Tuple:
        return (
            self.audit_id,
            self.account_id,
            self.status,
            self.opened_at,
            self.closed_at,
            self.type,
            self.legal_entity,
            self.created_at,
            self.updated_at,
            self.audit_operation
        )


@dataclass
class CustomerAccountLink:
    customer_id: str
    account_id: str
    role: str  # 'OWNER' or 'MEMBER'
    action: str  # 'ADDED' or 'REMOVED'
    created_at: datetime

    def as_tuple(self) -> Tuple:
        return self.customer_id, self.account_id, self.role, self.action, self.created_at


class AccountGenerator:
    ACCOUNT_INSERT_SQL = """
            INSERT INTO raw.account_audit (
                audit_id, account_id, status, opened_at, closed_at,
                type, legal_entity, created_at, updated_at, audit_operation
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

    CUSTOMER_ACCOUNT_INSERT_SQL = """
            INSERT INTO raw.customer_accounts (
                customer_id, account_id, role, action, created_at
            ) VALUES (%s, %s, %s, %s, %s)
        """

    def __init__(self, conn):
        self.conn = conn

    def create_accounts_for_customer(
            self,
            customer_id: str,
            customer_created_at: datetime,
            valid_customer_ids: List[str]
    ) -> None:
        account_records: List[AccountAuditRecord] = []
        customer_accounts_records: List[CustomerAccountLink] = []

        # 1 CURRENT account
        current_acc = AccountAuditRecord.create_new("CURRENT", customer_created_at)
        account_records.append(current_acc)
        customer_accounts_records.append(CustomerAccountLink(
            customer_id,
            current_acc.account_id,
            "OWNER",
            "ADDED",
            current_acc.created_at
        ))

        # At most 1 SAVINGS account
        if random.random() < 0.5:
            savings_acc = AccountAuditRecord.create_new("SAVINGS", customer_created_at)
            account_records.append(savings_acc)
            customer_accounts_records.append(CustomerAccountLink(
                customer_id,
                savings_acc.account_id,
                "OWNER",
                "ADDED",
                savings_acc.created_at
            ))

        # 0 or more SUB-ACCOUNT
        for _ in range(random.randint(0, 2)):
            sub_acc = AccountAuditRecord.create_new("SUB-ACCOUNT", customer_created_at)
            account_records.append(sub_acc)
            # Owner
            customer_accounts_records.append(CustomerAccountLink(
                customer_id,
                sub_acc.account_id,
                "OWNER",
                "ADDED",
                sub_acc.created_at
            ))
            # Randomly assign 0–2 members who are NOT the owner
            eligible_members = [cid for cid in valid_customer_ids if cid != customer_id]
            members = random.sample(eligible_members, k=random.randint(0, min(2, len(eligible_members))))
            for member_id in members:
                customer_accounts_records.append(CustomerAccountLink(
                    member_id,
                    sub_acc.account_id,
                    "MEMBER",
                    "ADDED",
                    fake.past_datetime(start_date=sub_acc.created_at)
                ))

        try:
            # Insert into DB
            with self.conn.cursor() as cur:
                cur.executemany(self.ACCOUNT_INSERT_SQL, [acc.as_tuple() for acc in account_records])
                cur.executemany(self.CUSTOMER_ACCOUNT_INSERT_SQL, [link.as_tuple() for link in customer_accounts_records])
            self.conn.commit()
        except Exception as e:
            logger.exception(f"❌ Failed to create accounts for customer {customer_id}.")
            raise

        logger.info(f"✅ Created {len(account_records)} accounts for customer {customer_id}")