import urllib.request
import pandas as pd
import numpy as np
import io

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/autos/imports-85.data"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
content = urllib.request.urlopen(req).read().decode("utf-8")

cols = [
    "symboling", "normalized-losses", "make", "fuel-type", "aspiration",
    "num-of-doors", "body-style", "drive-wheels", "engine-location",
    "wheel-base", "length", "width", "height", "curb-weight",
    "engine-type", "num-of-cylinders", "engine-size", "fuel-system",
    "bore", "stroke", "compression-ratio", "horsepower", "peak-rpm",
    "city-mpg", "highway-mpg", "price"
]
df = pd.read_csv(io.StringIO(content), names=cols, na_values="?")

sample_indices = [
    0, 3, 10, 15, 17, 20, 29, 44, 55, 67, 74, 90, 100, 110, 125, 126, 127, 128, 129, 135, 150, 165, 180, 195, 204
]
sub_df = df.iloc[sample_indices].copy().reset_index(drop=True)

models = []
for i, r in sub_df.iterrows():
    models.append(f"{r['make'].upper()}_{r['body-style']}_Satir{sample_indices[i]}")

final_df = pd.DataFrame({
    "Arac_Modeli": models,
    "Motor_Gucu_HP": sub_df["horsepower"],
    "Sehir_Ici_MPG": sub_df["city-mpg"],
    "Otoyol_MPG": sub_df["highway-mpg"],
    "Motor_Hacmi_cc": sub_df["engine-size"],
    "Fiyat_USD": sub_df["price"],
    "Agirlik_Lbs": sub_df["curb-weight"],
    "Sigorta_Risk_Kaybi": sub_df["normalized-losses"]
})

final_df.to_csv("data/uci_automobile_missing_benchmark.csv", index=False)
print("Successfully saved UCI benchmark dataset to data/uci_automobile_missing_benchmark.csv with", len(final_df), "rows.")

