
from agents import (
    UtilizationAgent,
    DeliveryRiskAgent,
    CostMarginAgent,
    HRRiskAgent
)
from llm_groq import explain_insight


class Orchestrator:
    def __init__(self):
        self.util_agent = UtilizationAgent()
        self.risk_agent = DeliveryRiskAgent()
        self.cost_agent = CostMarginAgent()
        self.hr_agent = HRRiskAgent()

    def analyze(
        self,
        util_df,
        risk_df,
        cost_df,
        hr_df,
        use_llm=False
    ):
        """
        Central orchestration of all analytical agents.
        """

        low_util = self.util_agent.run(util_df)
        risky_projects = self.risk_agent.run(risk_df)
        loss_projects = self.cost_agent.run(cost_df)
        hr_risks = self.hr_agent.run(hr_df)

        explanation = None
        if use_llm:
            prompt = f"""
            Enterprise Delivery Intelligence Summary:

            Underutilized Employees: {len(low_util)}
            High Delivery Risk Projects: {len(risky_projects)}
            Loss-Making Projects: {len(loss_projects)}
            HR Risk Employees: {len(hr_risks)}

            Provide:
            - Executive insights
            - Root causes
            - Actionable recommendations
            """

            explanation = explain_insight(prompt)

        return {
            "low_util": low_util,
            "risk_projects": risky_projects,
            "loss_projects": loss_projects,
            "hr_risks": hr_risks,
            "explanation": explanation
        }

