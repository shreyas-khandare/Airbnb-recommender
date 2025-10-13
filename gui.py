import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import joblib

# ---------- Load saved model and encoders ----------
rf_model = joblib.load("rf_airbnb_model.pkl")
label_encoders = joblib.load("label_encoders.pkl")

# ---------- Load dataset ----------
df = pd.read_csv("airbnb_listings.csv")

# Encode categorical columns in the dataset using saved encoders
categorical_cols = ["city", "neighborhood", "room_type", "property_type", "cancellation_policy"]
for col in categorical_cols:
    df[col] = label_encoders[col].transform(df[col])

# ---------- Recommendation function ----------
def recommend():
    try:
        # Transform user inputs
        city_input = label_encoders["city"].transform([city_var.get()])[0]
        room_type_input = label_encoders["room_type"].transform([room_type_var.get()])[0]
        bedrooms_input = int(bedrooms_var.get())
        bathrooms_input = int(bathrooms_var.get())
        accommodates_input = int(accommodates_var.get())
        max_price_input = float(max_price_var.get())
        
        # Filter dataset based on user input
        filtered = df[
            (df["city"] == city_input) &
            (df["room_type"] == room_type_input) &
            (df["bedrooms"] >= bedrooms_input) &
            (df["bathrooms"] >= bathrooms_input) &
            (df["accommodates"] >= accommodates_input)
        ]
        
        if filtered.empty:
            result_label.config(text="No matching listings found.")
            return
        
        # Predict prices for filtered listings
        X_filtered = filtered.drop(columns=["listing_id", "price"])
        filtered["predicted_price"] = rf_model.predict(X_filtered)
        
        # Sort and show top 5 listings
        top5 = filtered.sort_values("predicted_price").head(5)
        result_text = ""
        for i, row in top5.iterrows():
            result_text += f"Listing {i+1} - Predicted Price: ${row['predicted_price']:.2f}\n"
        
        result_label.config(text=result_text)
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------- Tkinter GUI setup ----------
root = tk.Tk()
root.title("Airbnb Recommender")
root.geometry("500x500")

# Input variables
city_var = tk.StringVar(value="New York")
room_type_var = tk.StringVar(value="Entire home/apt")
bedrooms_var = tk.StringVar(value="1")
bathrooms_var = tk.StringVar(value="1")
accommodates_var = tk.StringVar(value="1")
max_price_var = tk.StringVar(value="500")

# GUI layout
tk.Label(root, text="City:").pack()
ttk.Combobox(root, textvariable=city_var, values=list(label_encoders["city"].classes_)).pack()

tk.Label(root, text="Room Type:").pack()
ttk.Combobox(root, textvariable=room_type_var, values=list(label_encoders["room_type"].classes_)).pack()

tk.Label(root, text="Bedrooms:").pack()
tk.Entry(root, textvariable=bedrooms_var).pack()

tk.Label(root, text="Bathrooms:").pack()
tk.Entry(root, textvariable=bathrooms_var).pack()

tk.Label(root, text="Accommodates:").pack()
tk.Entry(root, textvariable=accommodates_var).pack()

tk.Label(root, text="Maximum Price:").pack()
tk.Entry(root, textvariable=max_price_var).pack()

tk.Button(root, text="Recommend", command=recommend).pack(pady=10)

result_label = tk.Label(root, text="", justify="left")
result_label.pack(pady=20)

root.mainloop()
