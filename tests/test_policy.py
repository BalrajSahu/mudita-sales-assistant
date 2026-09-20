from app.qualification import qualify, route

def test_missing():
    assert qualify({'company_size':10})['status']=='needs_more_information'
def test_qualified():
    q=qualify({'company_size':10,'decision_maker':True,'timeline':'within 3 months','budget_usd':10000,'country':'IN'})
    assert q['status']=='qualified'
def test_route():
    assert route('IN')=='rep_priya'
    assert route('US')=='rep_alex'
