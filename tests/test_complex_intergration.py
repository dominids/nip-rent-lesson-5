import pytest
from src.manager import Manager
from src.models import Parameters, Bill, Apartment, Tenant, Transfer


@pytest.fixture
def manager_with_test_data(tmp_path):
    apartments_file = tmp_path / "apartments.json"
    tenants_file = tmp_path / "tenants.json"
    transfers_file = tmp_path / "transfers.json"
    bills_file = tmp_path / "bills.json"
    
    apartments_data = {
        "apart-polanka": {
            "key": "apart-polanka",
            "name": "Polanka",
            "location": "Polanka 3a",
            "area_m2": 65,
            "rooms": {
                "room-bigger": {"name": "Bigger Room", "area_m2": 20},
                "room-medium": {"name": "Medium Room", "area_m2": 18},
                "room-smaller": {"name": "Smaller Room", "area_m2": 15}
            }
        }
    }
    
    tenants_data = {
        "tenant-001": {
            "name": "John Doe",
            "apartment": "apart-polanka",
            "room": "room-bigger",
            "rent_pln": 1200.0,
            "deposit_pln": 2400.0,
            "date_agreement_from": "2025-01-01",
            "date_agreement_to": "2026-12-31"
        }
    }
    
    transfers_data = []
    
    bills_data = [
        {
            "amount_pln": 760.00,
            "date_due": "2025-02-15",
            "settlement_year": 2025,
            "settlement_month": 1,
            "apartment": "apart-polanka",
            "type": "rent"
        },
        {
            "amount_pln": 150.00,
            "date_due": "2025-02-12",
            "settlement_year": 2025,
            "settlement_month": 1,
            "apartment": "apart-polanka",
            "type": "electricity"
        },
        {
            "amount_pln": 85.50,
            "date_due": "2025-02-12",
            "settlement_year": 2025,
            "settlement_month": 1,
            "apartment": "apart-polanka",
            "type": "water"
        },
        {
            "amount_pln": 800.00,
            "date_due": "2025-03-15",
            "settlement_year": 2025,
            "settlement_month": 2,
            "apartment": "apart-polanka",
            "type": "rent"
        },
        {
            "amount_pln": 120.00,
            "date_due": "2025-03-20",
            "settlement_year": 2025,
            "settlement_month": 3,
            "apartment": "apart-polanka",
            "type": "electricity"
        }
    ]
    
    import json
    
    with open(apartments_file, 'w') as f:
        json.dump(apartments_data, f)
    
    with open(tenants_file, 'w') as f:
        json.dump(tenants_data, f)
    
    with open(transfers_file, 'w') as f:
        json.dump(transfers_data, f)
    
    with open(bills_file, 'w') as f:
        json.dump(bills_data, f)
    
    params = Parameters(
        apartments_json_path=str(apartments_file),
        tenants_json_path=str(tenants_file),
        transfers_json_path=str(transfers_file),
        bills_json_path=str(bills_file)
    )
    
    return Manager(params)


class TestGetApartmentCosts:
    
    def test_apartment_does_not_exist(self, manager_with_test_data):
        manager = manager_with_test_data
        result = manager.get_apartment_costs("apart-nonexistent", 2025, 1)
        
        assert result == 0.0, "Metoda powinna zwrócić 0.0 dla nieistniejącego mieszkania"
    
    def test_no_bills(self, manager_with_test_data):

        manager = manager_with_test_data
        result = manager.get_apartment_costs("apart-polanka", 2025, 4)
        
        assert result == 0.0, "Metoda powinna zwrócić 0.0 gdy brak rachunków w danym miesiącu"
    
    def test_multiple_bills(self, manager_with_test_data):
        manager = manager_with_test_data
        result = manager.get_apartment_costs("apart-polanka", 2025, 1)
        
        assert result == 995.50, "Metoda powinna zwrócić 995.50 dla stycznia 2025 (suma 3 rachunków)"