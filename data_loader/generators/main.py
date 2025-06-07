from datetime import datetime
from generators.customers import CustomerGenerator
from generators.accounts import AccountGenerator
from generators.customer_accounts import CustomerAccountMapper
from generators.transactions import TransactionGenerator

customer_ids = CustomerGenerator(10).generate_and_save("data/customers.csv")
account_ids = AccountGenerator(15).generate_and_save("data/accounts.csv")
mapped_account_ids = CustomerAccountMapper(customer_ids, account_ids).generate_and_save("data/customer_accounts.csv")
TransactionGenerator(mapped_account_ids, datetime(2025, 1, 1), 100).generate_and_save("data/transactions.csv")
