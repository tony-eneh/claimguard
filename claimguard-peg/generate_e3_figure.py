#!/usr/bin/env python3
"""
E3 Figure Generation: Create bar chart of attack block rates.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np

def generate_e3_chart(input_dir: str = "experiment_results/e3", output_dir: str = "figures/e3"):
    """Generate bar chart for E3 attack block rates."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Load results
    attacks = {}
    
    # Role Spoofing
    try:
        with open(os.path.join(input_dir, "e3_role_spoofing.json"), "r") as f:
            data = json.load(f)
            attempts = data.get("spoofing_attempts", 0)
            blocked = data.get("spoofing_blocked", 0)
            rate = (blocked / attempts * 100) if attempts > 0 else 0
            attacks["Role/Identity\nSpoofing"] = rate
    except:
        pass
    
    # Cloud Bypass
    try:
        with open(os.path.join(input_dir, "e3_cloud_bypass.json"), "r") as f:
            data = json.load(f)
            attempts = data.get("bypass_attempts", 0)
            blocked = data.get("bypass_blocked", 0)
            rate = (blocked / attempts * 100) if attempts > 0 else 0
            attacks["Direct Cloud\nBypass"] = rate
    except:
        pass
    
    # Gateway Abuse
    try:
        with open(os.path.join(input_dir, "e3_gateway_abuse.json"), "r") as f:
            data = json.load(f)
            attempts = data.get("abuse_attempts", 0)
            gracefully_rejected = data.get("gracefully_rejected", 0)
            unexpected_success = data.get("unexpected_success", 0)
            health_rate = ((attempts - unexpected_success) / attempts * 100) if attempts > 0 else 0
            attacks["Gateway Abuse\n/ Flood"] = health_rate
    except:
        pass
    
    if not attacks:
        print("✗ No E3 results to chart")
        return
    
    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    names = list(attacks.keys())
    rates = list(attacks.values())
    colors = ['#d62728' if r < 75 else '#2ca02c' for r in rates]  # Red if < 75%, green otherwise
    
    bars = ax.bar(names, rates, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add percentage labels on bars
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{rate:.0f}%',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add threshold line at 80%
    ax.axhline(y=80, color='gray', linestyle='--', linewidth=2, label='Pass Threshold (80%)')
    
    ax.set_ylabel('Block Rate (%)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 120)
    ax.set_title('E3: Attack Block Rates by Vector', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    filepath = os.path.join(output_dir, "e3_attack_block_rates.png")
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    print(f"✓ Chart saved to {filepath}")
    plt.close()

if __name__ == "__main__":
    generate_e3_chart()
