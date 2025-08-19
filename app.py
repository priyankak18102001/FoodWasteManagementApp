
import streamlit as st
import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt

# connect to database
conn = sqlite3.connect("food_availability.db")
st.sidebar.markdown("---")
st.sidebar.markdown("👩‍💻 **Developed by Priyanka Kumawat**")


# Check if 'providers' table exists
tables_df = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
existing_tables = tables_df['name'].tolist()

# If database is empty, load CSVs into SQL tables
if 'providers' not in existing_tables:
    st.warning("Database not found. Loading data from CSV files...")

    providers = pd.read_csv("providers_data.csv")
    receivers = pd.read_csv("receivers_data.csv")
    food_listings = pd.read_csv("food_listings_data.csv")
    claims = pd.read_csv("claims_data.csv")

    providers.to_sql("providers", conn, if_exists="replace", index=False)
    receivers.to_sql("receivers", conn, if_exists="replace", index=False)
    food_listings.to_sql("food_listings", conn, if_exists="replace", index=False)
    claims.to_sql("claims", conn, if_exists="replace", index=False)


st.title("Food Waste Management System")
st.markdown("Manage, analyze, and optimize food donations & claims.")

st.sidebar.header("Filter operations")
#Get unique filtered value from DB
city = ['All']+list(pd.read_sql('select distinct City from providers',conn)['City'].dropna())
provider_type = ['All'] + list(pd.read_sql('select distinct Type from providers',conn)['Type'].dropna())
food_type = ['All']+list(pd.read_sql('select distinct Food_Type from food_listings',conn)['Food_Type'].dropna())
meal_type = ['All']+list(pd.read_sql('select distinct Meal_Type from food_listings',conn)['Meal_Type'].dropna())

#slidebar selection boxes
selected_city = st.sidebar.selectbox('City',city)
selected_type = st.sidebar.selectbox('provider type',provider_type)
selected_food_type = st.sidebar.selectbox('food type',food_type)
selected_meal_type = st.sidebar.selectbox('meal type',meal_type)

#filtered food listing
st.subheader("🍱 Filtered Food Listings")

query = """
select f.Food_ID,p.Name as provider_name,p.City ,p.Type as provider_type,f.Food_Type,f.Meal_Type,f.Quantity,f.Expiry_Date From food_listings as f join providers as p on f.Provider_ID = p.Provider_ID where 1=1 """

query_parmas = []

#Apply filters if not "ALL"
if selected_city != "All":
    query += " AND p.City = ?"
    query_parmas.append(selected_city)
if selected_type != "All":
    query += " AND p.Type =?" 
    query_parmas.append(selected_type) 
if selected_food_type != "All":
    query += " AND f.Food_Type =?"
    query_parmas.append(selected_food_type)
if selected_meal_type != "All":
    query += " AND f.Meal_Type = ?"
    query_parmas.append(selected_meal_type)

#Fetch data from DB
filtered_df = pd.read_sql(query,conn,params=query_parmas)

#Display table
if filtered_df.empty:
    st.info("No food listings match the selected filters.")
else:
    st.dataframe(filtered_df)     

#provider and Receiver contact info
st.subheader("Provider Contact Info") 

provider_query = """ select Name, City , Type, Contact from providers where 1=1"""

provider_parmas = []

if selected_city != 'All':
    provider_query+= " AND City = ?" 
    provider_parmas.append(selected_city)
if selected_type!= 'All':
    provider_query+= " AND Type =?"
    provider_parmas.append(selected_type)  

#Get Filtered contact
provider_contact= pd.read_sql(provider_query,conn,params=provider_parmas) 

if provider_contact.empty:
    st.info("No providers match the selected filters.")
else:    
    st.dataframe(provider_contact)
    provider_csv = provider_contact.to_csv(index = False).encode('utf-8')
    st.download_button("📥 Download Provider Contacts", provider_csv, "provider_contacts.csv", "text/csv")


st.subheader("Receiver Contact Info") 

receiver_query = """ select Name, City , Contact from receivers where 1=1"""

receiver_parmas = []

if selected_city != 'All':
    receiver_query+= " AND City = ?" 
    receiver_parmas.append(selected_city)

#Get Filtered contact
receiver_contact= pd.read_sql(receiver_query,conn,params=receiver_parmas) 

if receiver_contact.empty:
    st.info("No receiver match the selected filters.")
else:    
    st.dataframe(receiver_contact)
    receiver_csv = receiver_contact.to_csv(index = False).encode('utf-8')
    st.download_button("📥 Download receiver Contacts", receiver_csv, "receiver_contacts.csv", "text/csv")


# Section for SQL query outputs
st.subheader("📊 Reports & Analysis")

report_option = {
    "1. How many food providers  are there in each city?":"SELECT city, COUNT(*) as provider_count FROM providers GROUP BY city",
     
     "2.How many receiver are there in each city?": "SELECT city,COUNT(*) as receiver_count FROM receivers GROUP BY city",
     "3.Which type of food provider (restaurant, grocery store, etc.) contributes the most food?":"SELECT Provider_Type,COUNT(*) AS provider_count FROM food_listings GROUP BY Provider_Type ORDER BY provider_count DESC LIMIT 1",
     "4.What is the contact information of food providers in a specific city": "SELECT Name , Contact FROM providers WHERE city = 'New Jessica'",
     "5.Which receivers have claimed the most food?": "SELECT Receiver_ID, cOUNT(*) as claim_amount FROM claims GROUP BY Receiver_ID ORDER BY claim_amount DESC LIMIT 1",
     "6..What is the total quantity of food available from all providers?": "SELECT SUM(Quantity) as total_quantity FROM food_listings",
     "7.Which city has the highest number of food listings?": "SELECT City , COUNT(*) as listing_count FROM providers GROUP BY City ORDER BY listing_count DESC limit 1",
     "8.What are the most commonly available food types?": "SELECT Food_Type , COUNT(*) as food_type FROM food_listings GROUP BY Food_Type ORDER BY food_type DESC LIMIT 1",
     "9.How many food claims have been made for each food item?": "SELECT Food_ID, COUNT(*) as claim_count FROM claims GROUP BY Food_ID",
     "10.Which provider has had the highest number of successful food claims?": "SELECT T2.Provider_ID, COUNT(*) as claim_count FROM claims AS T1 INNER JOIN food_listings AS T2 ON T1.Food_ID = T2.Food_ID WHERE T1.Status = 'Completed' GROUP BY T2.Provider_ID ORDER BY claim_count DESC LIMIT 1",
     "11.What percentage of food claims are completed vs. pending vs. canceled?": "SELECT Status, COUNT(*)*100.0/(SELECT COUNT(*) FROM claims) as percentage FROM claims GROUP BY Status",
     "12.What is the average quantity of food claimed per receiver?": "SELECT c.Receiver_ID,r.Name, AVG(f.Quantity) as avg_quantity FROM claims as c JOIN food_listings as f ON c.Food_Id = f.Food_ID JOIN receivers as r ON c.Receiver_ID = r.Receiver_ID Group by c.REceiver_ID",
     "13.Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?": "SELECT Meal_Type , COUNT(*) as claim_most FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY MEal_Type ORDER BY claim_most DESC LIMIT 1",
     "14.What is the total quantity of food donated by each provider?": "SELECT p.Provider_ID, SUM(f.Quantity) as total_quantity FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID GROUP BY p.Provider_ID",
     "15.Number of expired food items": "SELECT COUNT(*) AS experied_items FROM food_listings WHERE Expiry_Date <DATE('now')",
     "16.Cities with most pending food claims": "SELECT p.City , COUNT(*) AS pending_food FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID JOIN providers p ON f.Provider_ID = p.Provider_ID WHERE c.Status = 'Pending' GROUP BY p.City ORDER BY pending_food DESC",
     "17.Find out which food types are most often listed but not claimed." : "SELECT Food_Type ,COUNT(*) as not_claimed FROM food_listings WHERE Food_ID NOT IN(SELECT Food_ID FROM claims) GROUP BY Food_Type ORDER BY not_claimed DESC",
     "18.Where is the most food being wasted (listed but not claimed)?": "SELECT Location, COUNT(*) as wasted_food FROM food_listings WHERE Food_ID NOT IN(SELECT Food_ID FROM claims) GROUP BY Location ORDER BY wasted_food DESC LIMIT 1",
     "19.How many food items expired before being claimed?": "SELECT COUNT(*) AS experied_before_claimed FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID WHERE c.Status = 'Completed' and f.Expiry_Date<Date('now')",
     "20..Which meals are most needed": "SELECT Meal_Type ,COUNT(*) as most_meal FROM food_listings GROUP BY Meal_Type ORDER BY most_meal DESC LIMIT 1",
     "21.Most common meal types by city": "SELECT Location,Meal_Type, COUNT(*) as meal_count FROM food_listings GROUP BY Location,Meal_Type ORDER By meal_count DESC",
     "22.Providers who donated expired food items": "SELECT p.Name, COUNT(*) AS Expired_Food_Coun FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID WHERE DATE(f.Expiry_Date) < DATE('now') GROUP BY p.Name ORDER BY Expired_Food_Count DESC",
     "23.Total number of claims made per provider": "Select p.Provider_ID as provider_name, count(c.Claim_ID	) as total_claims from claims  c join food_listings f on f.Food_ID=c.Food_ID join providers  p on p.Provider_ID=f.Provider_ID group by p.Provider_ID",
     "24.Which food items are most frequently claimed": "select f.Food_Name , count(c.claim_ID) as most_claimed from claims c join food_listings f on f.Food_ID=c.Food_ID group by f.Food_Name order by most_claimed desc limit 1"
}

selected_report = st.selectbox("choose a report to view",list(report_option.keys()))

if selected_report:
    report_df = pd.read_sql(report_option[selected_report],conn)
    st.dataframe(report_df)
    
st.markdown("### A Streamlit app to analyze and predict food wastage trends.")

# ---------------------------
# Display SQL Query Results
# ---------------------------
st.subheader(" SQL Query Results")
query = "SELECT City, COUNT(*) as Providers FROM providers GROUP BY City"
df_results = pd.read_sql(query, conn)
st.dataframe(df_results) 


# Predictions
#----------------------
st.subheader("Food Demand Prediction")
cities = df_results['City'].unique()
selected_city = st.selectbox("select city",cities)

avg_demand = df_results[df_results["City"] == selected_city]["Providers"].mean()
st.write(f"Estimated Future demand in **{selected_city}**:{avg_demand:.0f} units")

# ---------------------------
# Step 4: EDA (Exploratory Data Analysis)
# ---------------------------
# 1. Food donations by Food Type
st.subheader("Explore Data Analysis")
eda_df = pd.read_sql(
    "SELECT Food_Type, COUNT(*) as Count FROM food_listings GROUP BY Food_Type", 
    conn
)
st.markdown("**Distribution of Food Types**")
fig, ax = plt.subplots()
ax.bar(eda_df["Food_Type"],eda_df["Count"],color = "blue")
ax.set_xlabel("Food Type")
ax.set_ylabel("count")
plt.xticks(rotation =45)
st.pyplot(fig)

# 2. Food donations by Meal Type
eda_meal = pd.read_sql(
    "SELECT Meal_Type, COUNT(*) as Count FROM food_listings GROUP BY Meal_Type", 
    conn
)
st.markdown("**Distribution of Meal Types**")
fig, ax = plt.subplots()
ax.bar(eda_meal["Meal_Type"], eda_meal["Count"], color="green")
ax.set_xlabel("Meal Type")
ax.set_ylabel("Count")
plt.xticks(rotation=45)
st.pyplot(fig)

# 3. Providers by City
eda_city = pd.read_sql(
    "SELECT City, COUNT(*) as Count FROM providers GROUP BY City", 
    conn
)
st.markdown("**Providers by City**")
fig, ax = plt.subplots()
ax.bar(eda_city["City"], eda_city["Count"], color="orange")
ax.set_xlabel("City")
ax.set_ylabel("Number of Providers")
plt.xticks(rotation=45)
st.pyplot(fig)

# 4. Food items by Expiry Date
eda_expiry = pd.read_sql(
    "SELECT Expiry_Date, COUNT(*) as Count FROM food_listings GROUP BY Expiry_Date", 
    conn
)
st.markdown("**Food Listings by Expiry Date**")
fig, ax = plt.subplots()
ax.plot(eda_expiry["Expiry_Date"], eda_expiry["Count"], marker="o", color="red")
ax.set_xlabel("Expiry Date")
ax.set_ylabel("Count of Food Items")
plt.xticks(rotation=45)
st.pyplot(fig)

# Implement CURD operation
st.subheader("CURD operation")
table_create,table_read,table_update,table_delete = st.tabs(["Creat","Read","Update","Delete"])

#------Create--------
with table_create:
    st.markdown("### Add New Food Listing")
    with st.form("create Form"):
        provider_ID = st.number_input("Provider ID" ,min_value=1)
        Food_Type = st.text_input("Food Type")
        Meal_Type = st.text_input("Meal Type")
        Quantity = st.number_input("Quantity",min_value=1)
        Expiry_Date = st.date_input("Expiry Date")
        Food_Name = st.text_input("Food Name")
        Food_ID = st.number_input("Food ID" ,min_value=1)
        Submitted = st.form_submit_button("Add Food")

        if Submitted:
            conn.execute(""" 
                         Insert Into food_listings (provider_ID, Food_Type, Meal_Type, Quantity, Expiry_Date,Food_Name,Food_ID)
                         values(? ,? ,?,?,?,?,?)""" ,(provider_ID,Food_Type,Meal_Type,Quantity,Expiry_Date,Food_Name,Food_ID))
            conn.commit()
            st.success("Food Listing added Successfully")

#------ Read------
with table_read:
    st.markdown("###View All Food Listings")
    listings_df = pd.read_sql("Select * from food_listings",conn)
    st.dataframe(listings_df)  

#------Update--------              

with table_update:
    st.markdown("### Update Food Listings")
    listing_df = pd.read_sql("select * from food_listings",conn)
    food_ids = listing_df['Food_ID'].tolist()
    select_food_id = st.selectbox("select Food_ID to update",food_ids)

    selected_row = listing_df[listing_df["Food_ID"] == select_food_id].iloc[0]
    new_quantity = st.number_input("Quantity",min_value=1,value = int(selected_row["Quantity"]))
    new_expiry = st.date_input("Expiry_Date",value = pd.to_datetime(selected_row["Expiry_Date"]))

    if st.button("Update Food"):
        conn.execute(""" update food_listings SET Quantity = ?, Expiry_Date =? where Food_ID =? """,(new_quantity,new_expiry,select_food_id))
        conn.commit()
        st.success("Food Listings Update Successfully")

#-------Delete------
with table_delete:
    st.markdown("### Delete Food Listings")
    listings_df = pd.read_sql("select * from  food_listings",conn)
    delete_ids = listings_df['Food_ID'].tolist()
    delete_food_id = st.selectbox("select Food_ID to delete",delete_ids)

    if st.button("Delete Food"):
        conn.execute("Delete from food_listings where Food_ID = ?",(delete_food_id,))
        conn.commit()
        st.success("Food Listings Delete Successfully")


