from agents import *
from llm_groq import explain_insight

class Orchestrator:
    def __init__(self):
        self.util = UtilizationAgent()
        self.risk = DeliveryRiskAgent()
        self.cost = CostMarginAgent()
        self.hr = HRRiskAgent()

    def analyze(self, util_df, risk_df, cost_df, hr_df, use_llm=False):
        low = self.util.run(util_df)
        risky = self.risk.run(risk_df)
        loss = self.cost.run(cost_df)
        hr = self.hr.run(hr_df)

        explanation = None
        if use_llm:
            explanation = explain_insight(
                f"""
                Underutilized Employees: {len(low)}
                Risky Projects: {len(risky)}
                Loss Projects: {len(loss)}
                HR Risk Employees: {len(hr)}
                """
            )

        return {
            "low_util": low,
            "risk_projects": risky,
            "loss_projects": loss,
            "hr_risks": hr,
            "explanation": explanation
        }
