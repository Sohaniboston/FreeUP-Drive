from src.utils import human_size

def test_human_size():
    assert human_size(0) == '0B'
    assert human_size(1024) == '1.0KB'
    assert human_size(1024*1024) == '1.0MB'
    assert human_size(1536) == '1.5KB'
