import streamlit as st
import pandas as pd
import duckdb
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Fraud Detection Chatbot - SQL Powered", layout="wide")
st.title("💳 Fraud Detection Chatbot using SQL (DuckDB + Streamlit)")

# Upload dataset
uploaded_file = st.file_uploader("📂 Upload fraudTrain.csv or fraudTest.csv", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, parse_dates=["trans_date_trans_time"])
    st.success("✅ Dataset uploaded successfully!")
    st.write("📄 Preview:", df.head())

    st.subheader("📊 Dataset Summary")
    st.write(df.describe(include='all'))

    # Register as a DuckDB table for SQL queries
    con = duckdb.connect()
    con.register("fraud_data", df)

    # Visualization Selector
    st.subheader("📈 Fraud Analysis Visualizations")
    viz_option = st.selectbox("Choose a visualization", [
        "Fraud Count by State",
        "Total Amount Lost to Fraud",
        "Category-wise Fraud Count",
        "Top Cities with Fraud",
        "Fraud Count by Age Group",
        "Fraud vs Legit by Amount"
    ])

    if viz_option == "Fraud Count by State":
        query = "SELECT state, COUNT(*) AS frauds FROM fraud_data WHERE is_fraud = 1 GROUP BY state ORDER BY frauds DESC"
        fraud_by_state = con.execute(query).fetchdf()
        st.dataframe(fraud_by_state)
        fig, ax = plt.subplots()
        sns.barplot(data=fraud_by_state.head(10), x="frauds", y="state", palette="viridis", ax=ax)
        ax.set_title("Top 10 States by Fraud Count")
        st.pyplot(fig)

    elif viz_option == "Total Amount Lost to Fraud":
        query = "SELECT SUM(amt) AS total_fraud_amount FROM fraud_data WHERE is_fraud = 1"
        result = con.execute(query).fetchone()
        st.success(f"💸 Total Amount Lost to Fraud: ${result[0]:,.2f}")

    elif viz_option == "Category-wise Fraud Count":
        query = "SELECT category, COUNT(*) AS count FROM fraud_data WHERE is_fraud = 1 GROUP BY category ORDER BY count DESC"
        cat_fraud = con.execute(query).fetchdf()
        st.dataframe(cat_fraud)
        fig2, ax2 = plt.subplots()
        sns.barplot(data=cat_fraud.head(10), x="count", y="category", palette="coolwarm", ax=ax2)
        ax2.set_title("Top Categories with Fraudulent Transactions")
        st.pyplot(fig2)

    elif viz_option == "Top Cities with Fraud":
        query = """
            SELECT city, COUNT(*) AS frauds
            FROM fraud_data
            WHERE is_fraud = 1
            GROUP BY city
            ORDER BY frauds DESC
            LIMIT 10
        """
        city_df = con.execute(query).fetchdf()
        fig, ax = plt.subplots()
        sns.barplot(data=city_df, y="city", x="frauds", palette="flare", ax=ax)
        ax.set_title("Top 10 Cities by Fraud Count")
        st.pyplot(fig)

    elif viz_option == "Fraud Count by Age Group":
        query = """
            SELECT 
                CASE 
                    WHEN age < 25 THEN '<25'
                    WHEN age BETWEEN 25 AND 40 THEN '25-40'
                    WHEN age BETWEEN 41 AND 60 THEN '41-60'
                    ELSE '60+' 
                END AS age_group,
                COUNT(*) AS frauds
            FROM fraud_data
            WHERE is_fraud = 1
            GROUP BY age_group
            ORDER BY frauds DESC
        """
        age_df = con.execute(query).fetchdf()
        fig, ax = plt.subplots()
        sns.barplot(data=age_df, x="age_group", y="frauds", palette="muted", ax=ax)
        ax.set_title("Fraud Count by Customer Age Group")
        st.pyplot(fig)

    elif viz_option == "Fraud vs Legit by Amount":
        query = "SELECT is_fraud, amt FROM fraud_data"
        amt_df = con.execute(query).fetchdf()
        fig, ax = plt.subplots()
        sns.histplot(data=amt_df, x="amt", hue="is_fraud", bins=50, kde=True, ax=ax)
        ax.set_xlim(0, 1000)
        ax.set_title("Transaction Amounts: Fraud vs Legit")
        st.pyplot(fig)

    # SQL Chat Input
    st.subheader("💬 Ask SQL-like Questions")
    user_query = st.text_area("Enter your SQL query (fraud_data is your table):")
    if st.button("Run Query"):
        try:
            result = con.execute(user_query).fetchdf()
            st.dataframe(result)
        except Exception as e:
            st.error(f"❌ Query failed: {e}")
else:
    st.info("Upload `fraudTrain.csv` or `fraudTest.csv` from [this Kaggle dataset](https://www.kaggle.com/datasets/kartik2112/fraud-detection) to begin.")
