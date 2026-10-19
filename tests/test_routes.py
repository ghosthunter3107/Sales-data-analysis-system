import pytest
import io
from app import create_app
from core import data_store

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test home landing page renders successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Sales Analytics" in response.data

def test_upload_page_get(client):
    """Test upload page loads."""
    response = client.get('/upload')
    assert response.status_code == 200
    assert b"Upload Sales Data" in response.data

def test_load_sample_dataset(client):
    """Test loading demo clean sample dataset."""
    response = client.get('/load-sample/clean', follow_redirects=True)
    assert response.status_code == 200
    assert b"sample_sales.csv" in response.data
    assert data_store.has_active_data()

def test_clean_action_route(client):
    """Test triggering cleaning on sample dirty dataset."""
    client.get('/load-sample/issues', follow_redirects=True)
    response = client.post('/clean', follow_redirects=True)
    assert response.status_code == 200
    assert b"Data Cleaning Complete" in response.data

def test_dashboard_route_with_data(client):
    """Test dashboard displays KPI cards when data is loaded."""
    client.get('/load-sample/clean', follow_redirects=True)
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Total Revenue" in response.data
    assert b"Average Order Value" in response.data
    assert b"Best-Selling Product" in response.data

def test_charts_route_with_data(client):
    """Test charts page loads."""
    client.get('/load-sample/clean', follow_redirects=True)
    response = client.get('/charts')
    assert response.status_code == 200
    assert b"monthlyRevenueChart" in response.data

def test_database_page(client):
    """Test database management page renders gracefully."""
    response = client.get('/database')
    assert response.status_code == 200
    assert b"MySQL Database" in response.data

def test_api_status(client):
    """Test /api/status endpoint returns valid JSON."""
    response = client.get('/api/status')
    assert response.status_code == 200
    data = response.get_json()
    assert 'database' in data
    assert 'dataset' in data

def test_api_charts_data(client):
    """Test /api/charts-data endpoint returns chart dataset."""
    client.get('/load-sample/clean', follow_redirects=True)
    response = client.get('/api/charts-data')
    assert response.status_code == 200
    data = response.get_json()
    assert 'monthly_revenue' in data
    assert 'category_revenue' in data
    assert 'top_products' in data
