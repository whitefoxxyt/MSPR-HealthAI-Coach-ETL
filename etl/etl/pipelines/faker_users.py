from loaders.postgres_loader import TableConfig

TABLE = TableConfig(
    table="users",
    columns=[
        "email",
        "username",
        "password_hash",
        "role",
        "is_premium",
        "age",
        "gender",
        "weight_kg",
        "height_cm",
        "objective",
    ],
    conflict_clause="ON CONFLICT (email) DO NOTHING",
)

COUNT = 500
