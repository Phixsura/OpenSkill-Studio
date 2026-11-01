from app.services.app_marketplace_extension_sandbox_output_formatter import (
    OutputFormatterService,
)
import json


SAMPLE = [
    {"name": "Alice", "age": 30, "city": "NYC"},
    {"name": "Bob", "age": 25, "city": "SF"},
    {"name": "Charlie", "age": 35, "city": "LA"},
]


def test_to_json():
    svc = OutputFormatterService()
    output = svc.to_json(SAMPLE)
    parsed = json.loads(output)
    assert len(parsed) == 3
    assert parsed[0]["name"] == "Alice"


def test_to_json_field_select():
    svc = OutputFormatterService()
    output = svc.to_json(SAMPLE, fields=["name", "age"])
    parsed = json.loads(output)
    assert "city" not in parsed[0]


def test_to_csv():
    svc = OutputFormatterService()
    output = svc.to_csv(SAMPLE)
    lines = output.strip().split("\n")
    assert lines[0] == "name,age,city"
    assert "Alice" in lines[1]
    assert len(lines) == 4


def test_csv_escape():
    svc = OutputFormatterService()
    data = [{"note": 'Has "quotes" and, commas'}]
    output = svc.to_csv(data)
    assert '""' in output  # escaped quotes


def test_to_markdown():
    svc = OutputFormatterService()
    output = svc.to_markdown_table(SAMPLE)
    assert "| name |" in output
    assert "| --- |" in output
    assert "| Alice |" in output


def test_to_html():
    svc = OutputFormatterService()
    output = svc.to_html_table(SAMPLE)
    assert "<table>" in output
    assert "<th>name</th>" in output
    assert "<td>Alice</td>" in output


def test_html_escapes():
    svc = OutputFormatterService()
    data = [{"value": '<script>alert("xss")</script>'}]
    output = svc.to_html_table(data)
    assert "<script>" not in output
    assert "&lt;script&gt;" in output


def test_sort_data():
    svc = OutputFormatterService()
    sorted_data = svc.sort_data(SAMPLE, "age", descending=True)
    assert sorted_data[0]["name"] == "Charlie"
    assert sorted_data[-1]["name"] == "Bob"


def test_empty_data():
    svc = OutputFormatterService()
    assert svc.to_csv([]) == ""
    assert svc.to_markdown_table([]) == ""
    assert svc.to_html_table([]) == "<table></table>"
