import os
import time
import requests
from anonlink import randomnames, entitymatch
from phe import paillier
from serialization import *

"""
The URL to test can be overridden with the environment variable
ENTITY_SERVICE_URL

# When running behind ngnix
url = "http://localhost:8851/api/v1"

# When running the flask application directly
set the environment variable ENTITY_SERVICE_URL to "http://localhost:8851"
"""
url = os.environ.get("ENTITY_SERVICE_URL", "http://localhost:8851/api/v1")


def retrieve_result(mapping_id, token):
    print("Retrieving mapping")
    response = requests.get(url + '/mappings/{}'.format(mapping_id),
                            json={'token': token})
    print(response.status_code, response.json())
    return response


def server_status_test():
    print("Connecting to server '{}'".format(url))
    status = requests.get(url + '/status')
    print("Server status:")
    assert status.status_code == 200, 'Server status was {}'.format(status.status_code)
    print(status.json())


def mapping_test(dataset_size=1000):
    """
    Uses the NameList data and schema and a result_type of "mapping"
    """
    print("Connecting to server '{}'".format(url))
    status = requests.get(url + '/status')
    print("Server status:")
    assert status.status_code == 200, 'Server status was {}'.format(status.status_code)
    print(status.json())

    print('*'*80)
    print("Running e2e test with {} entites".format(dataset_size))
    print("Generating local address data")
    nl = randomnames.NameList(dataset_size * 2)
    s1, s2 = nl.generate_subsets(dataset_size, 0.8)

    print("Locally hashing identity data to create bloom filters")
    keys = ('something', 'secret')
    filters1 = entitymatch.calculate_bloom_filters(s1, nl.schema, keys)
    filters2 = entitymatch.calculate_bloom_filters(s2, nl.schema, keys)

    party1_filters = serialize_filters(filters1)
    party2_filters = serialize_filters(filters2)

    print("Servers mappings:")
    print(requests.get(url + '/mappings').json())

    print('Creating a new mapping')
    # ('INDEX', 'NAME freetext', 'DOB YYYY/MM/DD', 'GENDER M or F')
    schema = [
        {"identifier": "INDEX",          "weight": 0, "notes":""},
        {"identifier": "NAME freetext",  "weight": 1, "notes": "max length set to 128"},
        {"identifier": "DOB YYYY/MM/DD", "weight": 1, "notes": ""},
        {"identifier": "GENDER M or F",  "weight": 1, "notes": ""}
    ]
    new_map_response = requests.post(url + '/mappings', json={
        'schema': schema,
        'result_type': 'mapping'
    }).json()
    print(new_map_response)

    id = new_map_response['resource_id']
    print("New mapping request created with id: ", id)

    print("Servers mappings:")
    print(requests.get(url + '/mappings').json())

    print("Checking status without authentication token")
    r = requests.get(url + '/mappings/{}'.format(id), json={})
    print(r.status_code, r.json())
    assert r.status_code == 401

    print("Checking status with invalid token")
    r = requests.get(url + '/mappings/{}'.format(id), json={'token': 'invalid'})
    print(r.status_code, r.json())
    assert r.status_code == 403

    print("Test a mapping that doesn't exist with valid token")
    response = requests.get(
        url + '/mappings/NOT_A_REAL_MAPPING',
        json={'token': new_map_response['result_token']})
    print(response.status_code)
    assert response.status_code == 404

    print("Checking status with valid token (before adding data)")
    r = requests.get(
        url + '/mappings/{}'.format(id),
        json={'token': new_map_response['result_token']})
    print(r.status_code, r.json())
    assert r.status_code == 503

    print("Adding first party's filter data")

    party1_data = {
        'token': new_map_response['update_tokens'][0],
        'clks': party1_filters
    }

    resp1 = requests.put(url + '/mappings/{}'.format(id), json=party1_data)
    # status code should be 201 if a resource was created
    assert resp1.status_code == 201

    r1 = resp1.json()
    assert 'receipt-token' in r1
    print(resp1.status_code, r1)

    print("Adding second party's data - without authentication")
    party2_data = {'clks': party2_filters}
    resp = requests.put(url + '/mappings/{}'.format(id), json=party2_data)
    assert resp.status_code == 401
    assert 'token required' in resp.json()['message']

    print("Adding second party's data - without clk data")
    party2_data = {'token': new_map_response['update_tokens'][1]}
    resp = requests.put(url + '/mappings/{}'.format(id),
                         json=party2_data)
    assert resp.status_code == 400
    assert 'Missing information' in resp.json()['message']

    print("Adding second party's data - properly this time")
    party2_data = {
        'token': new_map_response['update_tokens'][1],
        'clks': party2_filters
    }
    resp2 = requests.put(url + '/mappings/{}'.format(id),
                         json=party2_data)

    assert resp2.status_code == 201

    print("Going to sleep to give the server some processing time...")
    time.sleep(1)

    response = retrieve_result(id, new_map_response['result_token'])
    while not response.status_code == 200:
        snooze = 30*dataset_size/10000
        print("Sleeping for another {} seconds".format(snooze))
        time.sleep(snooze)
        response = retrieve_result(id, new_map_response['result_token'])

    assert response.status_code == 200

    mapping_result = response.json()["mapping"]
    print(mapping_result)


def permutation_test(dataset_size=500):
    """
    Uses the NameList data and schema and a result_type of "permutation"
    """

    print("Running e2e test with {} entites".format(dataset_size))
    print("Generating local address data")
    nl = randomnames.NameList(dataset_size * 2)
    s1, s2 = nl.generate_subsets(dataset_size, 0.8)

    print("Locally hashing identity data to create bloom filters")
    keys = ('something', 'secret')
    filters1 = entitymatch.calculate_bloom_filters(s1, nl.schema, keys)
    filters2 = entitymatch.calculate_bloom_filters(s2, nl.schema, keys)

    party1_filters = serialize_filters(filters1)
    party2_filters = serialize_filters(filters2)

    print("Servers mappings:")
    print(requests.get(url + '/mappings').json())

    print("Generating paillier keypair")
    pub, priv = paillier.generate_paillier_keypair()
    public_key = {'g': pub.g, 'n': pub.n}

    print('Creating a new mapping')
    # ('INDEX', 'NAME freetext', 'DOB YYYY/MM/DD', 'GENDER M or F')
    schema = [
        {"identifier": "INDEX",          "weight": 0, "notes":""},
        {"identifier": "NAME freetext",  "weight": 1, "notes": "max length set to 128"},
        {"identifier": "DOB YYYY/MM/DD", "weight": 1, "notes": ""},
        {"identifier": "GENDER M or F",  "weight": 1, "notes": ""}
    ]
    new_map_response = requests.post(url + '/mappings', json={
        'schema': schema,
        'result_type': 'permutation',
        'public_key': public_key
    }).json()
    print(new_map_response)

    id = new_map_response['resource_id']
    print("New mapping request created with id: ", id)

    print("Checking status without authentication token")
    r = requests.get(url + '/mappings/{}'.format(id), json={})
    print(r.status_code, r.json())
    assert r.status_code == 401

    print("Checking status with invalid token")
    r = requests.get(url + '/mappings/{}'.format(id), json={'token': 'invalid'})
    print(r.status_code, r.json())
    assert r.status_code == 403

    print("Test a mapping that doesn't exist with valid token")
    response = requests.get(
        url + '/mappings/NOT_A_REAL_MAPPING',
        json={'token': new_map_response['result_token']})
    print(response.status_code)
    assert response.status_code == 404

    print("Checking status with valid results token (not receipt token as required)")
    r = requests.get(
        url + '/mappings/{}'.format(id),
        json={'token': new_map_response['result_token']})
    print(r.status_code, r.json())
    assert r.status_code == 403

    print("Adding first party's filter data")

    party1_data = {
        'token': new_map_response['update_tokens'][0],
        'clks': party1_filters
    }

    resp1 = requests.put(url + '/mappings/{}'.format(id), json=party1_data)
    # status code should be 201 if a resource was created
    assert resp1.status_code == 201

    r1 = resp1.json()
    assert 'receipt-token' in r1
    print(resp1.status_code, r1)

    print("Adding second party's data - without authentication")
    party2_data = {'clks': party2_filters}
    resp = requests.put(url + '/mappings/{}'.format(id), json=party2_data)
    assert resp.status_code == 401
    assert 'token required' in resp.json()['message']

    print("Adding second party's data - without clk data")
    party2_data = {'token': new_map_response['update_tokens'][1]}
    resp = requests.put(url + '/mappings/{}'.format(id),
                         json=party2_data)
    assert resp.status_code == 400
    assert 'Missing information' in resp.json()['message']

    print("Adding second party's data - properly this time")
    party2_data = {
        'token': new_map_response['update_tokens'][1],
        'clks': party2_filters
    }
    resp2 = requests.put(url + '/mappings/{}'.format(id),
                         json=party2_data)

    assert resp2.status_code == 201
    r2 = resp2.json()
    print(resp2.status_code, r2)

    print("Going to sleep to give the server some processing time...")
    time.sleep(1)

    print("Retrieving results as organisation 1")
    response = retrieve_result(id, r1['receipt-token'])
    while not response.status_code == 200:
        snooze = 30*dataset_size/10000
        print("Sleeping for another {} seconds".format(snooze))
        time.sleep(snooze)
        response = retrieve_result(id, r1['receipt-token'])

    assert response.status_code == 200
    mapping_result_a = response.json()

    print("Retrieving results as organisation 2")
    response = retrieve_result(id, r2['receipt-token'])
    while not response.status_code == 200:
        snooze = 30*dataset_size/10000
        print("Sleeping for another {} seconds".format(snooze))
        time.sleep(snooze)
        response = retrieve_result(id, r2['receipt-token'])

    assert response.status_code == 200
    mapping_result_b = response.json()

    # Now we will print a few sample matches...

    for original_a_index, element in enumerate(s1):
        new_index = mapping_result_a['permutation'][original_a_index]
        if new_index < 10:
            print(original_a_index, " -> ", new_index, element)

    print("\nOrg 2\n")
    for original_b_index, element in enumerate(s2):
        new_index = mapping_result_b['permutation'][original_b_index]
        if new_index < 10:
            print(original_b_index, " -> ", new_index, element, mapping_result_b['mask'])


if __name__ == "__main__":
    size = int(os.environ.get("ENTITY_SERVICE_TEST_SIZE", "500"))
    repeats = int(os.environ.get("ENTITY_SERVICE_TEST_REPEATS", "1"))

    server_status_test()

    for i in range(repeats):
        mapping_test(size)
        permutation_test(size)
