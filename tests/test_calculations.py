import unittest
from dataclasses import replace

from financewebapp.calculations import (
    HousingScenario,
    amortize,
    monthly_payment,
    project_housing,
    project_retirement,
)


class LoanTests(unittest.TestCase):
    def test_zero_interest_and_capped_final_payment(self):
        rows = amortize(1_200, 0, 12, extra=140)
        self.assertEqual(monthly_payment(1_200, 0, 12), 100)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[-1].balance, 0)
        self.assertEqual(rows[-1].cumulative_interest, 0)
        self.assertEqual(sum(row.payment for row in rows), 1_200)
        self.assertEqual(amortize(1_200, 0, 12, extra=10_000)[0].payment, 1_200)

    def test_extra_reduces_interest_and_term(self):
        base = amortize(280_000, 3.5, 300)
        accelerated = amortize(280_000, 3.5, 300, 200)
        self.assertEqual(len(base), 300)
        self.assertEqual(base[-1].balance, 0)
        self.assertLess(len(accelerated), len(base))
        self.assertLess(accelerated[-1].cumulative_interest, base[-1].cumulative_interest)
        self.assertAlmostEqual(sum(row.principal for row in accelerated), 280_000)


class HousingTests(unittest.TestCase):
    scenario = HousingScenario(
        years=2, savings=12_000, budget=1_000, rent=500, price=12_000,
        down_payment_percent=0, purchase_cost_percent=0, maintenance=0,
        mortgage_rate=0, mortgage_years=1, investment_growth=0, property_growth=0, inflation=0,
    )

    def test_rent_and_buy_share_a_budget_through_mortgage_payoff(self):
        initial, first, second = project_housing(self.scenario)
        self.assertEqual(initial.rent_net_worth, 12_000)
        self.assertEqual(initial.buy_net_worth, 12_000)
        self.assertEqual(first.rent_net_worth, 18_000)
        self.assertEqual(first.buy_net_worth, 24_000)
        self.assertEqual(second.rent_net_worth, 24_000)
        self.assertEqual(second.buy_net_worth, 36_000)

    def test_upfront_cost_reduces_real_and_nominal_starting_wealth(self):
        scenario = replace(self.scenario, down_payment_percent=100, savings=13_200,
                           purchase_cost_percent=10, inflation=2)
        first, *_, end = project_housing(scenario)
        self.assertAlmostEqual(first.buy_net_worth, 12_000)
        self.assertEqual(first.buy_net_worth, first.buy_real)
        self.assertAlmostEqual(end.buy_real, end.buy_net_worth / 1.02**2)

    def test_unaffordable_scenario_is_rejected(self):
        with self.assertRaises(ValueError):
            project_housing(replace(self.scenario, budget=999))
        with self.assertRaises(ValueError):
            project_housing(replace(self.scenario, savings=0, down_payment_percent=20))


class RetirementTests(unittest.TestCase):
    def test_contributions_and_purchasing_power(self):
        start, end = project_retirement(64, 65, 1_000, 100, 500, 0, 0, 2)
        self.assertEqual(start.real, 1_000)
        self.assertEqual(end.invested, 2_700)
        self.assertEqual(end.contributed, 2_700)
        self.assertAlmostEqual(end.real, 2_700 / 1.02)

    def test_effective_annual_return_and_simplified_tax(self):
        end = project_retirement(64, 65, 100, 0, 0, 10, 20, 0)[-1]
        self.assertAlmostEqual(end.invested, 108)
        loss = project_retirement(64, 65, 100, 0, 0, -10, 20, 0)[-1]
        self.assertAlmostEqual(loss.invested, 90)

    def test_retirement_age_must_be_in_the_future(self):
        with self.assertRaises(ValueError):
            project_retirement(65, 65, 1_000, 100, 0, 3, 0, 0)
