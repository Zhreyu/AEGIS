"""
AEGIS - Advanced Security Triage System

Main entry point for the AEGIS security incident triage system.
This script demonstrates the complete triage workflow using the modular architecture.
"""

import sys
import os
from typing import List, Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import TriageSystem
from src.utils import setup_logger, format_incident_result, format_system_status


def main():
    """Main function to run the AEGIS triage system."""
    # Set up logging
    logger = setup_logger("aegis_main")
    logger.info("Initializing AEGIS Multi-LLM-Agent Triage System...")
    
    try:
        # Initialize the triage system
        triage_system = TriageSystem()
        triage_system.setup_data_and_agents()
        
        # Display system status
        status = triage_system.get_system_status()
        print("\n" + "="*50)
        print(format_system_status(status))
        print("="*50)
        
        # Test with sample incidents
        sample_incidents = [
            "Server outage in datacenter A, error code 503, high network latency.",
            "Application unresponsive, database connection failed.",
            "Suspicious network activity detected: multiple failed login attempts from unknown IP.",
            "Unusual traffic spike, potential DoS attack on web server.",
            "New malware detected on endpoint, requires immediate isolation."
        ]
        
        print("\n--- Starting Incident Triage Process ---")
        results = []
        
        for i, incident in enumerate(sample_incidents, 1):
            print(f"\n{'='*60}")
            print(f"PROCESSING INCIDENT {i}/{len(sample_incidents)}")
            print(f"{'='*60}")
            
            try:
                result = triage_system.triage_incident(incident)
                results.append(result)
                
                # Display formatted result
                print("\n" + format_incident_result(result))
                
            except Exception as e:
                logger.error(f"Error processing incident {i}: {e}")
                print(f"Error processing incident: {e}")
        
        print(f"\n{'='*60}")
        print("--- Incident Triage Process Completed ---")
        print(f"Successfully processed {len(results)} incidents")
        print(f"{'='*60}")
        
        # Display summary
        display_summary(results)
        
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


def display_summary(results: List[Dict[str, Any]]) -> None:
    """
    Display a summary of the triage results.
    
    Args:
        results (List[Dict[str, Any]]): List of triage results
    """
    print("\n--- TRIAGE SUMMARY ---")
    
    accepted_count = 0
    rejected_count = 0
    
    for i, result in enumerate(results, 1):
        outcome = result.get('triage_outcome', {})
        status = outcome.get('status', 'UNKNOWN')
        
        if status == 'ACCEPTED':
            accepted_count += 1
            assigned_team = outcome.get('assigned_team', 'Unknown')
            print(f"Incident {i}: ACCEPTED by {assigned_team}")
        else:
            rejected_count += 1
            print(f"Incident {i}: {status}")
    
    print(f"\nTotal Incidents: {len(results)}")
    print(f"Accepted: {accepted_count}")
    print(f"Rejected: {rejected_count}")
    print(f"Success Rate: {(accepted_count/len(results)*100):.1f}%")


def run_batch_triage(incidents: List[str]) -> List[Dict[str, Any]]:
    """
    Run batch triage on a list of incidents.
    
    Args:
        incidents (List[str]): List of incident descriptions
        
    Returns:
        List[Dict[str, Any]]: List of triage results
    """
    triage_system = TriageSystem()
    triage_system.setup_data_and_agents()
    
    return triage_system.batch_triage_incidents(incidents)


if __name__ == "__main__":
    main()