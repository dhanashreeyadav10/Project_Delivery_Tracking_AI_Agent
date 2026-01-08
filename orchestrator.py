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

        explanation = None

        # ------------------------------
        # EXECUTIVE SUMMARY (LLM OPTIONAL)
        # ------------------------------
        if use_llm:
            prompt = f"""
            You are a senior delivery executive.

            Provide a concise executive summary based on:
            - Underutilized Employees: {len(low_util)}
            - High Delivery Risk Projects: {len(risky_projects)}
            - Loss-Making Projects: {len(loss_projects)}
            - HR Risk Employees: {len(hr_risks)}

            Focus on:
            - Key risks
            - Business impact
            - Immediate leadership actions
            """

            explanation = explain_insight(prompt)

            # ✅ HARD GUARD AGAINST RAW ERRORS
            if explanation.lower().startswith("llm unavailable"):
                explanation = None

        # ------------------------------
        # FALLBACK (NO LLM / FAILURE)
        # ------------------------------
        if explanation is None:
            explanation = f"""
            📊 **Executive Summary (Data-Driven)**

            • **Utilization**: {len(low_util)} employees are underutilized, indicating potential bench cost risk.
            • **Delivery Risk**: {len(risky_projects)} projects show delivery risk due to open or high-priority issues.
            • **Financial Health**: {len(loss_projects)} projects are currently loss-making or at margin risk.
            • **People Risk**: {len(hr_risks)} employees exhibit early HR risk indicators.

            **Recommended Leadership Actions**
            • Rebalance capacity from underutilized resources.
            • Prioritize resolution of high-risk delivery projects.
            • Initiate financial reviews for loss-making engagements.
            • Proactively engage employees showing HR risk signals.
            """

        return {
            "low_util": low_util,
            "risk_projects": risky_projects,
            "loss_projects": loss_projects,
            "hr_risks": hr_risks,
            "explanation": explanation
        }
