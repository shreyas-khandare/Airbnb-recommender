import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import joblib
from tkinter import font
import threading
import time

# ---------- Load saved model and encoders ----------
print("Loading model and data...")
rf_model = joblib.load("rf_airbnb_model.pkl")
label_encoders = joblib.load("label_encoders.pkl")

# ---------- Load dataset ----------
df = pd.read_csv("airbnb_listings.csv")

# Encode categorical columns in the dataset using saved encoders
categorical_cols = ["city", "neighborhood", "room_type", "property_type", "cancellation_policy"]
for col in categorical_cols:
    df[col] = label_encoders[col].transform(df[col])

# ---------- Global variables for UI ----------
results_data = []
current_sort = "price_asc"

# ---------- Validation functions ----------
def validate_numeric_input(value, field_name, min_val=0, max_val=20):
    """Validate numeric input with real-time feedback"""
    try:
        num = int(value) if value else 0
        if min_val <= num <= max_val:
            return True, ""
        else:
            return False, f"{field_name} must be between {min_val} and {max_val}"
    except ValueError:
        return False, f"{field_name} must be a valid number"

def validate_price_input(value):
    """Validate price input"""
    try:
        price = float(value) if value else 0
        if 0 <= price <= 10000:
            return True, ""
        else:
            return False, "Price must be between $0 and $10,000"
    except ValueError:
        return False, "Price must be a valid number"

def on_input_change(*args):
    """Real-time validation and feedback"""
    # Validate bedrooms
    bedrooms_valid, bedrooms_msg = validate_numeric_input(bedrooms_var.get(), "Bedrooms", 0, 10)
    bedrooms_status.config(text=bedrooms_msg, fg="red" if bedrooms_msg else "green")
    
    # Validate bathrooms
    bathrooms_valid, bathrooms_msg = validate_numeric_input(bathrooms_var.get(), "Bathrooms", 0, 10)
    bathrooms_status.config(text=bathrooms_msg, fg="red" if bathrooms_msg else "green")
    
    # Validate accommodates
    accommodates_valid, accommodates_msg = validate_numeric_input(accommodates_var.get(), "Accommodates", 1, 20)
    accommodates_status.config(text=accommodates_msg, fg="red" if accommodates_msg else "green")
    
    # Validate price
    price_valid, price_msg = validate_price_input(max_price_var.get())
    price_status.config(text=price_msg, fg="red" if price_msg else "green")
    
    # Enable/disable recommend button
    all_valid = bedrooms_valid and bathrooms_valid and accommodates_valid and price_valid
    recommend_btn.config(state="normal" if all_valid else "disabled")

# ---------- Enhanced recommendation function ----------
def recommend():
    """Enhanced recommendation with progress indication"""
    def run_recommendation():
        try:
            # Show loading state
            recommend_btn.config(text="Searching...", state="disabled")
            progress_bar.start()
            status_label.config(text="Finding your perfect Airbnb...", fg="blue")
            
            # Small delay for visual feedback
            time.sleep(0.5)
            
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
                status_label.config(text="No matching listings found. Try adjusting your criteria.", fg="orange")
                clear_results()
                return
            
            # Predict prices for filtered listings
            X_filtered = filtered.drop(columns=["listing_id", "price"])
            filtered["predicted_price"] = rf_model.predict(X_filtered)
            
            # Apply price filter
            filtered = filtered[filtered["predicted_price"] <= max_price_input]
            
            if filtered.empty:
                status_label.config(text="No listings within your price range. Try increasing your budget.", fg="orange")
                clear_results()
                return
            
            # Sort based on current sort option
            if current_sort == "price_asc":
                filtered = filtered.sort_values("predicted_price")
            elif current_sort == "price_desc":
                filtered = filtered.sort_values("predicted_price", ascending=False)
            elif current_sort == "rating_desc":
                filtered = filtered.sort_values("review_score", ascending=False)
            
            # Store results globally
            global results_data
            results_data = filtered.head(10).copy()
            
            # Display results
            display_results()
            status_label.config(text=f"Found {len(results_data)} great options for you!", fg="green")
            
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", str(e))
        finally:
            # Reset UI state
            recommend_btn.config(text="Find My Perfect Stay", state="normal")
            progress_bar.stop()
    
    # Run in separate thread to prevent UI freezing
    threading.Thread(target=run_recommendation, daemon=True).start()

def display_results():
    """Display results in an enhanced format"""
    clear_results()
    
    if results_data.empty:
        return
    
    # Create results frame
    results_frame = ttk.Frame(results_container)
    results_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    for i, (idx, row) in enumerate(results_data.iterrows()):
        # Create card for each listing
        card = tk.Frame(results_frame, bg="#f8f9fa", relief="raised", bd=1)
        card.pack(fill="x", pady=5, padx=5)
        
        # Card header
        header_frame = tk.Frame(card, bg="#e3f2fd")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Listing number and price
        tk.Label(header_frame, text=f"Option {i+1}", 
                font=("Arial", 12, "bold"), bg="#e3f2fd").pack(side="left")
        tk.Label(header_frame, text=f"${row['predicted_price']:.2f}/night", 
                font=("Arial", 14, "bold"), fg="#1976d2", bg="#e3f2fd").pack(side="right")
        
        # Details frame
        details_frame = tk.Frame(card, bg="#f8f9fa")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Create two columns for details
        left_col = tk.Frame(details_frame, bg="#f8f9fa")
        left_col.pack(side="left", fill="x", expand=True)
        
        right_col = tk.Frame(details_frame, bg="#f8f9fa")
        right_col.pack(side="right", fill="x", expand=True)
        
        # Left column details
        tk.Label(left_col, text=f"Bedrooms: {int(row['bedrooms'])}", 
                font=("Arial", 10), bg="#f8f9fa").pack(anchor="w")
        tk.Label(left_col, text=f"Bathrooms: {int(row['bathrooms'])}", 
                font=("Arial", 10), bg="#f8f9fa").pack(anchor="w")
        tk.Label(left_col, text=f"Sleeps: {int(row['accommodates'])}", 
                font=("Arial", 10), bg="#f8f9fa").pack(anchor="w")
        
        # Right column details
        tk.Label(right_col, text=f"Rating: {row['review_score']:.1f}/5", 
                font=("Arial", 10), bg="#f8f9fa").pack(anchor="w")
        tk.Label(right_col, text=f"Reviews: {int(row['number_of_reviews'])}", 
                font=("Arial", 10), bg="#f8f9fa").pack(anchor="w")
        tk.Label(right_col, text=f"Amenities: {int(row['amenities_count'])}", 
                font=("Arial", 10), bg="#f8f9fa").pack(anchor="w")

def clear_results():
    """Clear the results display"""
    for widget in results_container.winfo_children():
        widget.destroy()

def sort_results(sort_type):
    """Sort and redisplay results"""
    global current_sort
    current_sort = sort_type
    if not results_data.empty:
        display_results()

def reset_form():
    """Reset all form inputs to default values"""
    city_var.set("Seattle")
    room_type_var.set("Entire home/apt")
    bedrooms_var.set("1")
    bathrooms_var.set("1")
    accommodates_var.set("2")
    max_price_var.set("500")
    clear_results()
    status_label.config(text="Ready to find your perfect stay!", fg="blue")

# ---------- Enhanced Tkinter GUI setup ----------
root = tk.Tk()
root.title("Airbnb Smart Recommender")
root.geometry("1000x700")
root.configure(bg="#f5f5f5")

# Configure style
style = ttk.Style()
style.theme_use('clam')

# Configure custom styles
style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f5f5f5')
style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f5f5f5')
style.configure('Custom.TButton', font=('Arial', 11, 'bold'), padding=10)
style.configure('Custom.TFrame', background='#f5f5f5')

# Input variables with trace for real-time validation
city_var = tk.StringVar(value="Seattle")
room_type_var = tk.StringVar(value="Entire home/apt")
bedrooms_var = tk.StringVar(value="1")
bathrooms_var = tk.StringVar(value="1")
accommodates_var = tk.StringVar(value="2")
max_price_var = tk.StringVar(value="500")

# Add trace callbacks for real-time validation
bedrooms_var.trace('w', on_input_change)
bathrooms_var.trace('w', on_input_change)
accommodates_var.trace('w', on_input_change)
max_price_var.trace('w', on_input_change)

# ---------- Main Container ----------
main_container = ttk.Frame(root, style='Custom.TFrame')
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# ---------- Header Section ----------
header_frame = ttk.Frame(main_container, style='Custom.TFrame')
header_frame.pack(fill="x", pady=(0, 20))

title_label = ttk.Label(header_frame, text="Airbnb Smart Recommender", style='Title.TLabel')
title_label.pack()

subtitle_label = ttk.Label(header_frame, text="Find your perfect stay with AI-powered recommendations", 
                          font=('Arial', 10), background='#f5f5f5', foreground='#666')
subtitle_label.pack()

# ---------- Input Section ----------
input_frame = ttk.LabelFrame(main_container, text="Your Preferences", style='Custom.TFrame', padding=20)
input_frame.pack(fill="x", pady=(0, 20))

# Create input grid
input_grid = ttk.Frame(input_frame, style='Custom.TFrame')
input_grid.pack(fill="x")

# Row 1: City and Room Type
row1 = ttk.Frame(input_grid, style='Custom.TFrame')
row1.pack(fill="x", pady=5)

ttk.Label(row1, text="City:", style='Header.TLabel').pack(side="left", padx=(0, 10))
city_combo = ttk.Combobox(row1, textvariable=city_var, values=list(label_encoders["city"].classes_),
                         state="readonly", width=20)
city_combo.pack(side="left", padx=(0, 30))

ttk.Label(row1, text="Room Type:", style='Header.TLabel').pack(side="left", padx=(0, 10))
room_type_combo = ttk.Combobox(row1, textvariable=room_type_var, values=list(label_encoders["room_type"].classes_),
                              state="readonly", width=20)
room_type_combo.pack(side="left")

# Row 2: Bedrooms and Bathrooms
row2 = ttk.Frame(input_grid, style='Custom.TFrame')
row2.pack(fill="x", pady=5)

ttk.Label(row2, text="Bedrooms:", style='Header.TLabel').pack(side="left", padx=(0, 10))
bedrooms_entry = ttk.Entry(row2, textvariable=bedrooms_var, width=10)
bedrooms_entry.pack(side="left", padx=(0, 30))
bedrooms_status = ttk.Label(row2, text="", font=('Arial', 8), background='#f5f5f5')
bedrooms_status.pack(side="left", padx=(5, 0))

ttk.Label(row2, text="Bathrooms:", style='Header.TLabel').pack(side="left", padx=(0, 10))
bathrooms_entry = ttk.Entry(row2, textvariable=bathrooms_var, width=10)
bathrooms_entry.pack(side="left", padx=(0, 30))
bathrooms_status = ttk.Label(row2, text="", font=('Arial', 8), background='#f5f5f5')
bathrooms_status.pack(side="left", padx=(5, 0))

# Row 3: Accommodates and Max Price
row3 = ttk.Frame(input_grid, style='Custom.TFrame')
row3.pack(fill="x", pady=5)

ttk.Label(row3, text="Accommodates:", style='Header.TLabel').pack(side="left", padx=(0, 10))
accommodates_entry = ttk.Entry(row3, textvariable=accommodates_var, width=10)
accommodates_entry.pack(side="left", padx=(0, 30))
accommodates_status = ttk.Label(row3, text="", font=('Arial', 8), background='#f5f5f5')
accommodates_status.pack(side="left", padx=(5, 0))

ttk.Label(row3, text="Max Price ($):", style='Header.TLabel').pack(side="left", padx=(0, 10))
price_entry = ttk.Entry(row3, textvariable=max_price_var, width=10)
price_entry.pack(side="left", padx=(0, 30))
price_status = ttk.Label(row3, text="", font=('Arial', 8), background='#f5f5f5')
price_status.pack(side="left", padx=(5, 0))

# ---------- Action Buttons ----------
button_frame = ttk.Frame(main_container, style='Custom.TFrame')
button_frame.pack(fill="x", pady=(0, 20))

recommend_btn = ttk.Button(button_frame, text="Find My Perfect Stay", 
                          command=recommend, style='Custom.TButton')
recommend_btn.pack(side="left", padx=(0, 10))

reset_btn = ttk.Button(button_frame, text="Reset", command=reset_form, style='Custom.TButton')
reset_btn.pack(side="left", padx=(0, 10))

# Progress bar
progress_bar = ttk.Progressbar(button_frame, mode='indeterminate')
progress_bar.pack(side="right", padx=(10, 0))

# ---------- Status Section ----------
status_label = ttk.Label(main_container, text="Ready to find your perfect stay!", 
                        font=('Arial', 10), background='#f5f5f5', foreground='blue')
status_label.pack(pady=(0, 10))

# ---------- Results Section ----------
results_section = ttk.LabelFrame(main_container, text="Your Recommendations", style='Custom.TFrame', padding=10)
results_section.pack(fill="both", expand=True)

# Sort controls
sort_frame = ttk.Frame(results_section, style='Custom.TFrame')
sort_frame.pack(fill="x", pady=(0, 10))

ttk.Label(sort_frame, text="Sort by:", style='Header.TLabel').pack(side="left", padx=(0, 10))
ttk.Button(sort_frame, text="Price (Low to High)", 
          command=lambda: sort_results("price_asc")).pack(side="left", padx=(0, 5))
ttk.Button(sort_frame, text="Price (High to Low)", 
          command=lambda: sort_results("price_desc")).pack(side="left", padx=(0, 5))
ttk.Button(sort_frame, text="Rating (High to Low)", 
          command=lambda: sort_results("rating_desc")).pack(side="left", padx=(0, 5))

# Results container with scrollbar
results_container_frame = ttk.Frame(results_section, style='Custom.TFrame')
results_container_frame.pack(fill="both", expand=True)

# Create canvas and scrollbar for results
canvas = tk.Canvas(results_container_frame, bg="#f5f5f5")
scrollbar = ttk.Scrollbar(results_container_frame, orient="vertical", command=canvas.yview)
results_container = ttk.Frame(canvas, style='Custom.TFrame')

results_container.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=results_container, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Bind mousewheel to canvas
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Initialize validation
on_input_change()

# ---------- Start the application ----------
print("Airbnb Recommender GUI loaded successfully!")
root.mainloop()

