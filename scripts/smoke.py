#!/usr/bin/env python3
"""HTTP integration smoke test. Run only against your local demo instance.

Default: URL lifecycle and access controls. --engineering adds real Maven builds
and simulated approvals using the two independent local demonstration identities.
No production deployment or remote repository push is performed.
"""
import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.request
import uuid


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://localhost:8080')
    parser.add_argument('--engineering', action='store_true')
    parser.add_argument('--repository-path', default='.')
    args = parser.parse_args()
    opener = urllib.request.build_opener(NoRedirect())

    def request(method, path, body=None, user=None, expected=200, headers=None):
        hdr = dict(headers or {})
        if body is not None:
            hdr['Content-Type'] = 'application/json'
        if user:
            password = os.getenv('AGENTIC_' + user.upper() + '_PASSWORD', 'local-' + user + '-only')
            hdr['Authorization'] = 'Basic ' + base64.b64encode(f'{user}:{password}'.encode()).decode()
        req = urllib.request.Request(args.base_url.rstrip('/') + path,
                                     data=None if body is None else json.dumps(body).encode(),
                                     headers=hdr, method=method)
        try:
            response = opener.open(req, timeout=900)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read()
            if response.status != expected:
                raise AssertionError(f'{method} {path}: expected {expected}, got {response.status}: {raw[:1000]!r}')
            return (json.loads(raw) if raw else {}), response.headers

    request('GET', '/actuator/health')
    alias = 'smoke-' + uuid.uuid4().hex[:12]
    payload = {'url': 'https://example.com/smoke', 'customAlias': alias}
    headers = {'Idempotency-Key': alias}
    link, _ = request('POST', '/api/v1/links', payload, expected=201, headers=headers)
    repeated, _ = request('POST', '/api/v1/links', payload, expected=201, headers=headers)
    assert repeated['code'] == link['code'] == alias
    _, hdr = request('GET', '/r/' + alias, expected=302)
    assert hdr['Location'] == payload['url']
    request('GET', f'/api/v1/links/{alias}/analytics', expected=401)
    deadline = time.monotonic() + 10
    while True:
        analytics, _ = request('GET', f'/api/v1/links/{alias}/analytics', user='admin')
        if analytics['totalClicks'] == 1:
            break
        if time.monotonic() > deadline:
            raise AssertionError('Analytics event was not recorded')
        time.sleep(0.1)
    request('DELETE', '/api/v1/links/' + alias, user='admin', expected=204)
    request('GET', '/r/' + alias, expected=410)
    print('PASS URL creation, idempotency, redirect, analytics authorization, analytics and disable', flush=True)

    if not args.engineering:
        return
    for scenario, requirement in [
        ('GREENFIELD', 'Create an expiry capability with executable tests and reviewer documentation.'),
        ('BROWNFIELD', 'Create a repair-demo capability with executable tests and documentation.'),
        ('AMBIGUOUS', 'Improve the service with whatever is best while preserving safe controls.'),
    ]:
        run, _ = request('POST', '/api/v1/engineering/runs', {
            'requirement': requirement, 'scenario': scenario,
            'repositoryPath': args.repository_path, 'baselineRevision': 'WORKING_TREE',
        }, user='submitter', expected=201)
        endpoint = '/api/v1/engineering/runs/' + run['id']
        assert run['auditChainValid'], run
        if scenario == 'AMBIGUOUS':
            assert run['status'] == 'AWAITING_CLARIFICATION', run
            assert not run.get('patch'), run
            run, _ = request('POST', endpoint + '/cancel', {'reason': 'Smoke test verified clarification safe-stop'}, user='submitter')
            assert run['status'] == 'CANCELLED', run
        else:
            assert run['status'] == 'AWAITING_CHANGE_APPROVAL', run
            run, _ = request('POST', endpoint + '/approvals/change', {
                'artifactHash': run['planHash'], 'comment': 'Local automated smoke test approval'}, user='approver')
            assert run['status'] == 'AWAITING_RELEASE_APPROVAL', run
            builds = run['validationAttempts']
            assert builds[-1]['status'] == 'PASSED' and builds[-1]['reportHashes'], run
            assert builds[-1]['testsRun'] > 0, run
            if scenario == 'BROWNFIELD':
                assert len(builds) == 2 and builds[0]['status'] == 'FAILED', run
            run, _ = request('POST', endpoint + '/approvals/release', {
                'artifactHash': run['outcomeHash'], 'comment': 'Local smoke test evidence verified; no deployment'}, user='approver')
            assert run['status'] == 'RELEASE_READY' and run['auditChainValid'], run
        print(f'PASS {scenario}: {run["status"]}', flush=True)


if __name__ == '__main__':
    main()
