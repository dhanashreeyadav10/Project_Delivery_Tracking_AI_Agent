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

    def analyze(self, util_df, risk_df, cost_df, hr_df, use_llm=False):
        low_util = self.util_agent.run(util_df)
        risky_projects = self.risk_agent.run(risk_df)
        loss_projects = self.cost_agent.run(cost_df)
        hr_risks = self.hr_agent.run(hr_df)

        # -----------------------------
        # DATA-DRIVEN EXECUTIVE SUMMARY
        # -----------------------------
        base_summary = f"""
Key Delivery Intelligence Insights:

• Underutilized Employees: {len(low_util)}
• Delivery Risk Projects: {len(risky_projects)}
• Loss-Making Projects: {len(loss_projects)}
• HR Risk Employees: {len(hr_risks)}

Recommended Actions:
• Optimize bench utilization through reallocation
• Prioritize high-risk Jira items
• Review pricing and cost overruns
• Engage HR for early attrition signals
        """.strip()

        explanation = base_summary

        # -----------------------------
        # OPTIONAL LLM ENHANCEMENT
        # -----------------------------
        if use_llm:
            enhanced = explain_insight(
                f"""
Rewrite the following executive summary in professional consulting tone:

{base_summary}
"""
            )
            if enhanced:
                explanation = enhanced

        return {
            "low_util": low_util,
            "risk_projects": risky_projects,
            "loss_projects": loss_projects,
            "hr_risks": hr_risks,
            "explanation": explanation
        }
