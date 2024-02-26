import streamlit as st
from funcs_old import *

def selectSub(year):
    global subs
    if year=="2nd Year":
        subs = ["COA Lab", "Webd Lab", "DSA Lab"]
        subs = st.multiselect("Chose Subjects: ", subs)
    elif year == "3rd Year":
        subs = ["DBMS Lab KCS551", "Compiler Design Lab KCS552", "DAA Lab KCS553"]
        subs = st.multiselect("Chose Subjects: ", subs)
    elif year == "4th Year":
        subs = ["Artificial Intelligence Lab KCS751A"]
        subs = st.multiselect("Chose Subjects: ", subs)

if __name__=="__main__":
    st.write("# Practicle Scheduler")
    # with st.sidebar:
    session = st.text_input("What is session year")
    session = session[:-3]
    year = st.radio("Select Year", ["2nd Year", "3rd Year", "4th Year"])
    fclt = st.radio("Select Faculty Type", ["AKTU Appointed", "Personal Appointed"])
    day1 = st.text_input("Enter Day1 for practical")
    day2 = st.text_input("Enter Day2 for practical")
    selectSub(year)
    uploaded_file = st.file_uploader('Upload a file:', type=['xlsx', "csv"])
    addData = st.button("Add File")
    if uploaded_file and addData:
        if fclt == "AKTU Appointed":
            ak, Or=1, None
        elif fclt == "Personal Appointed":
            ak, Or = None, 1
        df2 , batchs = preprocessData(uploaded_file, session, aktu=ak, ours=Or)
        df1 = makeSchedule(subs, day1, day2, batchs)
        with pd.ExcelWriter(r"E:\Users\HP\Desktop\aalix clg\projects\IMSECCSE\practical schedular\data\outputt.xlsx") as writer:
            df1.to_excel(writer, sheet_name="Schdule", index_label=["Date", "Time"])
            df2.to_excel(writer, sheet_name="Groups", index_label="Group")