import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import random


def train_basic_model():
    """
    Train a basic classifier that determines if a property is a good STR candidate.
    For simplicity, we'll create a toy dataset.
    """
    random.seed(42)
    rents = [random.randint(2000, 100000) for _ in range(100000)]
    rents.extend(random.randint(2000, 100000) for _ in range(5000))
    airdna_revenues = [random.randint(1500, 200000) for _ in range(100000)]
    airdna_revenues.extend(0 for _ in range(5000))
    match = [1 if rev >= 2*rent else 0 for rent, rev in zip(rents, airdna_revenues)]
    data = {
        "rent": rents,
        "airdna_revenue": airdna_revenues,
        "match": match  # 1 = Good, 0 = Not Good
    }
    df = pd.DataFrame(data)

    X = df[["rent", "airdna_revenue"]]
    y = df["match"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Save model
    with open('ml/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model trained and saved.")

train_basic_model()