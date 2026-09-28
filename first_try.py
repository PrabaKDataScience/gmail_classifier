from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
from dotenv import load_dotenv

load_dotenv()

# Reads TYPESAFE_API_KEY and TYPESAFE_BASE_URL=https://api.codiv.ai
client = TypeSafeClient()

response = client.system_one(
    "Hi, my Stripe connection keeps failing with a 403 and we launch tomorrow.",
    {
        "department": Choice(
            instructions="Which team should handle this",
            criteria={
                "billing": "Payment or subscription issues",
                "technical": "Bugs or integration problems",
                "sales": "Pricing or account questions",
            },
        ),
        "frustration": Score(
            instructions="How frustrated the customer appears",
            criteria=["Calm, just stating facts", "Frustrated but civil", "Very angry, strong language"],
        ),
        "is_urgent": Noul(instructions="The message conveys urgency"),
    },
    model="openjev-latest",
)

print(response.choices["department"].choice)   # "technical"
print(response.scores["frustration"].score)     # 1.0
print(response.nouls["is_urgent"].noul)        # 1.0