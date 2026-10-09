"""Shared sample personas; these are examples, never real users."""
import json
from engine import ROOT

def personas():
    return json.loads((ROOT/'config/personas.json').read_text())

def saved_pairs():
    defaults=personas()
    return [{**row,**defaults[row['role']]} for row in json.loads((ROOT/'demo_data/manifest.json').read_text())]
