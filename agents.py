class UtilizationAgent:
    def run(self, df):
        return df[df["utilization_pct"] < 60]


class DeliveryRiskAgent:
    def run(self, df):
        return df[df["risk_flag"] == 1]


class CostMarginAgent:
    def run(self, df):
        return df[df["margin"] < 0]


class HRRiskAgent:
    def run(self, df):
        return df[df["hr_risk"] == 1]
