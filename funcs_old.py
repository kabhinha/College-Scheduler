import pandas as pd
import numpy as np

labs = {
    0:"Lab 5",
    1:"Lab 7",
    2:"Lab 8",
    3:"Lab 9"
}

slots = {
    0:"9:00-10:30",
    1:"10:30-12:00",
    2:"1:00-2:30",
    3:"2:30-4:00"
}


def locate_in_df(df:pd.DataFrame, value)->tuple:
    "Return the locations of value present in a DataFrame"
    global static_record
    try:
        a = df.to_numpy()
        row = list(np.where(a == value)[0])
        col = list(np.where(a == value)[1])
        col = [df.columns[i] for i in col]
        return row,col
    except Exception:
        return True


def getLabIndex(x):
    for i, j in labs.items():
        if x==j:
            return i


def makeSchedule(subs:list, Day1:str, Day2:str, total_batch_made:int)->pd.DataFrame:
        date = [Day1, Day2]
        cols = ["Date", "Time"]
        cols.extend(labs.values())
        df = pd.DataFrame([[np.nan for _ in range(6)] for _ in range(8)], columns=cols)
        removed = []
        remover = 0
        for i in range(len(labs.keys())-len(subs)):
                exec(f"del df['{labs[remover]}']")
                removed.append(labs[remover])
                remover+=1
        labs_used = list(set(labs.values()) - set(removed))
        labs_used.sort(key=getLabIndex)
        LABS_used = [f"{labs_used[i]}\n{subs[i]}" for i in range(len(subs))]

        g_counter = 0
        slot_counter = 0
        for i in range(10):
                if (i+1)%5==0:
                        df.loc[slot_counter, ["Date", "Time"]] =[np.nan, "External"]
                        slot_counter+=1
                        df.loc[slot_counter, ["Date", "Time"]] =[np.nan, "Internal"]
                        slot_counter+=1
                else:
                        df.loc[slot_counter, ["Date", "Time"]] =[date[slot_counter//5], slots[slot_counter%4]]
                        for j in range(remover, len(labs.keys())):
                                if g_counter+1<=total_batch_made :
                                        row, col = locate_in_df(df, f"G{g_counter+1}")
                                        if slot_counter not in row and labs[j] not in col:
                                                df.loc[slot_counter, labs[j]] = f"G{g_counter+1}"
                                                g_counter=(g_counter+1)%(total_batch_made)
                                        else: # Add incremented group after checking pre-existing
                                                row, col = locate_in_df(df, f"G{g_counter+2}")
                                                if slot_counter not in row and labs[j] not in col:
                                                        df.loc[slot_counter, labs[j]] = f"G{g_counter+2}"
                                                        g_counter=(g_counter+2)%(total_batch_made)
                                                else:
                                                        break
                        slot_counter+=1
        inside = list(slots.values())
        inside.extend(["Internal Faculty", "External Faculty"])
        inside = inside*2
        outside = [f"{Day1}"]*6
        outside.extend((f"{Day2} "*6).split())
        hier_index = list(zip(outside,inside))
        hier_index = pd.MultiIndex.from_tuples(hier_index)
        df = pd.DataFrame(df[labs_used].to_numpy(), index=hier_index, columns=LABS_used)
        return df



def preprocessData(path, yr, aktu=None, ours=None):
    FILE = pd.ExcelFile(path)
    ranges = []
    global min, max
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
    df.index = [i+1 for i in range(len(df))]
# Check the faculty coming
    if aktu==1:
        total_1_day=120
    elif ours==1:
        total_1_day=100
    elif aktu==1 and ours==1:
        total_1_day = (120,100)
    
    global batch_no
    batch_no = 1
    indexCounter=1
    batchCounter  = 0
    if type(total_1_day)==type(1): # Single type
        for i in range(len(df)//total_1_day):
            for j in range(1,total_1_day//30+1):
                for k in range(indexCounter, indexCounter+30,1):
                    batch_no=batchCounter+j
                    df.loc[k,"Batch"] = f"G{batch_no}"
                indexCounter += 30
            batchCounter+=total_1_day//30
    else: # Multiple Type
    # TODO: Ask what to do if 1 aktu's and 1 our come
        pass

    df = df.fillna("Other dept.")
    
    # Segregrating batches
    prv = [roll for i,roll in df.to_dict()["Roll No."].items() if f"{yr[-2:]}014301" not in df.to_dict()["Roll No."][i] and df.to_dict()["Batch"][i]=="G1"]
    G1 = df[df["Batch"]=="G1"]
    G1 = list(G1[[False if df.loc[i, "Roll No."] in prv else True for i in range(1,len(G1)+1)]].to_dict()["Roll No."].values())
    ranges.append(["G1", f"{min(G1)} - {max(G1)}"])
    s = ""
    for i in prv:
        s+=i+", "
    s = s[:-2]+"\n"
    ranges[0][1] = s+ranges[0][1]
    try:
        for i in range(2, batch_no+1):
            exec(f"G{i} = list(df[df['Batch']=='G{i}'].to_dict()['Roll No.'].values())")
            Max, Min = eval(f"max(G{i})"), eval(f"min(G{i})")
            ranges.append([f'G{i}', f"{Min} - {Max}"])
    except Exception:
        print(i)
    lat = [roll for i,roll in df.to_dict()["Roll No."].items() if f"{yr[-2:]}014301" not in df.to_dict()["Roll No."][i] and (df.to_dict()["Batch"][i]==f"G{batch_no}" or df.to_dict()["Batch"][i]=="Other dept.")]
    if df.loc[locate_in_df(df, lat[1])[0][0], "Batch"]==f"G{batch_no}":
        exec(f'G{batch_no} = df[df["Batch"]=="G{batch_no}"]')
        exec(f"G{batch_no} = list(G{batch_no}[[False if df.loc[i, 'Roll No.'] in lat else True for i in range(1,len(G{batch_no})+1)]].to_dict()['Roll No.'].values())")
        Max, min = eval(f"max(G{batch_no})"), eval(f"min(G{batch_no})")
        ranges[-1][1] = f"{Min} - {Max}"
    else:
        otr = list(df[df['Batch']=='Other dept.'].to_dict()['Roll No.'].values())
        otr = [i for i in otr if i not in lat]
        others = f"{min(otr)} - {max(otr)}" + "\n"
        for i in lat:
            others += i + ", "
        others = others[:-2] 
        ranges.append(["Other dept.", others])
    df = pd.DataFrame(ranges)
    df.columns = ["Group", "Roll No. Range"]
    df = df.set_index("Group")
    return df, batch_no