#!/usr/bin/env python3
"""
E3 Analysis: Summarize attack test results and generate security table.
"""

import json
import os
import argparse
from typing import Dict, Any
import pandas as pd

def load_e3_results(input_dir: str = "experiment_results/e3") -> Dict[str, Any]:
    """Load all E3 test results from JSON files."""
    results = {}
    
    test_files = [
        "e3_token_replay.json",
        "e3_token_forgery.json",
        "e3_role_spoofing.json",
        "e3_cloud_bypass.json",
        "e3_gateway_abuse.json"
    ]
    
    for test_file in test_files:
        filepath = os.path.join(input_dir, test_file)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                test_name = data.get("test", test_file.replace("e3_", "").replace(".json", ""))
                results[test_name] = data
                print(f"✓ Loaded {test_file}")
        else:
            print(f"✗ Missing {test_file}")
    
    return results

def analyze_results(results: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Analyze E3 results and compute key metrics."""
    analysis = {}
    
    # Token Replay Analysis
    if "token_replay" in results:
        tr = results["token_replay"]
        analysis["token_replay"] = {
            "attack": "Token Replay",
            "attempts": tr.get("replays_attempted", 0) + tr.get("expired_replays_attempted", 0),
            "blocked": tr.get("replays_blocked", 0) + tr.get("expired_replays_blocked", 0),
            "success_rate": 0.0,
            "details": f"Replays blocked: {tr.get('replays_blocked', 0)}, Expired: {tr.get('expired_replays_blocked', 0)}"
        }
        if analysis["token_replay"]["attempts"] > 0:
            analysis["token_replay"]["success_rate"] = (analysis["token_replay"]["blocked"] / analysis["token_replay"]["attempts"]) * 100
    
    # Token Forgery Analysis
    if "token_forgery" in results:
        tf = results["token_forgery"]
        analysis["token_forgery"] = {
            "attack": "Token Forgery/Tampering",
            "attempts": tf.get("forgeries_attempted", 0),
            "blocked": tf.get("forgeries_blocked", 0),
            "success_rate": 0.0,
            "details": f"Forgeries blocked: {tf.get('forgeries_blocked', 0)}/{tf.get('forgeries_attempted', 0)}"
        }
        if analysis["token_forgery"]["attempts"] > 0:
            analysis["token_forgery"]["success_rate"] = (analysis["token_forgery"]["blocked"] / analysis["token_forgery"]["attempts"]) * 100
    
    # Role Spoofing Analysis
    if "role_spoofing" in results:
        rs = results["role_spoofing"]
        analysis["role_spoofing"] = {
            "attack": "Role/Identity Spoofing",
            "attempts": rs.get("spoofing_attempts", 0),
            "blocked": rs.get("spoofing_blocked", 0),
            "success_rate": 0.0,
            "details": f"Spoofing blocked: {rs.get('spoofing_blocked', 0)}/{rs.get('spoofing_attempts', 0)}"
        }
        if analysis["role_spoofing"]["attempts"] > 0:
            analysis["role_spoofing"]["success_rate"] = (analysis["role_spoofing"]["blocked"] / analysis["role_spoofing"]["attempts"]) * 100
    
    # Cloud Bypass Analysis
    if "cloud_bypass" in results:
        cb = results["cloud_bypass"]
        analysis["cloud_bypass"] = {
            "attack": "Direct Cloud Bypass",
            "attempts": cb.get("bypass_attempts", 0),
            "blocked": cb.get("bypass_blocked", 0),
            "success_rate": 0.0,
            "details": f"Bypass blocked: {cb.get('bypass_blocked', 0)}/{cb.get('bypass_attempts', 0)}"
        }
        if analysis["cloud_bypass"]["attempts"] > 0:
            analysis["cloud_bypass"]["success_rate"] = (analysis["cloud_bypass"]["blocked"] / analysis["cloud_bypass"]["attempts"]) * 100
    
    # Gateway Abuse Analysis
    if "gateway_abuse" in results:
        ga = results["gateway_abuse"]
        analysis["gateway_abuse"] = {
            "attack": "Gateway Abuse / Flood",
            "attempts": ga.get("abuse_attempts", 0),
            "blocked": ga.get("gracefully_rejected", 0),
            "success_rate": 0.0,
            "details": f"Malformed requests rejected: {ga.get('gracefully_rejected', 0)}/{ga.get('abuse_attempts', 0)}"
        }
        if analysis["gateway_abuse"]["attempts"] > 0:
            analysis["gateway_abuse"]["success_rate"] = (analysis["gateway_abuse"]["blocked"] / analysis["gateway_abuse"]["attempts"]) * 100
    
    return analysis

def generate_summary_table(analysis: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """Generate a summary table suitable for LaTeX."""
    data = []
    for key, metrics in analysis.items():
        data.append({
            "Attack": metrics["attack"],
            "Attempts": metrics["attempts"],
            "Blocked": metrics["blocked"],
            "Block Rate (%)": f"{metrics['success_rate']:.1f}",
            "Result": "✓ PASS" if metrics['success_rate'] >= 95 else "✗ FAIL"
        })
    
    df = pd.DataFrame(data)
    return df

def main():
    parser = argparse.ArgumentParser(description="E3 Attack Test Analysis")
    parser.add_argument("--input-dir", default="experiment_results/e3", help="Input results directory")
    parser.add_argument("--output-dir", default="experiment_results/e3", help="Output directory")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("E3 ANALYSIS: ADVERSARIAL & ATTACK BEHAVIOUR")
    print("=" * 80)
    
    # Load results
    results = load_e3_results(args.input_dir)
    
    if not results:
        print("✗ No E3 results found")
        return
    
    # Analyze
    analysis = analyze_results(results)
    
    # Generate table
    summary_df = generate_summary_table(analysis)
    
    print("\n" + summary_df.to_string(index=False))
    
    # Save summary
    os.makedirs(args.output_dir, exist_ok=True)
    
    summary_csv = os.path.join(args.output_dir, "e3_security_summary.csv")
    summary_df.to_csv(summary_csv, index=False)
    print(f"\n✓ Summary saved to {summary_csv}")
    
    # Save LaTeX table
    latex_file = os.path.join(args.output_dir, "e3_security_table.tex")
    try:
        latex_table = summary_df.to_latex(index=False, escape=False)
        with open(latex_file, "w", encoding='utf-8') as f:
            f.write(latex_table)
        print(f"✓ LaTeX table saved to {latex_file}")
    except Exception as e:
        print(f"⚠ Could not generate LaTeX table (missing jinja2): {e}")
        # Fallback: create simple LaTeX table manually
        with open(latex_file, "w", encoding='utf-8') as f:
            f.write("\\begin{table}[ht]\n")
            f.write("\\centering\n")
            f.write("\\caption{E3 Security Assessment: Attack Block Rates}\n")
            f.write("\\begin{tabular}{lcccc}\n")
            f.write("\\toprule\n")
            f.write("\\textbf{Attack} & \\textbf{Attempts} & \\textbf{Blocked} & \\textbf{Block Rate (\\%)} & \\textbf{Result} \\\\\n")
            f.write("\\midrule\n")
            for _, row in summary_df.iterrows():
                attack = row['Attack']
                attempts = row['Attempts']
                blocked = row['Blocked']
                block_rate = row['Block Rate (%)']
                result = "PASS" if "PASS" in row['Result'] else "FAIL"
                f.write(f"{attack} & {attempts} & {blocked} & {block_rate} & {result} \\\\\n")
            f.write("\\bottomrule\n")
            f.write("\\end{tabular}\n")
            f.write("\\label{tab:e3-security}\n")
            f.write("\\end{table}\n")
        print(f"✓ LaTeX table saved to {latex_file} (fallback format)")
    
    # Overall assessment
    print("\n" + "=" * 80)
    print("SECURITY ASSESSMENT")
    print("=" * 80)
    
    all_blocked = all(a["success_rate"] >= 95 for a in analysis.values())
    if all_blocked:
        print("✓ ALL ATTACKS BLOCKED (≥95% block rate)")
        print("  ClaimGuard successfully prevents unauthorized evidence access.")
    else:
        print("✗ SOME ATTACKS SUCCEEDED")
        for key, metrics in analysis.items():
            if metrics["success_rate"] < 95:
                print(f"  - {metrics['attack']}: {metrics['success_rate']:.1f}% blocked")

if __name__ == "__main__":
    main()
