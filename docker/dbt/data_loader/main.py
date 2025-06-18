from data_loader import db
from data_loader.accounts import AccountGenerator
from data_loader.customers import CustomerGenerator


def main() -> None:
    # Get DB Connection
    conn = db.get_connection()

    # Get Customer Generator instance create few customers
    customer_generator = CustomerGenerator(conn)
    customer_generator.load_initial_data(no_of_customers=5)
    customers = customer_generator.get_all_customers_created_date()

    # Get Account Generator instance and create few accounts
    account_generator = AccountGenerator(conn)
    for customer in customers.items():
        account_generator.create_accounts_for_customer(
            customer_id=customer[0],
            customer_created_at=customer[1],
            valid_customer_ids=list(customers.keys())
        )


if __name__ == '__main__':
    main()
