# FoodWasteManagementApp
#  Food Waste Management System

A Streamlit-based web application to manage, analyze, and optimize food donations and claims.  
This system connects food providers with receivers, reduces wastage, and promotes efficient distribution.

---

##  Features
- Display results of **23 SQL queries** with filtering options
- Show **provider contact information** for direct coordination
- Predict **food demand** based on city selection
- Perform **EDA** (Exploratory Data Analysis) with visualizations
- Implement **CRUD operations** for updating, adding, and removing records

---

##  Dataset
The app uses the following datasets:
- `providers_data.csv`
- `receivers_data.csv`
- `food_listings_data.csv`
- `claims_data.csv`

These datasets are stored in a SQLite database (`food_availability.db`).  
If the database is missing, the app **automatically creates it from the CSV files**.

---

## 🛠 Technology Stack
- Python 3.x
- Pandas
- SQLite
- Streamlit
- Matplotlib

---

## 📦 Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/FoodWasteApp.git
cd FoodWasteApp
