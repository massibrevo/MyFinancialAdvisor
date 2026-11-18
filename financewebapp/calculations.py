"""Deterministic financial projections. Currency values are in euro."""

from dataclasses import dataclass
from math import expm1, log1p


def monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """Payment for a fixed-rate loan with a nominal annual interest rate."""
    if principal < 0 or annual_rate < 0 or months < 1:
        raise ValueError("Loan terms must be non-negative and duration must be positive.")
    rate = annual_rate / 1200
    if rate == 0:
        return principal / months
    return principal * rate / -expm1(-months * log1p(rate))


@dataclass(frozen=True)
class LoanMonth:
    month: int
    payment: float
    principal: float
    interest: float
    balance: float
    cumulative_interest: float


def amortize(
    principal: float, annual_rate: float, months: int, extra: float = 0
) -> list[LoanMonth]:
    payment = monthly_payment(principal, annual_rate, months)
    if extra < 0:
        raise ValueError("Extra payment must be non-negative.")
    balance = principal
    cumulative_interest = 0.0
    rows = []
    for month in range(1, months + 1):
        if balance == 0:
            break
        interest = balance * annual_rate / 1200
        repaid = min(balance, payment + extra - interest)
        if month == months or balance - repaid < 1e-8:
            repaid = balance
        balance -= repaid
        cumulative_interest += interest
        rows.append(LoanMonth(month, repaid + interest, repaid, interest, balance, cumulative_interest))
    return rows


def monthly_growth(annual_percent: float) -> float:
    """Convert an effective annual growth rate to a monthly rate."""
    if annual_percent <= -100:
        raise ValueError("Growth rate must be above -100%.")
    return expm1(log1p(annual_percent / 100) / 12)


@dataclass(frozen=True)
class HousingScenario:
    years: int
    savings: float
    budget: float
    rent: float
    price: float
    down_payment_percent: float
    purchase_cost_percent: float
    maintenance: float
    mortgage_rate: float
    mortgage_years: int
    investment_growth: float
    property_growth: float
    inflation: float

    @property
    def down_payment(self) -> float:
        return self.price * self.down_payment_percent / 100

    @property
    def upfront_cost(self) -> float:
        return self.down_payment + self.price * self.purchase_cost_percent / 100

    @property
    def mortgage(self) -> float:
        return self.price - self.down_payment


@dataclass(frozen=True)
class HousingYear:
    year: int
    rent_net_worth: float
    buy_net_worth: float
    buy_home_equity: float
    rent_real: float
    buy_real: float


def project_housing(scenario: HousingScenario) -> list[HousingYear]:
    s = scenario
    payment = monthly_payment(s.mortgage, s.mortgage_rate, s.mortgage_years * 12)
    if s.savings < s.upfront_cost:
        raise ValueError("Il capitale iniziale deve coprire anticipo e spese di acquisto.")
    if s.budget < max(s.rent, payment + s.maintenance):
        raise ValueError("Il budget mensile deve coprire il costo abitativo di entrambe le alternative.")

    rent_fund = s.savings
    buy_fund = s.savings - s.upfront_cost
    investment_rate = monthly_growth(s.investment_growth)
    mortgage = amortize(s.mortgage, s.mortgage_rate, s.mortgage_years * 12)
    rows = [HousingYear(0, rent_fund, buy_fund + s.down_payment, s.down_payment,
                        rent_fund, buy_fund + s.down_payment)]

    for month in range(1, s.years * 12 + 1):
        installment = mortgage[month - 1] if month <= len(mortgage) else None
        rent_fund = rent_fund * (1 + investment_rate) + s.budget - s.rent
        buy_fund = buy_fund * (1 + investment_rate) + s.budget - s.maintenance
        if installment:
            buy_fund -= installment.payment
        if month % 12 == 0:
            year = month // 12
            equity = s.price * (1 + s.property_growth / 100) ** year
            if installment:
                equity -= installment.balance
            deflator = (1 + s.inflation / 100) ** year
            rows.append(HousingYear(year, rent_fund, buy_fund + equity, equity,
                                    rent_fund / deflator, (buy_fund + equity) / deflator))
    return rows


@dataclass(frozen=True)
class RetirementYear:
    age: int
    invested: float
    contributed: float
    real: float


def project_retirement(
    age: int,
    target_age: int,
    initial: float,
    monthly: float,
    lump_sum: float,
    annual_return: float,
    return_tax: float,
    inflation: float,
) -> list[RetirementYear]:
    if target_age <= age:
        raise ValueError("L’età di pensionamento deve essere superiore a quella attuale.")
    net_return = annual_return - max(0, annual_return) * return_tax / 100
    growth = monthly_growth(net_return)
    capital = initial
    rows = [RetirementYear(age, capital, initial, capital)]
    for year in range(1, target_age - age + 1):
        for _ in range(12):
            capital = capital * (1 + growth) + monthly
        capital += lump_sum
        contributed = initial + year * (12 * monthly + lump_sum)
        deflator = (1 + inflation / 100) ** year
        rows.append(RetirementYear(age + year, capital, contributed, capital / deflator))
    return rows
