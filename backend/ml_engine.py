    def _calculate_pricing(self, pd_score: float, credit_amount: float, duration_months: int):
        if pd_score < 0.06:
            tier = "Prime Preferred"
            apr = 5.5 + (pd_score * 100 * 0.25)
        elif pd_score < 0.12:
            tier = "Prime Standard"
            apr = 7.0 + (pd_score * 100 * 0.28)
        else:
            tier = "Near-Prime"
            apr = 10.5 + (pd_score * 100 * 0.25)

        r = (apr / 100) / 12
        n = duration_months
        P = credit_amount

        if r == 0:
            monthly_payment = P / n
        else:
            monthly_payment = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

        total_interest = (monthly_payment * n) - P

        return {
            "risk_tier": tier,
            "offered_apr": round(apr, 2),
            "monthly_installment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2)
        }