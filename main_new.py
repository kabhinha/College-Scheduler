import streamlit as st
from funcs_new import *


if __name__=="__main__":
    with open("./batch.txt", "r+") as f:
        batch_no, ic = f.read().split()
        batch_no = int(batch_no[0])
        ic = int(ic)
    st.write("# Practicle Scheduler")
    session = st.text_input("What is session year")
    session = session[:-3]
    with open("./session.txt", "w") as f:
        f.write(session)
    day1 = st.text_input("Enter Date of practical")
    sub1 = st.text_input("Enter Subject of practical")
    lab1 = st.text_input("Enter Lab for practical")
    fclt1 = st.radio("Select Faculty1 Type", ["AKTU Appointed", "Personal Appointed"])
    uploaded_file = st.file_uploader('Upload a file:', type=['xlsx', "csv"])
    addData = st.button("Add File")
    resetDB = st.button("Reset Data")
    if resetDB:
        os.remove("./data/output.xlsx")
        for i in next(os.walk("./data/Alloted/"))[2]:
            os.remove(f"./data/Alloted/{i}")
    if uploaded_file and addData:
        print("Work")
        df, len_df = preprocessData(uploaded_file)
        if day1:
            aktu=1
            if fclt1=="Personal Appointed":
                aktu = 0
            DF = makeGroups(df, len_df, day1, sub1, lab1, aktu=aktu, initalize=1)
            DF_ = rangeGroups(sub1, lab1, day1)
        if type(DF)==type(()):
            if os.path.exists("./data/output.xlsx"):
                try:
                    df_ = pd.read_excel("./data/output.xlsx", sheet_name="Groups")
                except Exception:
                    df_ = pd.DataFrame([])
                DF_ = pd.concat([df_, DF_])
                total_performed = DF_["Total Students"].sum()
                if total_performed in [240, 220, 200] and len_df>total_performed:
                    otr = list(df["Roll No."][total_performed:])
                    diploma = {otr[i] for i in range(len(otr)) if chkoutliner(otr[i])}
                    otr = set(otr) - diploma
                    otr, diploma = list(otr), list(diploma)
                    otr.sort()
                    diploma.sort()
                    otrs = f'{min(otr)} - {max(otr)}\n{min(diploma)} - {max(diploma)}'
                    DF_.loc[len(DF_)] = ["Other Deptartment Send", otrs, len(otr)+len(list(diploma))]

            with pd.ExcelWriter("./data/output.xlsx") as writer:
                display_dir().to_excel(
                    writer,
                    sheet_name="ouput",
                    index_label=["Subject", "Date", "Lab", "Internal Faculty", "External Faculty", "Time"]
                    )
                DF_.to_excel(writer, sheet_name="Groups", index=False)
        else:
            raise Exception(f"Alloted {DF}")
        with open("./batch.txt", "r+") as f:
            if batch_no !=0 and ic!=1:
                f.write(f"{batch_no}, {ic}")
            batch_no, ic = f.read().split()
            batch_no = int(batch_no[0])
            ic = int(ic)
