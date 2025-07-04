import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit page config
st.set_page_config(page_title="Hospital Appointment EDA", layout="wide")
st.title("📊 Nigeria Hospital Appointments - Exploratory Data Analysis by Francis Bright")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_excel("Nigeria_Hospital_Appointments.xlsx", sheet_name="Sheet1")
    df['AppointmentDate'] = pd.to_datetime(df['AppointmentDate'])
    df['BookingDate'] = pd.to_datetime(df['BookingDate'])
    df['WaitingDays'] = (df['AppointmentDate'] - df['BookingDate']).dt.days
    df['Weekday'] = df['AppointmentDate'].dt.day_name()
    df['Month'] = df['AppointmentDate'].dt.month_name()
    df['NoShow'] = df['NoShow'].astype(int)

    # Add Age Group
    def categorize_age(age):
        if age <= 17:
            return "Children"
        elif 18 <= age <= 30:
            return "Young Adults"
        else:
            return "Adults"
    df['AgeGroup'] = df['Age'].apply(categorize_age)

    return df

df = load_data()

# Sidebar filters
st.sidebar.header(" Filters")
selected_location = st.sidebar.multiselect("Select Location", options=df['Location'].unique(), default=df['Location'].unique())
selected_department = st.sidebar.multiselect("Select Department", options=df['Department'].unique(), default=df['Department'].unique())

filtered_df = df[(df['Location'].isin(selected_location)) & (df['Department'].isin(selected_department))]

# Create Age Group column
df['AgeGroup'] = pd.cut(
    df['Age'],
    bins=[0, 17, 30, df['Age'].max()],
    labels=['Children', 'Young Adults', 'Adults'],
    right=True
)

# Display age group explanation on Streamlit
st.markdown("###  Age Group Categorization")
st.markdown("""
We have grouped patients based on their age to enable clearer demographic analysis and healthcare insight.

**Age Groups:**
- **Children (0–17 years):** Includes minors, often attending pediatric or general clinics.
- **Young Adults (18–30 years):** Covers students and early-career individuals.
- **Adults (31 years and above):** Represents middle-aged and older patients, more likely to present with chronic conditions.

This categorization helps in identifying health trends, planning resource allocation, and understanding no-show behaviors across age brackets.
""")

# Section 1: Overview
st.header("1. Dataset Overview")
st.dataframe(filtered_df.head(20))

average_age = filtered_df['Age'].mean()


col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Appointments", len(filtered_df))
col2.metric("No-Show Rate (%)", f"{filtered_df['NoShow'].mean()*100:.2f}")
col3.metric("Avg Waiting Days", f"{filtered_df['WaitingDays'].mean():.1f}")
col4.metric("Departments", filtered_df['Department'].nunique())
col5.metric("Average Age", f"{filtered_df['Age'].mean():.1f} years")


# Section 2: Gender Distribution
st.header("2. Demographic Insights")

col1, col2 = st.columns(2)
with col1:
    gender_counts = filtered_df['Gender'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title("Gender Distribution")
    st.pyplot(fig1)



# Age group bar chart
fig3, ax3 = plt.subplots()
age_group_counts = filtered_df['AgeGroup'].value_counts()
sns.barplot(x=age_group_counts.index, y=age_group_counts.values, palette="Set2", ax=ax3)
ax3.set_title("Age Group Distribution")
ax3.set_ylabel("Number of Appointments")
st.pyplot(fig3)

# Section 3: No-Show Analysis
st.header("3. No-Show Analysis")

col1, col2 = st.columns(2)
with col1:
    fig4, ax4 = plt.subplots()
    sns.barplot(data=filtered_df, x='Gender', y='NoShow', ax=ax4)
    ax4.set_title("No-Show Rate by Gender")
    st.pyplot(fig4)

with col2:
    fig5, ax5 = plt.subplots()
    sns.barplot(data=filtered_df, x='Department', y='NoShow', ax=ax5)
    ax5.set_title("No-Show Rate by Department")
    ax5.tick_params(axis='x', rotation=45)
    st.pyplot(fig5)

col3, col4 = st.columns(2)
with col3:
    fig6, ax6 = plt.subplots()
    sns.barplot(data=filtered_df, x='HealthInsurance', y='NoShow', ax=ax6)
    ax6.set_title("Impact of Health Insurance on No-Show")
    st.pyplot(fig6)

with col4:
    fig7, ax7 = plt.subplots()
    sns.barplot(data=filtered_df, x='SMSReminderSent', y='NoShow', ax=ax7)
    ax7.set_title("Impact of SMS Reminders on No-Show")
    st.pyplot(fig7)

# Section 4: Waiting Time and Temporal Trends

with col2:
    fig9, ax9 = plt.subplots()
    sns.barplot(data=filtered_df, x='Weekday', y='NoShow', order=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], ax=ax9)
    ax9.set_title("No-Show by Day of the Week")
    ax9.tick_params(axis='x', rotation=45)
    st.pyplot(fig9)

fig10, ax10 = plt.subplots(figsize=(10, 4))
monthly_data = filtered_df.groupby('Month')['NoShow'].mean().sort_index()
monthly_data.plot(kind='bar', ax=ax10, color='coral')
ax10.set_title("Average No-Show Rate by Month")
st.pyplot(fig10)

# Section 5: Location Analysis
st.header("5. Geographic Trends")

fig11, ax11 = plt.subplots()
sns.barplot(data=filtered_df, x='Location', y='NoShow', ax=ax11)
ax11.set_title("No-Show Rate by Location")
st.pyplot(fig11)

age_disease_table = filtered_df.groupby(['AgeGroup', 'Department']).size().unstack().fillna(0)
st.dataframe(age_disease_table)

fig, ax = plt.subplots(figsize=(10, 6))
age_disease_table.plot(kind='bar', stacked=True, ax=ax)
ax.set_title("Disease Distribution Across Age Groups")
ax.set_xlabel("Age Group")
ax.set_ylabel("Number of Appointments")
st.pyplot(fig)

# Gender distribution by department
gender_by_dept = filtered_df.groupby(['Department', 'Gender']).size().unstack().fillna(0)

# Determine departments with more male and more female patients
most_male_dept = gender_by_dept['Male'].idxmax()
most_female_dept = gender_by_dept['Female'].idxmax()

# Display the results
st.markdown("###  Departmental Gender Distribution")
st.markdown(f"""
-  **Department with the most Male patients:** `{most_male_dept}` ({int(gender_by_dept.loc[most_male_dept, 'Male'])} males)
-  **Department with the most Female patients:** `{most_female_dept}` ({int(gender_by_dept.loc[most_female_dept, 'Female'])} females)
""")

# Gender distribution by department
gender_by_dept = filtered_df.groupby(['Department', 'Gender']).size().unstack().fillna(0)

# Horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 6))
gender_by_dept.plot(kind='barh', ax=ax, color=['skyblue', 'lightcoral'])
ax.set_title("Gender Distribution by Department")
ax.set_xlabel("Number of Patients")
ax.set_ylabel("Department")
ax.legend(title="Gender")
st.pyplot(fig)

# Group age by Gender and Department
age_grouped = filtered_df.groupby(['Gender', 'Department'])['Age'].mean().reset_index()

# Round the average age for better display
age_grouped['Age'] = age_grouped['Age'].round(1)

# Display as a bar chart
st.header(" Average Age by Gender and Department")
with st.expander("See Data Table"):
    st.dataframe(age_grouped)
fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(data=age_grouped, x='Department', y='Age', hue='Gender', ax=ax)
ax.set_title("Average Age by Gender and Department")
ax.set_ylabel("Average Age (years)")
ax.set_xlabel("Department")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)









# Footer
st.markdown("---")
st.markdown(" **Insights:**")
st.markdown("""
            
General Appointment Overview
            
•	A large number of appointments were recorded across various departments and locations in Nigeria.
            
•	The no-show rate is a significant metric and varies across demographics and departments.
            
•	Average waiting time between booking and appointment is a critical factor influencing patient turnout.
________________________________________
Demographic Insights
            
•	Gender Distribution shows a fairly balanced mix of male and female patients, though slightly more females attend hospital appointments.
            
•	Age Group Distribution:
            
•	Children (0-17) represent a smaller portion of appointments.
            
•	Young Adults (18-30) form a major part of the patient population.
            
•	Adults (31+) also make up a significant proportion, often related to chronic health issues.
            
•	The most common age group for appointments varies by disease — younger patients are more represented in general clinics and pediatrics, while older adults dominate cardiology and internal medicine.
________________________________________
Geographical Insights
            
•	Ibadan recorded the highest total number of appointments, while Lagos shows better attendance and lower no-show rates.
            
•	Gender distribution by location is relatively balanced, but slight skews exist (e.g., more male patients in some regions like Kano).
________________________________________
Departmental Trends
            
•	Departments such as General Medicine and Pediatrics received more appointments.
            
•	Cardiology and Endocrinology saw higher no-show rates, possibly due to longer waiting periods or chronic conditions.
            
•	Male patients are more frequent in departments like Surgery and Orthopedics, while females dominate Obstetrics/Gynecology and General OPD.
________________________________________
No-Show Analysis
            
•	Patients without SMS reminders were more likely to miss their appointments.
            
•	Patients with Health Insurance were more likely to show up.
            
•	Wednesdays and Thursdays had slightly higher no-show patterns.
            
•	Shorter waiting periods lead to higher attendance rates.
________________________________________
 Actionable Recommendations
            
•	Enhance SMS Reminder System to improve appointment turnout.
            
•	Promote Health Insurance as insured patients are more likely to keep appointments.
            
•	Reduce Waiting Times streamline booking systems to ensure closer appointment dates.
            
•	Target No-Show Hotspots like certain departments and weekdays for better scheduling.

            
""")
st.success("Project by: Francis Bright")
