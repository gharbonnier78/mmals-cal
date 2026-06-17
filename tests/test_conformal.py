import numpy as np
from mmals_cal.conformal import finite_sample_quantile, lac_nonconformity

def test_quantile_index():
    x=np.arange(1,11,dtype=float)
    assert finite_sample_quantile(x,0.1)==10.0

def test_nonconformity():
    p=np.array([[.8,.2],[.1,.9]])
    y=np.array([0,1])
    assert np.allclose(lac_nonconformity(p,y),[.2,.1])
