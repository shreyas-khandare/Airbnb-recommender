# Airbnb Recommender System

## Project Overview
This project is a Machine Learning-based Airbnb recommendation system developed using Python.  
The system predicts and recommends the best Airbnb listings to users based on multiple preferences such as city, room type, bedrooms, bathrooms, accommodates, and budget.

A Random Forest Regression model is trained on an Airbnb dataset containing multiple listing variables.  
The project also includes a simple and interactive Tkinter GUI where users can enter their preferences and receive personalized Airbnb recommendations instantly.

---

## Features
- Predicts Airbnb listing prices using Machine Learning.
- Recommends the best Airbnb listings based on user preferences.
- Filters listings using:
  - City
  - Room Type
  - Bedrooms
  - Bathrooms
  - Accommodates
  - Maximum Budget
- Displays Top 5 recommended Airbnb listings.
- Interactive GUI built using Tkinter.
- Uses a trained Random Forest Regression model.
- Saves and loads the trained model using Joblib.

---

## Technologies Used
- Python
- Pandas
- NumPy
- Scikit-learn
- Tkinter
- Matplotlib
- Seaborn
- Joblib

---

## Machine Learning Workflow
1. Data Collection and CSV Generation  
2. Data Cleaning and Preprocessing  
3. Exploratory Data Analysis (EDA)  
4. Label Encoding for Categorical Variables  
5. Train-Test Split  
6. Random Forest Model Training  
7. Model Evaluation  
8. Model Saving using Joblib  
9. GUI Integration with Trained Model  

---

## Project Structure

```bash
Airbnb_recommender/
│
├── airbnb_listings.csv
├── rf_airbnb_model.pkl
├── label_encoders.pkl
├── gui.py
├── README.md
```

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/shreyas-khandare/Airbnb-recommender.git
```

### 2. Navigate to the Project Folder

```bash
cd Airbnb-recommender
```

### 3. Install Required Libraries

```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

### 4. Run the Application

```bash
python gui.py
```

---

## GUI Functionality
The user can:
- Select City
- Select Room Type
- Enter Bedrooms
- Enter Bathrooms
- Enter Accommodates
- Enter Maximum Budget

The system then predicts and displays the Top 5 recommended Airbnb listings.

---

## Future Improvements
- Add property images and reviews
- Improve recommendation accuracy using advanced ML models
- Deploy as a web application using Flask or Streamlit
- Add user authentication and personalized recommendations
- Use real-world Airbnb datasets

---

## Author
**Shreyas Khandare**  
