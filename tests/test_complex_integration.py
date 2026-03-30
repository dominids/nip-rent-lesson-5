import pytest
import json
from src.manager import Manager
from src.models import Parameters, ApartmentSettlement, TenantSettlement


def create_manager(tmp_path, apartments_data, tenants_data, transfers_data, bills_data):
    apartments_file = tmp_path / "apartments.json"
    tenants_file = tmp_path / "tenants.json"
    transfers_file = tmp_path / "transfers.json"
    bills_file = tmp_path / "bills.json"
    
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


APARTMENT_POLANKA = {
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

TENANT_JOHN = {
    "name": "John Doe",
    "apartment": "apart-polanka",
    "room": "room-bigger",
    "rent_pln": 1200.0,
    "deposit_pln": 2400.0,
    "date_agreement_from": "2025-01-01",
    "date_agreement_to": "2026-12-31"
}

BILLS_POLANKA_JAN_FEB_MAR = [
    {"amount_pln": 760.00, "date_due": "2025-02-15", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "rent"},
    {"amount_pln": 150.00, "date_due": "2025-02-12", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "electricity"},
    {"amount_pln": 85.50, "date_due": "2025-02-12", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "water"},
    {"amount_pln": 800.00, "date_due": "2025-03-15", "settlement_year": 2025, "settlement_month": 2, "apartment": "apart-polanka", "type": "rent"},
    {"amount_pln": 120.00, "date_due": "2025-03-20", "settlement_year": 2025, "settlement_month": 3, "apartment": "apart-polanka", "type": "electricity"}
]

BILLS_POLANKA_JAN = [
    {"amount_pln": 900.0, "date_due": "2025-02-15", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "rent"},
    {"amount_pln": 300.0, "date_due": "2025-02-12", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "electricity"}
]


@pytest.fixture
def manager_with_test_data(tmp_path):
    return create_manager(
        tmp_path,
        {"apart-polanka": APARTMENT_POLANKA},
        {"tenant-001": TENANT_JOHN},
        [],
        BILLS_POLANKA_JAN_FEB_MAR
    )


class TestGetApartmentCosts:
    def test_apartment_does_not_exist(self, manager_with_test_data):
        result = manager_with_test_data.get_apartment_costs("apart-nonexistent", 2025, 1)
        assert result == 0.0
    
    def test_no_bills(self, manager_with_test_data):
        result = manager_with_test_data.get_apartment_costs("apart-polanka", 2025, 4)
        assert result == 0.0
    
    def test_multiple_bills(self, manager_with_test_data):
        result = manager_with_test_data.get_apartment_costs("apart-polanka", 2025, 1)
        assert result == 995.50


@pytest.fixture
def manager_for_settlement(tmp_path):
    apartments = {"apart-polanka": APARTMENT_POLANKA}
    tenants = {"tenant-001": TENANT_JOHN}
    transfers = [{"amount_pln": 2000.0, "date": "2025-02-01", "settlement_year": 2025, "settlement_month": 1, "tenant": "John Doe"}]
    bills = [
        {"amount_pln": 760.00, "date_due": "2025-02-15", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "rent"},
        {"amount_pln": 150.00, "date_due": "2025-02-12", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "electricity"},
        {"amount_pln": 85.50, "date_due": "2025-02-12", "settlement_year": 2025, "settlement_month": 1, "apartment": "apart-polanka", "type": "water"},
        {"amount_pln": 800.00, "date_due": "2025-03-15", "settlement_year": 2025, "settlement_month": 2, "apartment": "apart-polanka", "type": "rent"}
    ]
    return create_manager(tmp_path, apartments, tenants, transfers, bills)


class TestGetApartmentSettlement:
    def test_settlement_with_bills_and_transfers(self, manager_for_settlement):
        settlement = manager_for_settlement.get_apartment_settlement("apart-polanka", 2025, 1)
        
        assert isinstance(settlement, ApartmentSettlement)
        assert settlement.apartment == "apart-polanka"
        assert settlement.month == 1
        assert settlement.year == 2025
        assert settlement.total_bills_pln == 995.50
        assert settlement.total_rent_pln == 760.0
        assert settlement.total_due_pln == 1004.50
        assert settlement.total_due_pln > 0
    
    def test_settlement_no_bills_in_month(self, manager_for_settlement):
        settlement = manager_for_settlement.get_apartment_settlement("apart-polanka", 2025, 4)
        
        assert isinstance(settlement, ApartmentSettlement)
        assert settlement.total_bills_pln == 0.0
        assert settlement.total_due_pln == 0.0
    
    def test_settlement_nonexistent_apartment(self, manager_for_settlement):
        settlement = manager_for_settlement.get_apartment_settlement("apart-nonexistent", 2025, 1)
        assert settlement is None


TENANT_JANE = {
    "name": "Jane Smith",
    "apartment": "apart-polanka",
    "room": "room-medium",
    "rent_pln": 1000.0,
    "deposit_pln": 2000.0,
    "date_agreement_from": "2025-01-01",
    "date_agreement_to": "2026-12-31"
}

TENANT_BOB = {
    "name": "Bob Johnson",
    "apartment": "apart-polanka",
    "room": "room-bigger",
    "rent_pln": 1200.0,
    "deposit_pln": 2400.0,
    "date_agreement_from": "2025-01-01",
    "date_agreement_to": "2026-12-31"
}

APARTMENT_EMPTY = {
    "key": "apart-empty",
    "name": "Empty",
    "location": "Empty 1",
    "area_m2": 50,
    "rooms": {"room-single": {"name": "Single Room", "area_m2": 25}}
}

APARTMENT_SINGLE = {
    "key": "apart-single",
    "name": "Single",
    "location": "Single 1",
    "area_m2": 50,
    "rooms": {"room-single": {"name": "Single Room", "area_m2": 25}}
}

TENANT_ALICE = {
    "name": "Alice Brown",
    "apartment": "apart-single",
    "room": "room-single",
    "rent_pln": 900.0,
    "deposit_pln": 1800.0,
    "date_agreement_from": "2025-01-01",
    "date_agreement_to": "2026-12-31"
}


@pytest.fixture
def manager_for_tenant_settlements(tmp_path):
    apartments = {
        "apart-polanka": APARTMENT_POLANKA,
        "apart-empty": APARTMENT_EMPTY
    }
    tenants = {
        "tenant-001": TENANT_JOHN,
        "tenant-002": TENANT_JANE,
        "tenant-003": TENANT_BOB
    }
    return create_manager(tmp_path, apartments, tenants, [], BILLS_POLANKA_JAN)


@pytest.fixture
def manager_single_tenant(tmp_path):
    apartments = {"apart-single": APARTMENT_SINGLE}
    tenants = {"tenant-single": TENANT_ALICE}
    return create_manager(tmp_path, apartments, tenants, [], BILLS_POLANKA_JAN)


class TestGetTenantSettlements:
    def test_tenant_settlements_multiple_tenants(self, manager_for_tenant_settlements):
        apartment_settlement = manager_for_tenant_settlements.get_apartment_settlement("apart-polanka", 2025, 1)
        tenant_settlements = manager_for_tenant_settlements.get_tenant_settlements(apartment_settlement)
        
        assert len(tenant_settlements) == 3
        for settlement in tenant_settlements:
            assert isinstance(settlement, TenantSettlement)
            assert settlement.bills_pln == 400.0
            assert settlement.rent_pln == 300.0
            assert settlement.total_due_pln == 700.0
            assert settlement.apartment_settlement == "apart-polanka"
            assert settlement.month == 1
            assert settlement.year == 2025
        
        total_bills_sum = sum(s.bills_pln for s in tenant_settlements)
        assert total_bills_sum == apartment_settlement.total_bills_pln
        
        total_rent_sum = sum(s.rent_pln for s in tenant_settlements)
        assert total_rent_sum == apartment_settlement.total_rent_pln
    
    def test_tenant_settlements_single_tenant(self, manager_single_tenant):
        apartment_settlement = manager_single_tenant.get_apartment_settlement("apart-single", 2025, 1)
        tenant_settlements = manager_single_tenant.get_tenant_settlements(apartment_settlement)
        
        assert len(tenant_settlements) == 1
        assert tenant_settlements[0].bills_pln == 1200.0
        assert tenant_settlements[0].rent_pln == 900.0
    
    def test_tenant_settlements_no_tenants(self, manager_for_tenant_settlements):
        apartment_settlement = manager_for_tenant_settlements.get_apartment_settlement("apart-empty", 2025, 1)
        tenant_settlements = manager_for_tenant_settlements.get_tenant_settlements(apartment_settlement)
        
        assert len(tenant_settlements) == 0
        assert isinstance(tenant_settlements, list)
