from app.services.app_marketplace_app_app_app_app_app_app_app_docs_renderer import parse_doc

def test_parse():
    content = """---
title: Getting Started
category: guides
---

# Introduction

Welcome to the platform.

## Installation

Run the installer.

## Configuration

Set up your config.

### Advanced Config

More options here.
"""
    r = parse_doc(content)
    assert r["frontmatter"]["title"] == "Getting Started"
    assert r["frontmatter"]["category"] == "guides"
    assert len(r["headings"]) == 4
    assert r["headings"][0]["text"] == "Introduction"
    assert r["headings"][0]["slug"] == "introduction"
    assert r["headings"][3]["level"] == 3
    assert r["has_toc"]
    assert r["read_time_min"] >= 1

def test_no_frontmatter():
    r = parse_doc("# Hello\n\nWorld")
    assert r["frontmatter"] == {}
    assert r["headings"][0]["text"] == "Hello"
