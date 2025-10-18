"""
AEGIS - Advanced Security Triage System

Main entry point for the AEGIS security incident triage system.
This script runs comprehensive testing on all datasets and generates detailed metrics.
"""

import sys
import os
import json
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import TriageSystem
from src.utils import setup_logger, format_incident_result, format_system_status


def main():
    """Main function to run comprehensive AEGIS triage testing."""
    # Set up logging
    logger = setup_logger("aegis_main")
    logger.info("Initializing AEGIS Multi-LLM-Agent Triage System for comprehensive testing...")
    
    try:
        # Initialize the triage system
        print("🚀 Initializing AEGIS Triage System...")
        triage_system = TriageSystem()
        triage_system.setup_data_and_agents()
        
        # Display system status
        status = triage_system.get_system_status()
        print("\n" + "="*50)
        print(format_system_status(status))
        print("="*50)
        
        # Get incidents from GUIDE dataset only
        print("\n📊 Loading incident data from GUIDE dataset...")
        guide_incidents = triage_system.data_manager.get_guide_data()
        
        print(f"  📁 GUIDE dataset: {len(guide_incidents)} incidents")
        
        # Process GUIDE incidents
        all_incidents = []
        incident_metadata = []  # Store metadata for each incident
        
        for i, incident in enumerate(guide_incidents):
            all_incidents.append(incident.get("description", ""))
            incident_metadata.append({
                "index": i,
                "source": "GUIDE",
                "id": incident.get("id", f"G{i}"),
                "ground_truth_team": incident.get("ground_truth_team", "Unknown"),
                "description": incident.get("description", "")
            })
        
        print(f"  📊 Total incidents to process: {len(all_incidents)}")
        
        # Run comprehensive batch triage
        print(f"\n🔄 Starting comprehensive triage process...")
        start_time = time.time()
        
        results = triage_system.batch_triage_incidents(all_incidents)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️  Processing completed in {processing_time:.2f} seconds")
        print(f"📈 Average time per incident: {processing_time/len(all_incidents):.2f} seconds")
        
        # Generate comprehensive metrics
        metrics = generate_comprehensive_metrics(results, incident_metadata, processing_time)
        
        # Save metrics to file
        save_metrics_to_file(metrics, results, incident_metadata)
        
        # Display summary
        display_comprehensive_summary(metrics, results)
        
    except Exception as e:
        logger.error(f"Fatal error in main execution: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


def generate_comprehensive_metrics(results: List[Dict[str, Any]], 
                                 incident_metadata: List[Dict[str, Any]], 
                                 processing_time: float) -> Dict[str, Any]:
    """
    Generate comprehensive metrics from triage results.
    
    Args:
        results (List[Dict[str, Any]]): Triage results
        incident_metadata (List[Dict[str, Any]]): Incident metadata
        processing_time (float): Total processing time
        
    Returns:
        Dict[str, Any]: Comprehensive metrics
    """
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "total_incidents": len(results),
        "processing_time_seconds": processing_time,
        "average_time_per_incident": processing_time / len(results) if results else 0,
        "success_metrics": {},
        "team_metrics": {},
        "dataset_metrics": {},
        "accuracy_metrics": {},
        "performance_metrics": {}
    }
    
    # Success metrics
    accepted_count = 0
    rejected_count = 0
    error_count = 0
    
    for result in results:
        outcome = result.get('triage_outcome', {})
        status = outcome.get('status', 'UNKNOWN')
        
        if status == 'ACCEPTED':
            accepted_count += 1
        elif status in ['REJECTED_NO_CONSENSUS', 'REJECTED_NO_CANDIDATE_TEAMS']:
            rejected_count += 1
        else:
            error_count += 1
    
    metrics["success_metrics"] = {
        "accepted": accepted_count,
        "rejected": rejected_count,
        "errors": error_count,
        "success_rate": (accepted_count / len(results) * 100) if results else 0,
        "rejection_rate": (rejected_count / len(results) * 100) if results else 0,
        "error_rate": (error_count / len(results) * 100) if results else 0
    }
    
    # Team assignment metrics
    team_assignments = {}
    for result in results:
        outcome = result.get('triage_outcome', {})
        if outcome.get('status') == 'ACCEPTED':
            team = outcome.get('assigned_team', 'Unknown')
            team_assignments[team] = team_assignments.get(team, 0) + 1
    
    metrics["team_metrics"] = {
        "team_assignments": team_assignments,
        "unique_teams_assigned": len(team_assignments),
        "most_assigned_team": max(team_assignments.items(), key=lambda x: x[1])[0] if team_assignments else None
    }
    
    # Dataset-specific metrics (GUIDE only)
    guide_results = []
    
    for i, (result, metadata) in enumerate(zip(results, incident_metadata)):
        if metadata["source"] == "GUIDE":
            guide_results.append(result)
    
    metrics["dataset_metrics"] = {
        "guide_incidents": len(guide_results),
        "guide_success_rate": calculate_success_rate(guide_results)
    }
    
    # Accuracy metrics (if ground truth is available)
    correct_assignments = 0
    total_with_ground_truth = 0
    
    for result, metadata in zip(results, incident_metadata):
        outcome = result.get('triage_outcome', {})
        if outcome.get('status') == 'ACCEPTED':
            assigned_team = outcome.get('assigned_team', '')
            ground_truth_team = metadata.get('ground_truth_team', '')
            
            if ground_truth_team and ground_truth_team != 'Unknown':
                total_with_ground_truth += 1
                if assigned_team == ground_truth_team:
                    correct_assignments += 1
    
    metrics["accuracy_metrics"] = {
        "correct_assignments": correct_assignments,
        "total_with_ground_truth": total_with_ground_truth,
        "accuracy_rate": (correct_assignments / total_with_ground_truth * 100) if total_with_ground_truth > 0 else 0
    }
    
    # Performance metrics
    metrics["performance_metrics"] = {
        "incidents_per_second": len(results) / processing_time if processing_time > 0 else 0,
        "average_processing_time": processing_time / len(results) if results else 0,
        "total_processing_time": processing_time
    }
    
    return metrics


def calculate_success_rate(results: List[Dict[str, Any]]) -> float:
    """Calculate success rate for a list of results."""
    if not results:
        return 0.0
    
    accepted = sum(1 for result in results 
                  if result.get('triage_outcome', {}).get('status') == 'ACCEPTED')
    return (accepted / len(results)) * 100


def save_metrics_to_file(metrics: Dict[str, Any], 
                         results: List[Dict[str, Any]], 
                         incident_metadata: List[Dict[str, Any]]) -> None:
    """
    Save comprehensive metrics, results, and visualizations to files.
    
    Args:
        metrics (Dict[str, Any]): Generated metrics
        results (List[Dict[str, Any]]): Triage results
        incident_metadata (List[Dict[str, Any]]): Incident metadata
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create results directory
    os.makedirs("results", exist_ok=True)
    
    # Save metrics
    metrics_file = f"results/metrics_{timestamp}.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"📊 Metrics saved to: {metrics_file}")
    
    # Save detailed results
    detailed_results = []
    for i, (result, metadata) in enumerate(zip(results, incident_metadata)):
        detailed_results.append({
            "incident_index": i,
            "incident_id": metadata.get("id", f"incident_{i}"),
            "source": metadata.get("source", "Unknown"),
            "ground_truth_team": metadata.get("ground_truth_team", "Unknown"),
            "description": metadata.get("description", "")[:100] + "..." if len(metadata.get("description", "")) > 100 else metadata.get("description", ""),
            "triage_result": result
        })
    
    results_file = f"results/detailed_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    print(f"📋 Detailed results saved to: {results_file}")
    
    # Save summary report
    summary_file = f"results/summary_report_{timestamp}.txt"
    with open(summary_file, 'w') as f:
        f.write("AEGIS Triage System - Comprehensive Test Results\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Incidents: {metrics['total_incidents']}\n")
        f.write(f"Processing Time: {metrics['processing_time_seconds']:.2f} seconds\n")
        f.write(f"Success Rate: {metrics['success_metrics']['success_rate']:.1f}%\n")
        f.write(f"Accuracy Rate: {metrics['accuracy_metrics']['accuracy_rate']:.1f}%\n")
        f.write(f"Average Time per Incident: {metrics['average_time_per_incident']:.2f} seconds\n")
        f.write(f"Incidents per Second: {metrics['performance_metrics']['incidents_per_second']:.2f}\n\n")
        
        f.write("Team Assignment Distribution:\n")
        for team, count in metrics['team_metrics']['team_assignments'].items():
            f.write(f"  {team}: {count} incidents\n")
        
        f.write(f"\nDataset Performance:\n")
        f.write(f"  GUIDE Success Rate: {metrics['dataset_metrics']['guide_success_rate']:.1f}%\n")
    
    print(f"📄 Summary report saved to: {summary_file}")
    
    # Generate and save visualizations
    generate_visualizations(metrics, results, incident_metadata, timestamp)


def generate_visualizations(metrics: Dict[str, Any], 
                           results: List[Dict[str, Any]], 
                           incident_metadata: List[Dict[str, Any]], 
                           timestamp: str) -> None:
    """
    Generate comprehensive visualizations and save them to the results folder.
    
    Args:
        metrics (Dict[str, Any]): Generated metrics
        results (List[Dict[str, Any]]): Triage results
        incident_metadata (List[Dict[str, Any]]): Incident metadata
        timestamp (str): Timestamp for file naming
    """
    print("📈 Generating visualizations...")
    
    # Set style for better-looking plots
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Success Rate Pie Chart
    ax1 = plt.subplot(3, 4, 1)
    success_metrics = metrics['success_metrics']
    labels = ['Accepted', 'Rejected', 'Errors']
    sizes = [success_metrics['accepted'], success_metrics['rejected'], success_metrics['errors']]
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Triage Success Distribution', fontsize=14, fontweight='bold')
    
    # 2. Team Assignment Bar Chart
    ax2 = plt.subplot(3, 4, 2)
    team_assignments = metrics['team_metrics']['team_assignments']
    if team_assignments:
        teams = list(team_assignments.keys())
        counts = list(team_assignments.values())
        bars = ax2.bar(teams, counts, color='#3498db')
        ax2.set_title('Team Assignment Distribution', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Teams')
        ax2.set_ylabel('Number of Incidents')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(count), ha='center', va='bottom')
    
    # 3. GUIDE Dataset Performance
    ax3 = plt.subplot(3, 4, 3)
    dataset_metrics = metrics['dataset_metrics']
    success_rate = dataset_metrics['guide_success_rate']
    incident_count = dataset_metrics['guide_incidents']
    
    categories = ['Success Rate (%)', 'Incident Count']
    values = [success_rate, incident_count]
    colors = ['#9b59b6', '#e67e22']
    
    bars = ax3.bar(categories, values, color=colors)
    ax3.set_title('GUIDE Dataset Performance', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Value')
    
    # Add value labels
    for bar, value in zip(bars, values):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{value:.1f}', ha='center', va='bottom')
    
    # 4. Processing Time Analysis
    ax4 = plt.subplot(3, 4, 4)
    performance_metrics = metrics['performance_metrics']
    categories = ['Total Time (s)', 'Avg Time/Incident (s)', 'Incidents/Second']
    values = [
        performance_metrics['total_processing_time'],
        performance_metrics['average_processing_time'],
        performance_metrics['incidents_per_second']
    ]
    
    bars = ax4.bar(categories, values, color=['#e74c3c', '#f39c12', '#2ecc71'])
    ax4.set_title('Processing Performance Metrics', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Value')
    ax4.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{value:.2f}', ha='center', va='bottom')
    
    # 5. Accuracy Analysis (if ground truth available)
    ax5 = plt.subplot(3, 4, 5)
    accuracy_metrics = metrics['accuracy_metrics']
    if accuracy_metrics['total_with_ground_truth'] > 0:
        correct = accuracy_metrics['correct_assignments']
        incorrect = accuracy_metrics['total_with_ground_truth'] - correct
        
        labels = ['Correct', 'Incorrect']
        sizes = [correct, incorrect]
        colors = ['#2ecc71', '#e74c3c']
        
        ax5.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax5.set_title(f'Accuracy Analysis\n({accuracy_metrics["total_with_ground_truth"]} incidents with ground truth)', 
                     fontsize=12, fontweight='bold')
    else:
        ax5.text(0.5, 0.5, 'No Ground Truth\nData Available', ha='center', va='center', 
                transform=ax5.transAxes, fontsize=12)
        ax5.set_title('Accuracy Analysis', fontsize=12, fontweight='bold')
    
    # 6. Timeline Analysis (if we had timestamps)
    ax6 = plt.subplot(3, 4, 6)
    # Simulate processing timeline
    incident_indices = list(range(len(results)))
    processing_times = [metrics['average_time_per_incident']] * len(results)
    
    ax6.plot(incident_indices, processing_times, color='#3498db', linewidth=2)
    ax6.set_title('Processing Time Consistency', fontsize=14, fontweight='bold')
    ax6.set_xlabel('Incident Index')
    ax6.set_ylabel('Processing Time (seconds)')
    ax6.grid(True, alpha=0.3)
    
    # 7. Error Analysis
    ax7 = plt.subplot(3, 4, 7)
    error_types = ['Accepted', 'Rejected', 'Errors']
    error_counts = [success_metrics['accepted'], success_metrics['rejected'], success_metrics['errors']]
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    
    bars = ax7.bar(error_types, error_counts, color=colors)
    ax7.set_title('Error Type Distribution', fontsize=14, fontweight='bold')
    ax7.set_ylabel('Count')
    
    # Add value labels
    for bar, count in zip(bars, error_counts):
        ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(count), ha='center', va='bottom')
    
    # 8. Performance Metrics Radar Chart
    ax8 = plt.subplot(3, 4, 8, projection='polar')
    
    # Normalize metrics for radar chart
    categories = ['Success Rate', 'Accuracy', 'Speed', 'Efficiency']
    values = [
        success_metrics['success_rate'] / 100,
        accuracy_metrics['accuracy_rate'] / 100,
        min(performance_metrics['incidents_per_second'] / 10, 1),  # Normalize to 0-1
        min(1 - (performance_metrics['average_processing_time'] / 10), 1)  # Invert time for efficiency
    ]
    
    # Complete the circle
    values += values[:1]
    angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
    angles += angles[:1]
    
    ax8.plot(angles, values, 'o-', linewidth=2, color='#9b59b6')
    ax8.fill(angles, values, alpha=0.25, color='#9b59b6')
    ax8.set_xticks(angles[:-1])
    ax8.set_xticklabels(categories)
    ax8.set_ylim(0, 1)
    ax8.set_title('Performance Radar', fontsize=12, fontweight='bold')
    
    # 9. Team Assignment Heatmap (if we have enough data)
    ax9 = plt.subplot(3, 4, 9)
    if len(team_assignments) > 1:
        # Create a simple heatmap of team assignments
        team_names = list(team_assignments.keys())
        team_counts = list(team_assignments.values())
        
        # Create a 1D heatmap
        im = ax9.imshow([team_counts], cmap='YlOrRd', aspect='auto')
        ax9.set_xticks(range(len(team_names)))
        ax9.set_xticklabels(team_names, rotation=45)
        ax9.set_yticks([0])
        ax9.set_yticklabels(['Assignments'])
        ax9.set_title('Team Assignment Heatmap', fontsize=12, fontweight='bold')
        
        # Add colorbar
        plt.colorbar(im, ax=ax9, shrink=0.8)
    else:
        ax9.text(0.5, 0.5, 'Insufficient Data\nfor Heatmap', ha='center', va='center', 
                transform=ax9.transAxes, fontsize=12)
        ax9.set_title('Team Assignment Heatmap', fontsize=12, fontweight='bold')
    
    # 10. Cumulative Success Rate
    ax10 = plt.subplot(3, 4, 10)
    cumulative_success = []
    running_total = 0
    for i, result in enumerate(results):
        if result.get('triage_outcome', {}).get('status') == 'ACCEPTED':
            running_total += 1
        cumulative_success.append((running_total / (i + 1)) * 100)
    
    ax10.plot(range(len(cumulative_success)), cumulative_success, color='#2ecc71', linewidth=2)
    ax10.set_title('Cumulative Success Rate', fontsize=12, fontweight='bold')
    ax10.set_xlabel('Incident Number')
    ax10.set_ylabel('Success Rate (%)')
    ax10.grid(True, alpha=0.3)
    
    # 11. GUIDE Dataset Success Analysis
    ax11 = plt.subplot(3, 4, 11)
    guide_data = [r for r, m in zip(results, incident_metadata) if m['source'] == 'GUIDE']
    
    guide_success = sum(1 for r in guide_data if r.get('triage_outcome', {}).get('status') == 'ACCEPTED')
    guide_failed = len(guide_data) - guide_success
    
    categories = ['Successful', 'Failed']
    counts = [guide_success, guide_failed]
    colors = ['#2ecc71', '#e74c3c']
    
    bars = ax11.bar(categories, counts, color=colors)
    ax11.set_xlabel('Outcome')
    ax11.set_ylabel('Number of Incidents')
    ax11.set_title('GUIDE Dataset Success Analysis', fontsize=12, fontweight='bold')
    
    # Add value labels
    for bar, count in zip(bars, counts):
        ax11.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                str(count), ha='center', va='bottom')
    
    # 12. Summary Statistics
    ax12 = plt.subplot(3, 4, 12)
    ax12.axis('off')
    
    summary_text = f"""
    AEGIS TRIAGE SYSTEM SUMMARY
    (GUIDE Dataset Only)
    
    Total Incidents: {metrics['total_incidents']}
    Processing Time: {metrics['processing_time_seconds']:.2f}s
    Success Rate: {success_metrics['success_rate']:.1f}%
    Accuracy Rate: {accuracy_metrics['accuracy_rate']:.1f}%
    Avg Time/Incident: {metrics['average_time_per_incident']:.2f}s
    Incidents/Second: {performance_metrics['incidents_per_second']:.2f}
    
    Teams Assigned: {metrics['team_metrics']['unique_teams_assigned']}
    Most Assigned: {metrics['team_metrics']['most_assigned_team'] or 'N/A'}
    
    GUIDE Success: {dataset_metrics['guide_success_rate']:.1f}%
    """
    
    ax12.text(0.05, 0.95, summary_text, transform=ax12.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Save the comprehensive visualization
    plot_file = f"results/comprehensive_analysis_{timestamp}.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"📊 Comprehensive analysis plot saved to: {plot_file}")
    
    # Save individual plots
    save_individual_plots(metrics, results, incident_metadata, timestamp)
    
    plt.close()


def save_individual_plots(metrics: Dict[str, Any], 
                         results: List[Dict[str, Any]], 
                         incident_metadata: List[Dict[str, Any]], 
                         timestamp: str) -> None:
    """
    Save individual specialized plots.
    
    Args:
        metrics (Dict[str, Any]): Generated metrics
        results (List[Dict[str, Any]]): Triage results
        incident_metadata (List[Dict[str, Any]]): Incident metadata
        timestamp (str): Timestamp for file naming
    """
    # 1. Success Rate Pie Chart
    plt.figure(figsize=(10, 8))
    success_metrics = metrics['success_metrics']
    labels = ['Accepted', 'Rejected', 'Errors']
    sizes = [success_metrics['accepted'], success_metrics['rejected'], success_metrics['errors']]
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('AEGIS Triage Success Distribution', fontsize=16, fontweight='bold')
    plt.savefig(f"results/success_distribution_{timestamp}.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Team Assignment Bar Chart
    plt.figure(figsize=(12, 8))
    team_assignments = metrics['team_metrics']['team_assignments']
    if team_assignments:
        teams = list(team_assignments.keys())
        counts = list(team_assignments.values())
        
        bars = plt.bar(teams, counts, color='#3498db')
        plt.title('Team Assignment Distribution', fontsize=16, fontweight='bold')
        plt.xlabel('Teams')
        plt.ylabel('Number of Incidents')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f"results/team_assignments_{timestamp}.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. Performance Metrics
    plt.figure(figsize=(12, 8))
    performance_metrics = metrics['performance_metrics']
    categories = ['Total Time (s)', 'Avg Time/Incident (s)', 'Incidents/Second']
    values = [
        performance_metrics['total_processing_time'],
        performance_metrics['average_processing_time'],
        performance_metrics['incidents_per_second']
    ]
    
    bars = plt.bar(categories, values, color=['#e74c3c', '#f39c12', '#2ecc71'])
    plt.title('AEGIS Processing Performance Metrics', fontsize=16, fontweight='bold')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{value:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f"results/performance_metrics_{timestamp}.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"📈 Individual plots saved to results/ directory")


def display_comprehensive_summary(metrics: Dict[str, Any], results: List[Dict[str, Any]]) -> None:
    """
    Display comprehensive summary of the triage results.
    
    Args:
        metrics (Dict[str, Any]): Generated metrics
        results (List[Dict[str, Any]]): Triage results
    """
    print(f"\n{'='*80}")
    print("🎯 AEGIS COMPREHENSIVE TRIAGE RESULTS")
    print(f"{'='*80}")
    
    # Overall performance
    print(f"\n📊 OVERALL PERFORMANCE:")
    print(f"  Total Incidents Processed: {metrics['total_incidents']}")
    print(f"  Processing Time: {metrics['processing_time_seconds']:.2f} seconds")
    print(f"  Average Time per Incident: {metrics['average_time_per_incident']:.2f} seconds")
    print(f"  Incidents per Second: {metrics['performance_metrics']['incidents_per_second']:.2f}")
    
    # Success metrics
    success_metrics = metrics['success_metrics']
    print(f"\n✅ SUCCESS METRICS:")
    print(f"  Accepted: {success_metrics['accepted']} ({success_metrics['success_rate']:.1f}%)")
    print(f"  Rejected: {success_metrics['rejected']} ({success_metrics['rejection_rate']:.1f}%)")
    print(f"  Errors: {success_metrics['errors']} ({success_metrics['error_rate']:.1f}%)")
    
    # Team assignments
    team_metrics = metrics['team_metrics']
    print(f"\n👥 TEAM ASSIGNMENTS:")
    print(f"  Unique Teams Assigned: {team_metrics['unique_teams_assigned']}")
    if team_metrics['most_assigned_team']:
        print(f"  Most Assigned Team: {team_metrics['most_assigned_team']}")
    
    for team, count in sorted(team_metrics['team_assignments'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / metrics['total_incidents']) * 100
        print(f"    {team}: {count} incidents ({percentage:.1f}%)")
    
    # Dataset performance
    dataset_metrics = metrics['dataset_metrics']
    print(f"\n📁 DATASET PERFORMANCE:")
    print(f"  GUIDE Incidents: {dataset_metrics['guide_incidents']} (Success: {dataset_metrics['guide_success_rate']:.1f}%)")
    
    # Accuracy
    accuracy_metrics = metrics['accuracy_metrics']
    print(f"\n🎯 ACCURACY METRICS:")
    print(f"  Correct Assignments: {accuracy_metrics['correct_assignments']}")
    print(f"  Total with Ground Truth: {accuracy_metrics['total_with_ground_truth']}")
    print(f"  Accuracy Rate: {accuracy_metrics['accuracy_rate']:.1f}%")
    
    print(f"\n{'='*80}")
    print("✅ Comprehensive testing completed successfully!")
    print(f"{'='*80}")


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