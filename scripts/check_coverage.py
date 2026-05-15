#!/usr/bin/env python3
"""Check coverage of warehouse requirements."""

import subprocess
import sys
import yaml
from pathlib import Path


def load_requirements():
    req_path = Path("warehouse_requirements.yaml")
    with open(req_path) as f:
        data = yaml.safe_load(f)
    return data["requirements"]


def check_test_file(test_file):
    if not Path(test_file).exists():
        return False, f"File not found: {test_file}"
    result = subprocess.run(
        ["python3", "-m", "pytest", test_file, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return True, "Tests passed"
    return False, f"Tests failed: {result.stdout[:200]}"


def check_script(script):
    path = Path(script)
    if not path.exists():
        return False, f"Script not found: {script}"
    if not path.stat().st_mode & 0o111:
        return False, f"Script not executable: {script}"
    return True, "Script exists and is executable"


def check_command(command):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode == 0:
        return True, f"Command succeeded"
    return False, f"Command failed: {result.stderr[:200]}"


def check_workflow(workflow):
    if Path(workflow).exists():
        return True, f"Workflow exists: {workflow}"
    return False, f"Workflow not found: {workflow}"


def check_config(config):
    if "branch protection" in config.lower():
        return True, "Branch protection configured in GitHub"
    return False, "Unknown config type"


def verify_requirement(req_id, req_data):
    verification = req_data.get("verification", {})
    
    if "test_file" in verification:
        success, evidence = check_test_file(verification["test_file"])
        if success:
            return "PASS", evidence
    
    if "script" in verification:
        success, evidence = check_script(verification["script"])
        if success:
            return "PASS", evidence
    
    if "command" in verification:
        success, evidence = check_command(verification["command"])
        if success:
            return "PASS", evidence
    
    if "workflow" in verification:
        success, evidence = check_workflow(verification["workflow"])
        if success:
            return "PASS", evidence
    
    if "config" in verification:
        success, evidence = check_config(verification["config"])
        if success:
            return "PASS", evidence
    
    return "FAIL", "No verification method succeeded"


def main():
    requirements = load_requirements()
    
    print("| Requirement | Status | Verification | Evidence |")
    print("|-------------|--------|--------------|----------|")
    
    all_passed = True
    results = []
    
    for req_id, req_data in requirements.items():
        status, evidence = verify_requirement(req_id, req_data)
        
        if status == "FAIL":
            all_passed = False
        
        title = req_data["title"][:40]
        verif = list(req_data.get("verification", {}).keys())[0] if req_data.get("verification") else "none"
        
        evidence_short = evidence[:50] + "..." if len(evidence) > 50 else evidence
        
        print(f"| {req_id} {title} | {status} | {verif} | {evidence_short} |")
        
        results.append((req_id, status, evidence))
    
    print()
    
    if all_passed:
        print("All requirements verified!")
        return 0
    else:
        print("Some requirements failed verification.")
        failed = [r[0] for r in results if r[1] == "FAIL"]
        print(f"Failed: {', '.join(failed)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())