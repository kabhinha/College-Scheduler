import pandas as pd
import numpy as np
import os

batch_no, ic = 0, 1


labs = {
    0:"Lab 5",
    1:"Lab 7",
    2:"Lab 8",
    3:"Lab 9"
}

slots = {
    0:"9:00 AM -10:30 AM",
    1:"10:30 AM-12:00 PM",
    2:"1:00 PM -2:30 PM",
    3:"2:30 AM-4:00 PM"
}

def updateBatch():
    with open("./batch.txt", "r+") as f:
        global batch_no, ic
        if batch_no !=0 and ic!=1:
            f.write(f"{batch_no}, {ic}")
            return
        batch_no, ic = f.read().split()
        batch_no = int(batch_no[0])
        ic = int(ic)

# Main Functiion
def preprocessData(path):
    """
    Takes the MultiSection file path and return the combine sorted dataframe and its length
    """
    FILE = pd.ExcelFile(path)
    dfs = [list((iD, pd.read_excel(path, sheet_name=i))) for iD,i in enumerate(FILE.sheet_names) if "LATERAL" not in i]
    for i in range(len(dfs)):
        dfs[i][1]=dfs[i][1][2:]
        dfs[i][1].columns = dfs[i][1].loc[2, dfs[i][1].columns]
        for j in dfs[i][1].columns:
            if j not in ["Roll No.", "S.No."]:
                del dfs[i][1][j]
        dfs[i][1]=dfs[i][1][1:]
        dfs[i][1]=dfs[i][1].set_index("S.No.")
        dfs[i][1]["Batch"]=np.nan

    df = pd.concat([i[1] for i in dfs])
    df = df.sort_values("Roll No.")
    df = df.astype({"Roll No.":str})
    len_df = len(df)
    df.index = [i+1 for i in range(len_df)]
    return df, len_df


def isAlloted(SUB:str, LAB:str, Date:str, GROUP:str="OLD")->int:
    """
    Checks weather lab is alloted to a subject on a date or not
    returns
    0: Not Alloted
    1: ALL Alloted(Make Schdule)
    2: Lab Alloted
    3: Group Alloted
    4: Group performed
    """
    alloted, f = [], 0
    global batch_no
    for i in next(os.walk("./data/Alloted/"))[2]:
        sub = i.split()[0]
        lab = "Lab "+ i.split()[2]
        date = i.split()[3][:-5]
        allotedGroups = list(pd.read_excel(f"./data/Alloted/{i}")["Batch"].value_counts().to_dict().keys())
        alloted.append((sub, lab, date, allotedGroups))
    for i in alloted:
            if SUB==i[0] and LAB==i[1] and Date==i[2] and GROUP in i[3]: # Make Schedule
                f = 1
                break
            elif SUB!=i[0] and LAB==i[1] and Date==i[2] and i[1]!="X" and (GROUP not in i[3] or GROUP in i[3]): # Change Lab
                f = 2
                break
            elif SUB!=i[0] and LAB!=i[1] and Date==i[2] and GROUP in i[3]: # Group is alloted already
                f = 3
                break
            elif SUB==i[0] and (LAB==i[1] or LAB!=i[1]) and (Date!=i[2] or Date==i[2]) and GROUP in i[3]:
                f=4
                break
    if f==1:
        grps_path = f"./data/Alloted/{i[0]} {i[1]} {i[2]}.xlsx"
        return (f, grps_path)
    return f

# Main Function
def makeGroups(df, len_df, date, sub, lab, aktu, initalize=0):
    """
    Make groups and returns the allocation details
    0: Groups are make successfully (Also return grouped df)
    1: All performed
    2: Lab Alloted
    3: Group Alloted
    """
    total_1_day = 120
    if aktu==0:
        total_1_day=100
    global batch_no,ic
    if initalize==1:
        if os.path.exists(f"./data/Alloted/{sub} {lab} {date}.xlsx"):
            os.remove(f"./data/Alloted/{sub} {lab} {date}.xlsx")
        batch_no, ic=0, 1
    else:
        batch_no = max(int(i[1]) for i in list(pd.read_excel(f"./data/Alloted/{sub} {lab} {date}.xlsx")["Batch"].value_counts().to_dict().keys()))
        ic = len(pd.read_excel(f"./data/Alloted/{sub} {lab} {date}.xlsx"))+1
    batchCounter = batch_no
    indexCounter= ic
    if batchCounter<(len_df//30-1) and isAlloted(sub, lab, date, f"G{batch_no+1}") in [0, 3, 4]:
        if isAlloted(sub, lab, date, f"G{batch_no+1}") in [3, 4]:
            while isAlloted(sub, lab, date, f"G{batchCounter+1}") in [3, 4]:
                print("Batch:", batchCounter+1, "Performed", indexCounter)
                batchCounter +=1
                indexCounter += 30
            if batchCounter+1==len_df//30+1:
                return 1
        for i in range(1,total_1_day//30+1):
            for j in range(indexCounter, indexCounter+30,1):
                batch_no=batchCounter+i
                allocation = isAlloted(sub, lab, date, f"G{batch_no}")
                if allocation==0 and indexCounter <= len_df:
                    df.loc[j,"Batch"] = f"G{batch_no}"
            indexCounter += 30
        ic=indexCounter
        df = df.dropna()
        if len(df)==0:
            raise "Alloted"
        df.to_excel(f"./data/Alloted/{sub} {lab} {date}.xlsx", index=False)
        return 0, df
    elif (len_df/30!=0) and isAlloted(sub, lab, date, "Other Dept.") in [0, 3, 4]:
        if isAlloted(sub, lab, date, f"G{batchCounter+1}") in [3, 4]:
            return 1
        for i in range(1,total_1_day//30+1):
            for j in range(indexCounter, indexCounter+30,1):
                batch_no=batchCounter+i
                allocation = isAlloted(sub, lab, date, f"G{batch_no}")
                if allocation==0 and indexCounter <= len_df:
                    df.loc[j,"Batch"] = "Other Dept."
            indexCounter += 30
        ic=indexCounter
        df = df.dropna()
        if len(df)==0:
            return 1
        df.to_excel(f"./data/Alloted/{sub} {lab} {date}.xlsx", index=False)
        return 0, df
    else:
        return isAlloted(sub, lab, date, f"G{batch_no+1}")


def chkoutliner(roll):
    "Returns True if roll number is not of the considerd session"
    with open("./session.txt") as f:
        session = f.read()
    if f"{session[-2:]}014301" not in str(roll):
        return True
    return False

def joinoutliner(otr, grp):
    "Join the outliners to the group"
    a = ""
    for i in otr:
        a+=i+", "
    a=a[:-2]+"\n"
    result = a+ f"{min(grp)} - {max(grp)}"
    return result

# Main function
def rangeGroups(sub, lab, date):
    global min, max
    ranges = []
    df = pd.read_excel(f"./data/Alloted/{sub} {lab} {date}.xlsx")
    df.index = [i+1 for i in range(len(df))]
    df = df.astype({"Roll No.": str})
    try:
        G1 = df[df["Batch"]=="G1"]
        pre = list(G1[G1["Roll No."].apply(chkoutliner)].to_dict()["Roll No."].values())
        G1 = set(G1["Roll No."].to_list()) - set(pre)
        G1 = list(G1)
        G1.sort()
        ranges.append(["G1", joinoutliner(pre, G1), len(G1)+len(pre)])
    except Exception as e:
        print(e.__class__)
    for i in df["Batch"].value_counts().to_dict().keys():
        if i!="G1":
            exec(f"{i} = list(df[df['Batch']=='{i}'].to_dict()['Roll No.'].values())")
            Max, Min, Total = eval(f"max({i})"), eval(f"min({i})"), eval(f"len({i})")
            if Total != 30:
                exec(f"outliers = [i for i in {i} if chkoutliner(i)]")
                ranges.append([f'{i}', f"{Min} - {Max}\n{outliers}", Total])
            else:
                ranges.append([f'{i}', f"{Min} - {Max}", Total])
    df = pd.DataFrame(ranges, columns=["Group", "Roll No. Range", "Total Students"])
    return df

def display_dir():
    alloted = []
    for i in next(os.walk("./data/Alloted/"))[2]:
        sub = i.split()[0]
        lab = "Lab "+ i.split()[2]
        date = i.split()[3][:-5]
        allotedGroups = list(pd.read_excel(f"./data/Alloted/{i}")["Batch"].value_counts().to_dict().keys())
        alloted.append((sub, lab, date, allotedGroups))
    a = []
    b=[]
    for i in range(len(alloted)):
        for j in range(len(alloted[i][3])):
            a.append((alloted[i][0], alloted[i][2], alloted[i][1], np.nan, np.nan, slots[j]))
            b.append((alloted[i][3][j]))
            
    a = pd.MultiIndex.from_tuples(a)
    b = pd.DataFrame(b, index=a, columns=["Groups"])
    return b


def writeDFs(path, df1, df2):
    with pd.ExcelWriter(path) as writer:
        df1.to_excel(writer, sheet_name="Schdule", index_label=["Date", "Time"])
        df2.to_excel(writer, sheet_name="Groups", index_label="Group")

if __name__=="__main__":
    # session = "2021"
    # ranges = []
    # df = pd.read_excel(r"E:\Users\HP\Desktop\aalix clg\projects\IMSECCSE\practical schedular\data\Alloted\KCS553 Lab 5 8-2-2024.xlsx")
    # df = df.astype({"Roll No.": str})
    # G1 = df[df["Batch"]=="G1"]
    # pre = list(G1[G1["Roll No."].apply(chkoutliner)].to_dict()["Roll No."].values())
    # G1 = set(G1["Roll No."].to_list()) - set(ranges)
    # G1 = list(G1)
    # G1.sort()
    print(rangeGroups("KCS553", "Lab 5", "8-2-2024"))