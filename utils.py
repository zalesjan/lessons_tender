from datetime import datetime, timedelta, timezone, time
from sqlalchemy import text
import pytz

def store_query(engine, auth0_id, user_input, assistant_output):
    sql = text("""
        INSERT INTO query (datetime, auth0_id, user_input, assistant_output)
        VALUES (:datetime, :auth0_id, :user_input, :assistant_output)
    """)
    with engine.connect() as connection:
        connection.execute(sql, {
            'datetime': datetime.now(timezone.utc),
            'auth0_id': auth0_id,
            'user_input': user_input,
            'assistant_output': assistant_output
        })
        connection.commit()


def count_queries_daily(engine, auth0_id, query_date):
    # Define CET/CEST timezone
    cet = pytz.timezone('Europe/Prague')
    
    # Convert UTC query_date to CET/CEST
    query_date_cet = query_date.astimezone(cet)

    # Combine date with min and max time, then localize to CET/CEST
    start_date_cet = cet.localize(datetime.combine(query_date_cet.date(), time.min))
    end_date_cet = cet.localize(datetime.combine(query_date_cet.date(), time.max))
    
    # Convert to UTC
    start_date_utc = start_date_cet.astimezone(pytz.utc)
    end_date_utc = end_date_cet.astimezone(pytz.utc)
    sql = text("""
        SELECT COUNT(*)
        FROM query
        WHERE auth0_id = :auth0_id
          AND datetime >= :start_date
          AND datetime <= :end_date
    """)
    with engine.connect() as connection:
        result = connection.execute(sql, {
            'auth0_id': auth0_id,
            'start_date': start_date_utc,
            'end_date': end_date_utc
        }).scalar()
    return result


def count_queries_monthly(engine, auth0_id, query_date):
    # Define CET/CEST timezone
    cet = pytz.timezone('Europe/Prague')
    
    # Convert UTC query_date to CET/CEST
    query_date_cet = query_date.astimezone(cet)
    
    # Get the first day of the month
    start_date_cet = cet.localize(datetime(query_date_cet.year, query_date_cet.month, 1))
    
    # Get the first day of the next month
    next_month = start_date_cet + timedelta(days=32)
    start_of_next_month = cet.localize(datetime(next_month.year, next_month.month, 1))
    
    # Convert to UTC
    start_date_utc = start_date_cet.astimezone(pytz.utc)
    end_date_utc = start_of_next_month.astimezone(pytz.utc) - timedelta(microseconds=1)
    
    sql = text("""
        SELECT COUNT(*)
        FROM query
        WHERE auth0_id = :auth0_id
          AND datetime >= :start_date
          AND datetime <= :end_date
    """)
    with engine.connect() as connection:
        result = connection.execute(sql, {
            'auth0_id': auth0_id,
            'start_date': start_date_utc,
            'end_date': end_date_utc
        }).scalar()
    return result


def get_user_role(engine, auth0_id):
    # Create a connection to the database
    with engine.connect() as connection:
        # Create a SQL query to fetch the user's organisation_id and role
        query = text('SELECT organisation_id, role FROM "users" WHERE auth0_id = :auth0_id')
        
        # Execute the query and fetch the result
        result = connection.execute(query, {'auth0_id': auth0_id}).fetchone()
        
        # If the user exists
        if result:
            organisation_id, role = result
            if organisation_id is not None:
                return "ORG"
            elif role is not None:
                return role
            else:
                return None  # Role is None
        else:
            return None  # User does not exist


def get_user_query_limit(engine, auth0_id):
    # Create a connection to the database
    with engine.connect() as connection:
        # Create a SQL query to fetch the user's organisation_id and role
        query = text('SELECT query_limit FROM "users" WHERE auth0_id = :auth0_id')
        
        # Execute the query and fetch the result
        result = connection.execute(query, {
            'auth0_id': auth0_id,
        }).scalar()

        return result


def count_queries_for_user_org(engine, auth0_id):
    query = text("""SELECT COUNT(*) AS total_queries
        FROM Query q
        JOIN "users" u ON q.auth0_id = u.auth0_id
        JOIN Organisation o ON u.organisation_id = o.id
        WHERE u.organisation_id = (
            SELECT organisation_id
            FROM "users"
            WHERE auth0_id = :auth0_id
        )
        AND q.datetime >= o.subscription_start
        """)
    with engine.connect() as connection:
        result = connection.execute(query, {
            'auth0_id': auth0_id,
        }).scalar()

    return result


def get_user_org_query_limit(engine, auth0_id):
    query = text("""
        SELECT o.request_limit
        FROM Organisation o
        JOIN "users" u ON u.organisation_id = o.id
        WHERE u.auth0_id = :auth0_id
        """)
    with engine.connect() as connection:
        result = connection.execute(query, {
            'auth0_id': auth0_id,
        }).scalar()

    return result


def save_lesson(engine, auth0_id, method_sequence, total_duration):
    sql = text("""
        INSERT INTO lessons (created_at, auth0_id, method_sequence, total_duration)
        VALUES (:created_at, :user_id, :method_sequence, :total_duration)
    """)
    with engine.connect() as connection:
        connection.execute(sql, {
            'created_at': datetime.now(timezone.utc),
            'user_id': auth0_id,
            'method_sequence': method_sequence,
            'total_duration': total_duration
        })
        connection.commit()

def fetch_lesson(engine, auth0_id):
    sql = text("""
        INSERT INTO lessons (created_at, auth0_id, method_sequence, total_duration)
        VALUES (:created_at, :user_id, :method_sequence, :assistant_output)
    """)
    with engine.connect() as connection:
        connection.execute(sql, {
            'created_at': datetime.now(timezone.utc),
            'user_id': auth0_id,
            'method_sequence': method_sequence,
            'total_duration': total_duration
        })
        connection.commit()
