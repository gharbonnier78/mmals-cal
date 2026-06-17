import pandas as pd
from mmals_cal.splitting import assign_harmonized_roles

def test_25_75_split():
    df=pd.DataFrame({'seed':[0]*40,'task_id':[0]*40,'true_class':[0]*40,'sample_id':range(40)})
    out=assign_harmonized_roles(df,7)
    assert (out.role=='calibration_reserved').sum()==10
    assert (out.role=='deployment').sum()==30
