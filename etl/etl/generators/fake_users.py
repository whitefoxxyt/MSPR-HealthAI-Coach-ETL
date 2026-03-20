import hashlib

from faker import Faker

fake = Faker("fr_FR")
Faker.seed(42)

OBJECTIVES = [
    "Perte de poids",
    "Prise de masse",
    "Maintien",
    "Endurance",
    "Renforcement musculaire",
    "Flexibilité",
]

GENDERS = ["Homme", "Femme"]


def generate(count: int = 500) -> list[dict]:
    """Génère n utilisateurs fictifs avec un seed fixe pour la reproductibilité."""
    users: list[dict] = []
    for _ in range(count):
        users.append(
            {
                "email": fake.unique.email(),
                "username": fake.user_name(),
                "password_hash": hashlib.sha256(fake.password().encode()).hexdigest(),
                "role": "USER",
                "is_premium": fake.boolean(chance_of_getting_true=20),
                "age": fake.random_int(min=18, max=75),
                "gender": fake.random_element(GENDERS),
                "weight_kg": round(fake.pyfloat(min_value=45, max_value=120), 2),
                "height_cm": round(fake.pyfloat(min_value=150, max_value=200), 1),
                "objective": fake.random_element(OBJECTIVES),
            }
        )
    return users
