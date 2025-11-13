# nb_model.py
import pandas as pd
import time
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import json

# ----- Step 1: Load Dataset -----
df = pd.read_excel("TrainingDataset.xlsx")

#print("\n Excel Sheet Data: ")
#print(df)

print("\n Column Names: ")
print(df.columns.tolist())

print("\n Remove the Label Column(result)!")
df_factors=df.drop(columns="reverse")
print(df_factors.columns.tolist())

print("\n Columns Count: ")
print(len(df_factors.columns))

print("\n Dataset Size: ")
print(len(df_factors))

# ----- Step 2: Features & Target -----
X = df.drop(columns=["reverse"])
y = df["reverse"]

# Identify categorical and numeric columns
categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

# ----- Step 3: Preprocessing -----
# Encode categoricals with OneHotEncoder, scale numerics
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
    ]
)

# ----- Step 4: Pipeline with Naive Bayes -----
nb_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", GaussianNB())
])

# ----- Step 5: Train-Test Split -----
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ----- Step 6: Training -----


# Save Results into JSON


# ----- Step 8: Save Model -----
