# TODO: implement function connecting to the DB and returning a cursor object
# TODO: implement functions for upserting data from each data frame,
#       the functions should take a data frame ans a DB cursor as arguments

# 0. Create a cursor and open a transaction (check if manual opening is needed).
# 1. Upsert data into the inner-level tables (countries, etc.), saving a map tmdb_id -> db_id.
# 2. Upsert data into all the other tables from inner to outer levels, saving id maps as well.
# 3. Upsert data into the connecting tables.
# 4. Commit the transaction.
# 5. On any error rollback the transaction.
