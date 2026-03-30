from src.models import Apartment, Bill, Parameters, Tenant, Transfer, ApartmentSettlement, TenantSettlement


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True
    
    def get_apartment_costs(self, apartment_key: str, year: int, month: int) -> float:
        if apartment_key not in self.apartments:
            return 0.0
        
        total_cost = sum(
            bill.amount_pln 
            for bill in self.bills 
            if bill.apartment == apartment_key 
            and bill.settlement_year == year 
            and bill.settlement_month == month
        )
        
        return total_cost
    
    def get_apartment_settlement(self, apartment_key: str, year: int, month: int):

        if apartment_key not in self.apartments:
            return None
        
        total_bills = sum(
            bill.amount_pln 
            for bill in self.bills 
            if bill.apartment == apartment_key 
            and bill.settlement_year == year 
            and bill.settlement_month == month
        )
        
        total_rent = sum(
            bill.amount_pln 
            for bill in self.bills 
            if bill.apartment == apartment_key 
            and bill.settlement_year == year 
            and bill.settlement_month == month 
            and bill.type == 'rent'
        )
        
        tenants_in_apartment = [
            tenant for tenant in self.tenants.values() 
            if tenant.apartment == apartment_key
        ]
        
        total_transfers = sum(
            transfer.amount_pln 
            for transfer in self.transfers 
            if transfer.settlement_year == year 
            and transfer.settlement_month == month 
            and transfer.tenant in [t.name for t in tenants_in_apartment]
        )
        
        balance = total_transfers - total_bills
        
        settlement = ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=total_rent,
            total_bills_pln=total_bills,
            total_due_pln=balance
        )
        
        return settlement
    
    def get_tenant_settlements(self, apartment_settlement: ApartmentSettlement):
        apartment_key = apartment_settlement.apartment
        
        tenants_in_apartment = [
            tenant for tenant in self.tenants.values() 
            if tenant.apartment == apartment_key
        ]
        
        if not tenants_in_apartment:
            return []
        
        tenant_count = len(tenants_in_apartment)
        
        bills_per_tenant = apartment_settlement.total_bills_pln / tenant_count
        rent_per_tenant = apartment_settlement.total_rent_pln / tenant_count
        total_due_per_tenant = bills_per_tenant + rent_per_tenant
        
        tenant_settlements = []
        for tenant in tenants_in_apartment:
            settlement = TenantSettlement(
                tenant=tenant.name,
                apartment_settlement=apartment_key,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=rent_per_tenant,
                bills_pln=bills_per_tenant,
                total_due_pln=total_due_per_tenant,
                balance_pln=0.0  # Przelewy
            )
            tenant_settlements.append(settlement)
        
        return tenant_settlements