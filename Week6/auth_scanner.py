#!/usr/bin/env python3

import json
from collections import Counter
from datetime import datetime

def parse_log_line(line): #parses each line
    try:

     line = line.strip() #remove extra whitespace

     if not line: #skip empty lines
        return None
    
     parts = line.split() #split on spaces

     if len(parts) < 2: #don't process if line is missing any fields
        print (f"WARNING: Line too short: {line}")
        return None
     
     timestamp = parts[0] + " " + parts[1] #extract timestamp for report

     #parse key=value pairs
     data = {'timestamp': timestamp}
     for pair in parts[2:]: 
        
        if '=' not in pair: 
            print (f"WARNING: Malformed pair '{pair}' in line: {line}")
            return None
            continue
        
        key, value = pair.split('=', 1) # Split on first = only (in case value contains =)
        data[key] = value
    
     return data
    
    except Exception as e: #don't crash on errors
        print(f"ERROR: Failed to parse line: {line}")
        print(f"       Exception: {e}")
        return None

def validate(data):
    if not data:
        return False 
    required_fields = ['status', 'user', 'ip']
    for field in required_fields:
        if field not in data or not data[field]:
            return False   #verify data has required fields
        
    if data['status'] not in ['SUCCESS', 'FAIL']: #validate status as success/fail
       print(f"WARNING: Invalid status '{data['status']}'")
       return False
    
    return True

def analyze_logs(filename): #further parsing of each line in file
   
    failed_by_user = Counter()
    failed_by_ip = Counter()
    parse_errors = Counter()
    total_lines = 0
    total_success = 0
    total_fail = 0
    parse_errors = Counter()
    total_unknown_status = 0
    successful_parses = 0 

    try:
      with open(filename, 'r') as file: #open file
       file_lines = file.readlines() #separate lines of file into objects in list
       total_lines += len(file_lines) #total lines in list
       for line in file_lines:
        data = parse_log_line(line) #begin parsing

        if data is None: #count errors as defined in parse_log_line(line)
           parse_errors['malformed_line'] += 1
           continue
        
        if not validate(data): #count errors as defined in validate(data). only process safe data
           parse_errors['missing_fields'] += 1
           print (f"WARNING: Missing required fields in line: {line}")
           continue
        
        #update counts for report
        successful_parses += 1
        status = data.get('status')
        if status == 'SUCCESS':
              total_success += 1
        elif status == 'FAIL':
              total_fail += 1
              failed_by_user[data.get('user', 'UNKNOWN')] += 1
              failed_by_ip[data.get('ip', 'UNKNOWN')] += 1
      
        results = {'summary': {
            'total_events': total_lines,
            'total_success': total_success,
            'total_fail': total_fail,
            'failure_rate': round((total_fail / successful_parses) * 100, 2) if successful_parses else 0
        },
        'top_targeted_users': [
            {'username': user, 'failed_attempts': count}
            for user, count in failed_by_user.most_common(10)
        ],
        'top_attacking_ips': [
            {'ip_address': ip, 'failed_attempts': count}
            for ip, count in failed_by_ip.most_common(10)
            ]
      }

      return results
    except FileNotFoundError: #won't crash if file isn't found
       print (f'File: {filename} Not Found')

def generate_json_report(log_lines): #generate and save json report
   results = analyze_logs(log_lines)
   report = {
        'metadata': { #datetime header for report
            'generated_at': datetime.now().isoformat(),
            'analyst': 'Zaire Wood',
            'classification': 'INTERNAL'
        },
            'results': results #statistics from analyze_logs
        },
   

   finalreport = json.dumps(report, indent=2) #json dump
   with open (f'incident_report.json', 'w') as f:
      json.dump(report, f, indent=2) #writes to file
   return finalreport

def generate_text_report(logname): #generate human readable report for SOC team
    #initialize counters/variables again...
    failed_by_user = Counter()
    failed_by_ip = Counter()
    parse_errors = Counter()
    total_lines = 0
    total_success = 0
    total_fail = 0
    successful_parses = 0
    
    try:
      with open(logname, 'r') as file: #open file
       file_lines = file.readlines() #separate lines of file into objects in list
       total_lines += len(file_lines) #total lines in list
       for line in file_lines:
        data = parse_log_line(line) #begin parsing

        if data is None: #count errors as defined in parse_log_line(line)
           parse_errors['malformed_line'] += 1
           continue
        
        if not validate(data): #count errors as defined in validate(data). only process safe data
           parse_errors['missing_fields'] += 1
           continue
        
        #update counts for report
        successful_parses += 1
        status = data.get('status')
        if status == 'SUCCESS':
              total_success += 1
        elif status == 'FAIL':
              total_fail += 1
              failed_by_user[data.get('user', 'UNKNOWN')] += 1
              failed_by_ip[data.get('ip', 'UNKNOWN')] += 1
        failure_rate = round((total_fail / successful_parses) * 100, 2)
    except FileNotFoundError: #won't crash if file isn't found
       print (f'File: {logname} Not Found')
    failure_rate = round((total_fail / successful_parses) * 100, 2)
    # Build report
    report = []
    report.append("=" * 70)
    report.append("       AUTHENTICATION FAILURE ANALYSIS REPORT")
    report.append(f"       Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("=" * 70)
    report.append("")
    
    # Alert if high failure rate
    if failure_rate > 10:
        report.append("[ CRITICAL ALERT ]")
        report.append(f"Abnormally high failure rate: {failure_rate}% (baseline: 2-5%)")
        report.append("Potential BRUTE FORCE ATTACK in progress.")
        report.append("")
    
    # Summary
    report.append("-" * 70)
    report.append("SUMMARY STATISTICS")
    report.append("-" * 70)
    report.append(f"Total Events:        {total_lines:,}")
    report.append(f"Successful Logins:   {total_success:,}  ({total_success/successful_parses*100:.1f}%)")
    report.append(f"Failed Attempts:     {total_fail:,}  ({failure_rate})%")
    report.append("")
    
    # Top targeted users
    report.append("-" * 70)
    report.append("TOP 5 TARGETED ACCOUNTS")
    report.append("-" * 70)
    for i, (user, count) in enumerate(failed_by_user.most_common(5), 1):
        severity = "CRITICAL" if count > 1000 else "HIGH" if count > 500 else "MEDIUM"
        report.append(f"{i}. {user:20} {count:,} attempts  ⚠ {severity}")
    report.append("")
    
    # Top attacking IPs
    report.append("-" * 70)
    report.append("TOP 5 ATTACKING SOURCE IPs")
    report.append("-" * 70)
    for i, (ip, count) in enumerate(failed_by_ip.most_common(5), 1):
        action = "BLOCK IMMEDIATELY" if count > 1000 else "INVESTIGATE"
        report.append(f"{i}. {ip:20} {count:,} attempts  ⚠ {action}")
    report.append("")
    
    # Recommendations
    report.append("-" * 70)
    report.append("RECOMMENDED ACTIONS")
    report.append("-" * 70)
    if failure_rate > 50:
        report.append("[ IMMEDIATE ]")
        top_ips = [ip for ip, _ in failed_by_ip.most_common(3)]
        report.append(f"  • Block IPs {', '.join(top_ips)} at firewall")
        report.append("  • Lock high-value accounts (require password reset)")
        report.append("  • Escalate to Incident Response team")
    
    return "\n".join(report)
    

def main():
     print (f"Input file location: ")
     file_location = input(r'')
     print("Authentication Log Scanner")
     print("=" * 50)

     generate_json_report(file_location)
     generate_text_report(file_location)

     textreport = generate_text_report(file_location)
     print(textreport)

    # Save to file
     with open('incident_report.txt', 'w', encoding='utf-8') as f: #had to add encoding bit or it was crashing
       f.write(textreport)


if __name__ == "__main__":
  main()
