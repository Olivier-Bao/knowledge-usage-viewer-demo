"""Synthetic public showcase, created 2026-11-10; not the private engine."""
import json
import sys
from pathlib import Path
from copy import deepcopy

import math

def validate(record):
    issues = []
    if record.get('schema_version') != 1:
        issues.append('unsupported_schema')
    if record.get('data_kind') != 'synthetic':
        issues.append('demo_requires_synthetic_data')
    tokens = record.get('target_tokens', [])
    if not tokens or not all(isinstance(t, str) for t in tokens):
        issues.append('invalid_tokens')
    sources = record.get('sources', [])
    ids = [s.get('id') for s in sources]
    if None in ids or len(set(ids)) != len(ids):
        issues.append('duplicate_or_missing_source_id')
    for signal in record.get('signals', []):
        if signal.get('source_id') not in ids:
            issues.append('unknown_source')
        values = signal.get('values', [])
        if len(values) != len(tokens):
            issues.append('token_signal_length_mismatch')
        if not all(type(v) in (int, float) and math.isfinite(v) for v in values):
            issues.append('non_finite_or_non_numeric_signal')
    if not record.get('signals'):
        issues.append('missing_signals')
    return issues

def self_test(record):
    assert validate(record) == []
    bad = deepcopy(record)
    bad['signals'][0]['values'].pop()
    assert 'token_signal_length_mismatch' in validate(bad)
    bad = deepcopy(record)
    bad['signals'][0]['source_id'] = 'missing'
    assert 'unknown_source' in validate(bad)
    bad = deepcopy(record)
    bad['signals'][0]['values'][0] = float('nan')
    assert 'non_finite_or_non_numeric_signal' in validate(bad)
    bad = deepcopy(record)
    bad['sources'].append(bad['sources'][0])
    assert 'duplicate_or_missing_source_id' in validate(bad)
    print('5 checks passed')

if __name__ == '__main__':
    record = json.loads(Path(__file__).with_name('sample.json').read_text(encoding='utf-8'))
    if '--self-test' in sys.argv:
        self_test(record)
    else:
        issues = validate(record)
        print(json.dumps({'data_kind': 'synthetic', 'valid': not issues, 'issues': issues}, ensure_ascii=False, indent=2))
        sys.exit(bool(issues))
