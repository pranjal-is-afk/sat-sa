import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

os.makedirs('data/sample', exist_ok=True)

start_date = datetime(2024, 10, 1)

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def generate_cse_01():
    # Base
    cse_id = 'CSE-01'
    # Assets
    assets = [
        ['WEB-SERVER-01', cse_id, 'HIGH', 'Server', 'Banking'],
        ['DB-SERVER-01', cse_id, 'CRITICAL', 'Database', 'Banking'],
        ['FIREWALL-01', cse_id, 'CRITICAL', 'Network', 'Banking'],
        ['ENDPOINT-01', cse_id, 'MEDIUM', 'Endpoint', 'Banking'],
        ['ROUTER-01', cse_id, 'HIGH', 'Network', 'Banking']
    ]
    pd.DataFrame(assets, columns=['asset_id', 'cse_id', 'classification', 'asset_type', 'sector']).to_csv(f'data/sample/{cse_id}_assets.csv', index=False)
    
    alerts = []
    cases = []
    
    templates = [f"Investigation completed. Findings documented in internal tracker {i}." for i in range(40)]
    
    case_idx = 1
    for i in range(3200):
        aid = f"ALT-{cse_id}-{i:05d}"
        r = random.random()
        if r < 0.15: sev = 'CRITICAL'
        elif r < 0.45: sev = 'HIGH'
        elif r < 0.80: sev = 'MEDIUM'
        else: sev = 'LOW'
        
        c_time = random_date(start_date, start_date + timedelta(days=90))
        a_time = c_time + timedelta(minutes=random.uniform(1, 15))
        
        if sev == 'CRITICAL':
            close_delta = np.random.normal(47, 12)
        else:
            close_delta = np.random.normal(120, 40)
            
        close_delta = max(close_delta, 1)
        cl_time = c_time + timedelta(minutes=close_delta)
        
        has_case = (sev == 'CRITICAL' and random.random() < 0.85) or (sev != 'CRITICAL' and random.random() < 0.1)
        cid = None
        if has_case:
            cid = f"CAS-{cse_id}-{case_idx:04d}"
            case_idx += 1
            esc = random.random() < 0.28
            cases.append([
                cid, cse_id, a_time, cl_time,
                random.choice(templates), f"ANA-0{random.randint(1,5)}",
                esc, "Resolved", f'["{aid}"]'
            ])
            
        alerts.append([
            aid, cse_id, sev, c_time.isoformat(), a_time.isoformat(), cl_time.isoformat(),
            'CLOSED', cid, random.choice(assets)[0], False
        ])
        
    pd.DataFrame(alerts, columns=['alert_id','cse_id','severity','created_at','acknowledged_at','closed_at','status','case_id','asset_id','escalated']).to_csv(f'data/sample/{cse_id}_alerts.csv', index=False)
    pd.DataFrame(cases, columns=['case_id','cse_id','opened_at','closed_at','investigation_text','investigator_id','escalated','resolution','alert_ids']).to_csv(f'data/sample/{cse_id}_cases.csv', index=False)


def generate_cse_07():
    # Execution Gap
    cse_id = 'CSE-07'
    assets = [
        ['WEB-SERVER-07', cse_id, 'HIGH', 'Server', 'Banking'],
        ['DB-SERVER-07', cse_id, 'CRITICAL', 'Database', 'Banking'],
        ['FIREWALL-07', cse_id, 'HIGH', 'Network', 'Banking'],
        ['ENDPOINT-07', cse_id, 'LOW', 'Endpoint', 'Banking']
    ]
    pd.DataFrame(assets, columns=['asset_id', 'cse_id', 'classification', 'asset_type', 'sector']).to_csv(f'data/sample/{cse_id}_assets.csv', index=False)
    
    alerts = []
    cases = []
    
    templates = [
        "Alert investigated. No indicators of compromise found. Closed without escalation.",
        "Alert investigated. No indicators of compromise found. Closed without escalation.",
        "Standard triage performed. System baseline verified. No IOC identified. Closed."
    ]
    
    case_idx = 1
    for i in range(4800):
        aid = f"ALT-{cse_id}-{i:05d}"
        if i < 960:
            sev = 'CRITICAL'
        else:
            sev = random.choice(['HIGH', 'MEDIUM', 'LOW'])
            
        c_time = random_date(start_date, start_date + timedelta(days=90))
        a_time = c_time + timedelta(minutes=random.uniform(0.5, 2))
        
        if sev == 'CRITICAL':
            close_delta = np.random.normal(5.2, 0.15)
        else:
            close_delta = np.random.normal(20, 5)
            
        close_delta = max(close_delta, 1)
        cl_time = c_time + timedelta(minutes=close_delta)
        
        has_case = (sev == 'CRITICAL' and random.random() < 0.8) or (sev != 'CRITICAL' and random.random() < 0.05)
        cid = None
        if has_case:
            cid = f"CAS-{cse_id}-{case_idx:04d}"
            case_idx += 1
            esc = random.random() < 0.06
            if random.random() < 0.74:
                txt = "Alert investigated. No indicators of compromise found. Closed without escalation."
            else:
                txt = f"Investigated system activity on port {random.randint(1024,65535)}. Correlated firewall session logs."
            cases.append([
                cid, cse_id, a_time, cl_time,
                txt, "ANA-007",
                esc, "Resolved", f'["{aid}"]'
            ])
            
        alerts.append([
            aid, cse_id, sev, c_time.isoformat(), a_time.isoformat(), cl_time.isoformat(),
            'CLOSED', cid, random.choice(assets)[0], False
        ])
        
    pd.DataFrame(alerts, columns=['alert_id','cse_id','severity','created_at','acknowledged_at','closed_at','status','case_id','asset_id','escalated']).to_csv(f'data/sample/{cse_id}_alerts.csv', index=False)
    pd.DataFrame(cases, columns=['case_id','cse_id','opened_at','closed_at','investigation_text','investigator_id','escalated','resolution','alert_ids']).to_csv(f'data/sample/{cse_id}_cases.csv', index=False)


def generate_cse_11():
    # Negative Space
    cse_id = 'CSE-11'
    assets = [
        ['FIN-SERVER-04', cse_id, 'CRITICAL', 'Server', 'Banking'], # silent
        ['SWIFT-GW-04', cse_id, 'CRITICAL', 'Network', 'Banking'],  # silent
        ['CTRL-SRV-11', cse_id, 'CRITICAL', 'Server', 'Banking'],
        ['ENDPOINT-11A', cse_id, 'MEDIUM', 'Endpoint', 'Banking']
    ]
    pd.DataFrame(assets, columns=['asset_id', 'cse_id', 'classification', 'asset_type', 'sector']).to_csv(f'data/sample/{cse_id}_assets.csv', index=False)
    
    alerts = []
    cases = []
    
    case_idx = 1
    for i in range(1100):
        aid = f"ALT-{cse_id}-{i:05d}"
        r = random.random()
        if r < 0.25: sev = 'CRITICAL'
        elif r < 0.75: sev = 'MEDIUM'
        else: sev = 'LOW'
        
        c_time = random_date(start_date, start_date + timedelta(days=90))
        a_time = c_time + timedelta(minutes=random.uniform(5, 30))
        
        close_delta = np.random.normal(60, 20)
        close_delta = max(close_delta, 5)
        cl_time = c_time + timedelta(minutes=close_delta)
        
        has_case = (sev == 'CRITICAL' and random.random() < 0.8) or (sev != 'CRITICAL' and random.random() < 0.1)
        cid = None
        if has_case:
            cid = f"CAS-{cse_id}-{case_idx:04d}"
            case_idx += 1
            esc = random.random() < 0.22
            cases.append([
                cid, cse_id, a_time, cl_time,
                f"Valid investigation for {aid}. Checked systems.", f"ANA-0{random.randint(1,3)}",
                esc, "Resolved", f'["{aid}"]'
            ])
            
        asset_id = 'CTRL-SRV-11' if random.random() < 0.5 else 'ENDPOINT-11A' # Never FIN-SERVER-04
            
        alerts.append([
            aid, cse_id, sev, c_time.isoformat(), a_time.isoformat(), cl_time.isoformat(),
            'CLOSED', cid, asset_id, False
        ])
        
    pd.DataFrame(alerts, columns=['alert_id','cse_id','severity','created_at','acknowledged_at','closed_at','status','case_id','asset_id','escalated']).to_csv(f'data/sample/{cse_id}_alerts.csv', index=False)
    pd.DataFrame(cases, columns=['case_id','cse_id','opened_at','closed_at','investigation_text','investigator_id','escalated','resolution','alert_ids']).to_csv(f'data/sample/{cse_id}_cases.csv', index=False)

generate_cse_01()
generate_cse_07()
generate_cse_11()
print("Sample data generated.")
