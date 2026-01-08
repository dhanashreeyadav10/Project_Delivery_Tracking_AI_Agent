class UtilizationAgent:
    def run(self, util_df):
        return util_df[util_df["utilization_pct"] < 60]


class DeliveryRiskAgent:
    def run(self, risk_df):
        return risk_df[risk_df["risk_flag"] == 1]


class CostMarginAgent:
    def run(self, cost_df):
        return cost_df[cost_df["margin"] < 0]


class HRRiskAgent:
    def run(self, hr_df):
        return hr_df[hr_df["hr_risk"] == 1]
