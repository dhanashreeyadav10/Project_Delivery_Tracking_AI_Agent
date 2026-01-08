from agents import *
from llm_groq import explain_insight


class Orchestrator:
    def __init__(self):
        self.util_agent = UtilizationAgent()
        self.risk_agent = DeliveryRiskAgent()
        self.cost_agent = CostMarginAgent()
        self.hr_agent = HRRiskAgent()

    def analyze(self, util_df, risk_df, cost_df, hr_df, use_llm=False):
        low_util = self.util_agent.run(util_df)
        risky = self.risk_agent.run(risk_df)
        loss = self.cost_agent.run(cost_df)
        hr = self.hr_agent.run(hr_df)

        explanation = None
        if use_llm:
            explanation = explain_insight(
                f"""
                Underutilized Employees: {len(low_util)}
                Risky Projects: {len(risky)}
                Loss Projects: {len(loss)}
                HR Risk Employees: {len(hr)}
                Provide executive insights and recommendations.
                """
            )

        return {
            "low_util": low_util,
            "risk_projects": risky,
            "loss_projects": loss,
            "hr_risks": hr,
            "explanation": explanation
        }
