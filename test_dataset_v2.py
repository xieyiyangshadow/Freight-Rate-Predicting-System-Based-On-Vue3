#!/usr/bin/env python
"""Test enhanced dataset features with session management"""

import requests
import json
import csv
import tempfile
import os

BASE_URL = "http://127.0.0.1:8001/api"

# Create a session to maintain login state
session = requests.Session()

def register_and_login():
    """Register or login a test user"""
    import time
    timestamp = str(int(time.time()))
    
    print("=== User Registration/Login ===")
    creds = {
        'username': f'testuser_{timestamp}',
        'phone': f'138000{timestamp[-4:]}',
        'password': 'testpass123'
    }
    
    # Try to register
    try:
        response = session.post(f"{BASE_URL}/users/register/", json=creds)
        print(f"Register Status: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            user_id = result.get('id')
            print(f"Registered User ID: {user_id}")
            return str(user_id)
    except Exception as e:
        print(f"Register error: {e}")
    
    # Try login
    print("=== Attempting Login ===")
    login_data = {
        'phone': creds['phone'],
        'password': 'testpass123'
    }
    try:
        response = session.post(f"{BASE_URL}/users/login/", json=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            user_id = result.get('id')
            print(f"Login User ID: {user_id}")
            return str(user_id)
    except Exception as e:
        print(f"Login error: {e}")
    
    return "1"

USER_ID = register_and_login()


print(f"\nSession cookies: {session.cookies}")
print(f"Session User ID: {USER_ID}")

def test_upload_dataset_with_target():
    """Test uploading a dataset with target column specified"""
    print("\n=== Test 1: Upload Dataset with Target Column ===")
    
    # Create a sample CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['distance', 'weight', 'price', 'target_price'])
        writer.writerow(['100', '50', '1000', '1050'])
        writer.writerow(['200', '75', '1500', '1600'])
        writer.writerow(['150', '60', '1200', '1300'])
        writer.writerow(['300', '100', '2000', '2100'])
        temp_file = f.name
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'file': f}
            data = {
                'name': 'Test Dataset with Target',
                'target_column': 'target_price'
            }
            
            response = session.post(
                f"{BASE_URL}/models/datasets/",
                files=files,
                data=data,
                    headers={'X-Client-User': USER_ID}
            )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        print(f"Dataset ID: {result.get('id')}")
        print(f"Target Column: {result.get('target_column')}")
        print(f"Columns: {json.loads(result.get('columns', '[]'))}")
        
        dataset_id = result.get('id')
        return dataset_id
    finally:
        os.unlink(temp_file)


def test_get_dataset_detail(dataset_id):
    """Test getting dataset detail with data preview"""
    print("\n=== Test 2: Get Dataset Detail with Data Preview ===")
    
    response = session.get(
        f"{BASE_URL}/models/datasets/{dataset_id}/",
            headers={'X-Client-User': USER_ID}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Dataset ID: {result.get('id')}")
    print(f"Name: {result.get('name')}")
    print(f"Target Column: {result.get('target_column')}")
    print(f"Total Rows: {result.get('total_rows')}")
    print(f"Columns: {result.get('columns_list')}")
    
    # Show data preview
    data_preview = result.get('data_preview', [])
    print(f"\nData Preview ({len(data_preview)} rows):")
    if data_preview:
        for i, row in enumerate(data_preview):
            print(f"  Row {i+1}: {row}")
    
    return dataset_id


def test_update_target_column(dataset_id):
    """Test updating target column selection"""
    print("\n=== Test 3: Update Target Column ===")
    
    data = {'target_column': 'price'}
    
    response = session.patch(
        f"{BASE_URL}/models/datasets/{dataset_id}/",
        json=data,
            headers={'X-Client-User': USER_ID}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Updated Target Column: {result.get('target_column')}")
    
    # Verify by getting again
    response = session.get(
        f"{BASE_URL}/models/datasets/{dataset_id}/",
        headers=headers
    )
    result = response.json()
    print(f"Verified Target Column: {result.get('target_column')}")


def test_list_datasets():
    """Test listing all datasets"""
    print("\n=== Test 4: List All Datasets ===")
    
    response = session.get(
        f"{BASE_URL}/models/datasets/",
            headers={'X-Client-User': USER_ID}
    )
    
    print(f"Status: {response.status_code}")
    datasets = response.json()
    print(f"Total Datasets: {len(datasets)}")
    
    for ds in datasets:
        print(f"  - ID: {ds['id']}, Name: {ds['name']}, Target: {ds.get('target_column', 'None')}")


if __name__ == '__main__':
    print("Testing Enhanced Dataset Features")
    print("=" * 50)
    
    # Run tests
    dataset_id = test_upload_dataset_with_target()
    if dataset_id:
        test_get_dataset_detail(dataset_id)
        test_update_target_column(dataset_id)
    
    test_list_datasets()
    
    print("\n" + "=" * 50)
    print("Tests Complete!")
