from triage_system import TriageSystem

if __name__ == "__main__":
    print("Initializing Multi-LLM-Agent Triage System...")
    triage_system = TriageSystem()
    triage_system.setup_data_and_agents()

    # Test with sample incidents
    sample_incidents = [
        "Server outage in datacenter A, error code 503, high network latency.",
        "Application unresponsive, database connection failed.",
        "Suspicious network activity detected: multiple failed login attempts from unknown IP.",
        "Unusual traffic spike, potential DoS attack on web server.",
        "New malware detected on endpoint, requires immediate isolation."
    ]

    print("\n--- Starting Incident Triage Process ---")
    for incident in sample_incidents:
        result = triage_system.triage_incident(incident)
        print(f"\nFinal Result for \'{incident}\': {result}")
    print("\n--- Incident Triage Process Completed ---")


