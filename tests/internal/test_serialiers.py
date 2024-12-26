from mantelo.internal.serializers import JsonSerializer


def test_content_type():
    assert JsonSerializer().content_type == "application/json"


def test_supported_content_types():
    assert JsonSerializer().supported_content_types == [
        "application/json",
        "application/x-javascript",
        "text/javascript",
        "text/x-javascript",
        "text/x-json",
    ]


def test_load_dump():
    data = {
        "foo": "bar",
        "baz": 42,
        "qux": True,
        "elantris": {"Sarene": "Raoden", "Hrathen": [1, 2, 3]},
    }
    ser = JsonSerializer().dumps(data)
    assert isinstance(ser, str)
    assert JsonSerializer().loads(ser) == data
