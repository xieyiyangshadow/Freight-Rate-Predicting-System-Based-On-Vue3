#!/usr/bin/env python
"""Test enhanced dataset features: preview, target column selection, etc."""

import requests
import json
import csv
import tempfile
import os

BASE_URL = "http://127.0.0.1:8001/api"

# First, register a user
def register_user():
    """Register a test user and return user ID"""
    import time
    timestamp = str(int(time.time()))
    
    print("=== Registering Test User ===")
    data = {
        'username': f'testuser_{timestamp}',
        'phone': f'138000{timestamp[-4:]}',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/register/", json=data)
        print(f"Register Status: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            user_id = result.get('id')
            print(f"User ID: {user_id}")
            return user_id
        else:
            print(f"Register response: {response.json()}")
    except Exception as e:
        print(f"Error during registration: {e}")
        import traceback
        traceback.print_exc()
    
    # If registration fails, try login
    print("=== Trying Login ===")
    login_data = {
        'phone': data['phone'],
        'password': 'testpass123'
    }
    try:
        response = requests.post(f"{BASE_URL}/users/login/", json=login_data)
        print(f"Login Status: {response.status_code}")
        if response.status_code in [200, 201]:
            result = response.json()
            user_id = result.get('id')
            print(f"User ID: {user_id}")
            return user_id
        else:
            print(f"Login failed: {response.json()}")
    except Exception as e:
        print(f"Error during login: {e}")
    
    return "1"  # Fallback to default user ID


USER_ID = register_user()
USER_ID = str(register_user())
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
            headers = {'X-Client-User': USER_ID}
            
            response = requests.post(
                f"{BASE_URL}/models/datasets/",
                files=files,
                data=data,
                headers=headers
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
    
    headers = {'X-Client-User': USER_ID}
    response = requests.get(
        f"{BASE_URL}/models/datasets/{dataset_id}/",
        headers=headers
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
    
    headers = {'X-Client-User': USER_ID}
    data = {'target_column': 'price'}
    
    response = requests.patch(
        f"{BASE_URL}/models/datasets/{dataset_id}/",
        json=data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Updated Target Column: {result.get('target_column')}")
    
    # Verify by getting again
    response = requests.get(
        f"{BASE_URL}/models/datasets/{dataset_id}/",
        headers=headers
    )
    result = response.json()
    print(f"Verified Target Column: {result.get('target_column')}")


def test_list_datasets():
    """Test listing all datasets"""
    print("\n=== Test 4: List All Datasets ===")
    
    headers = {'X-Client-User': USER_ID}
    response = requests.get(
        f"{BASE_URL}/models/datasets/",
        headers=headers
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
