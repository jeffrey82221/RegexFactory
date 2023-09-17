from regexfactory import Optional, Amount, Multi
def test_lt_operator():
    assert Optional('a') < Amount('a', 1)
    assert Optional('a') < Amount('a', 2)
    assert Amount('a', 3) < Multi('a')
    assert Amount('a', 2) < Amount('a', 3)
