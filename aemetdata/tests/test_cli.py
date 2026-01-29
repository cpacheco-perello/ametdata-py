from aemetdata.cli import parse_params


def test_parse_params_empty():
    assert parse_params([]) == {}


def test_parse_params_ok():
    assert parse_params(["a=1", "b=dos"]) == {"a": "1", "b": "dos"}
