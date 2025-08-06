from llm_agent import LLMAgent

class TeamManagerAgent(LLMAgent):
    def __init__(self, team_name):
        super().__init__(f"Team Manager ({team_name})", f"team manager for {team_name}")
        self.team_name = team_name

    def enrich_and_vote(self, incident_details, monitoring_data=None):
        # Placeholder for enriching incident and voting logic
        monitoring_str = monitoring_data if monitoring_data else "N/A"
        prompt = f"As the team manager for {self.team_name}, review the following incident details. If necessary, use the provided monitoring data to enrich the incident. Then, decide whether your team can accept this incident. Respond with \"ACCEPT\" or \"REJECT\" and a brief justification.\n\nIncident Details: {incident_details}\n\nMonitoring Data: {monitoring_str}\n\nDecision and Justification:"
        return self._call_llm(prompt)

class CollaborativeDecisionGroup:
    def __init__(self, team_manager_agents):
        self.team_manager_agents = team_manager_agents

    def conduct_negotiation_and_vote(self, incident_details, max_iterations=3):
        accepted_by = []
        rejected_by = []
        discussion_log = []

        for iteration in range(max_iterations):
            current_round_votes = {}
            for agent in self.team_manager_agents:
                vote_result = agent.enrich_and_vote(incident_details)
                current_round_votes[agent.team_name] = vote_result
                discussion_log.append(f"Iteration {iteration + 1}, {agent.team_name} voted: {vote_result}")

            accepted_by = [team for team, vote in current_round_votes.items() if "ACCEPT" in vote.upper()]
            rejected_by = [team for team, vote in current_round_votes.items() if "REJECT" in vote.upper()]

            if accepted_by:
                return {"status": "ACCEPTED", "assigned_team": accepted_by[0], "discussion_log": discussion_log}
            elif iteration < max_iterations - 1: # If no one accepted, and not last iteration, try to facilitate further discussion
                # This is where more sophisticated negotiation logic would go, e.g., LLM-driven discussion prompts
                incident_details += "\n\nNo team accepted in the last round. Please reconsider or provide reasons for rejection to facilitate further discussion."

        return {"status": "REJECTED_NO_CONSENSUS", "discussion_log": discussion_log}


