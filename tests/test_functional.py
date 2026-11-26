import pytest
from src.manager import Manager
from src.models import Parameters, Apartment, Room, Tenant, Bill, Transfer


def test_settlement_tenants_sum_equals_apartment_costs():
    """Zasada integralności danych: suma obciążeń lokatorów musi być równa kosztom mieszkania."""
    manager = Manager(Parameters())

    manager.apartments = {
        "A1": Apartment(
            key="A1",
            name="Apartament A1",
            location="Poznań",
            area_m2=60.0,
            rooms={"R1": Room(name="Pokój 1", area_m2=20.0)}
        )
    }
    manager.tenants = {
        "T1": Tenant(name="Jan Kowalski", apartment="A1", room="R1", rent_pln=1500.0, deposit_pln=1500.0, date_agreement_from="2024-01-01", date_agreement_to="2024-12-31"),
        "T2": Tenant(name="Anna Nowak", apartment="A1", room="R1", rent_pln=1500.0, deposit_pln=1500.0, date_agreement_from="2024-01-01", date_agreement_to="2024-12-31"),
        "T3": Tenant(name="Piotr Zieliński", apartment="A1", room="R1", rent_pln=1500.0, deposit_pln=1500.0, date_agreement_from="2024-01-01", date_agreement_to="2024-12-31"),
    }
    manager.bills = [
        Bill(amount_pln=650.0, date_due="2024-01-15", apartment="A1", settlement_year=2024, settlement_month=1, type="electricity"),
        Bill(amount_pln=350.0, date_due="2024-01-20", apartment="A1", settlement_year=2024, settlement_month=1, type="water"),
    ]

    expected_costs = manager.get_apartment_costs("A1", 2024, 1)
    assert expected_costs == 1000.0

    settlement = manager.get_settlement("A1", 2024, 1)
    assert settlement is not None
    assert settlement.total_due_pln == 1000.0

    tenant_settlements = manager.create_tenants_settlements(settlement)
    assert len(tenant_settlements) == 3

    total_tenants_due = sum(ts.total_due_pln for ts in tenant_settlements)
    assert pytest.approx(total_tenants_due, rel=1e-9) == expected_costs


def test_get_tax_calculation():
    """Test funkcjonalny sprawdzający wyliczenie zryczałtowanego podatku od przychodów w danym miesiącu."""
    manager = Manager(Parameters())
    manager.transfers = [
        Transfer(amount_pln=2000.0, date="2024-01-05", settlement_year=2024, settlement_month=1, tenant="T1"),
        Transfer(amount_pln=1550.0, date="2024-01-10", settlement_year=2024, settlement_month=1, tenant="T2"),
        Transfer(amount_pln=3000.0, date="2024-02-05", settlement_year=2024, settlement_month=2, tenant="T1"),
    ]

    tax = manager.get_tax(year=2024, month=1, tax_rate=0.085)
    assert tax == 302