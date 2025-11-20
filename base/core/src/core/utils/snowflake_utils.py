from snowflake import SnowflakeGenerator

_snowflake_generator = SnowflakeGenerator(58)

def gen_snowflake_id():
    global _snowflake_generator
    return next(_snowflake_generator)