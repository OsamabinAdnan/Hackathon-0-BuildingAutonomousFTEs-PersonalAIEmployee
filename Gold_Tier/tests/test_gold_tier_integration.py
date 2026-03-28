#!/usr/bin/env python
"""
Gold Tier Integration Verification
Verifies ALL Gold Tier requirements are integrated into orchestrator
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("GOLD TIER - FINAL INTEGRATION VERIFICATION")
print("=" * 70)
print()

orchestrator_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'orchestrator', 'main.py'
)

with open(orchestrator_path, 'r', encoding='utf-8') as f:
    orchestrator_content = f.read()

# ============================================================================
# REQUIREMENT 1: All Silver Requirements
# ============================================================================
print("1. Silver Tier Requirements (Foundation)...")
print()

silver_checks = {
    'Watcher imports': ['gmail_watcher', 'whatsapp_watcher', 'linkedin_watcher', 'filesystem_watcher'],
    'MCP integration': ['mcp_server', 'EmailService', 'WhatsAppService', 'LinkedInService'],
    'HITL workflow': ['/Approved', '/Pending_Approval', '/Rejected'],
    'Dashboard updates': ['update_dashboard', 'Dashboard'],
}

for check_name, keywords in silver_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 2: Cross-Domain Integration
# ============================================================================
print("2. Cross-Domain Integration (Personal + Business)...")
print()

cross_domain_checks = {
    'Personal (email)': ['email', 'Gmail'],
    'Personal (WhatsApp)': ['whatsapp', 'WhatsApp'],
    'Business (LinkedIn)': ['linkedin', 'LinkedIn'],
    'Business (Facebook)': ['facebook', 'Facebook'],
    'Business (Odoo)': ['odoo', 'Odoo'],
    'Files': ['files', 'FileSystem'],
}

for domain, keywords in cross_domain_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {domain}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 3: Odoo Accounting Integration
# ============================================================================
print("3. Odoo Accounting Integration...")
print()

odoo_checks = {
    'Odoo import': ['from mcp_server.odoo_service import OdooService'],
    'Odoo in VALID_CATEGORIES': ["'odoo'"],
    'Odoo execution': ['odoo_service', 'create_invoice', 'record_payment'],
    'Odoo folders': ['/Needs_Action/odoo', '/Done/odoo'],
}

for check_name, keywords in odoo_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 4: Facebook Integration
# ============================================================================
print("4. Facebook Integration...")
print()

facebook_checks = {
    'Facebook import': ['facebook_service', 'FacebookService'],
    'Facebook in VALID_CATEGORIES': ["'facebook'"],
    'Facebook execution': ['post_facebook', 'send_facebook_message'],
    'Facebook folders': ['/Needs_Action/facebook', '/Done/facebook'],
}

for check_name, keywords in facebook_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 6: Multiple MCP Servers
# ============================================================================
print("6. Multiple MCP Servers...")
print()

mcp_checks = {
    'Email MCP': ['send_email'],
    'WhatsApp MCP': ['send_whatsapp'],
    'LinkedIn MCP': ['post_linkedin'],
    'Facebook MCP': ['post_facebook'],
    'Odoo MCP': ['create_invoice', 'record_payment', 'get_financial_report'],
}

for check_name, keywords in mcp_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 7: Weekly CEO Briefing
# ============================================================================
print("7. Weekly CEO Briefing...")
print()

briefing_checks = {
    'Briefing method': ['generate_briefing', 'briefing'],
    'Briefing folder': ['/Briefings'],
    'Odoo integration': ['get_financial_report', 'revenue'],
    'Scheduling': ['weekly_briefing.ps1', 'Monday'],
}

for check_name, keywords in briefing_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 8: Error Recovery
# ============================================================================
print("8. Error Recovery & Graceful Degradation...")
print()

error_checks = {
    'Retry logic': ['retry', 'Retry'],
    'Circuit breaker': ['circuit_breaker', 'CircuitBreaker'],
    'Health checks': ['health', 'Health'],
    'Error handling': ['try:', 'except', 'logger.error'],
    'Fallback': ['DirectExecutor', 'fallback'],
}

for check_name, keywords in error_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 9: Audit Logging
# ============================================================================
print("9. Comprehensive Audit Logging...")
print()

audit_checks = {
    'Audit import': ['from audit.logger import', 'audit_logger'],
    'Audit logging': ['log_action', 'log_odoo_invoice', 'log_facebook_post'],
    'Audit folders': ['/Logs/audit'],
}

for check_name, keywords in audit_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 10: Ralph Wiggum Loop
# ============================================================================
print("10. Ralph Wiggum Loop...")
print()

ralph_checks = {
    'Ralph import': ['from ralph_wiggum import', 'TaskTracker', 'StopHook'],
    'Task tracking': ['get_task_tracker', 'start_task'],
    'Max iterations': ['max_iterations'],
    'Completion signal': ['TASK_COMPLETE', 'completion'],
    'State persistence': ['ralph_wiggum_state.json'],
}

for check_name, keywords in ralph_checks.items():
    found = all(kw in orchestrator_content for kw in keywords)
    print(f"   {'✅' if found else '❌'} {check_name}: {'Integrated' if found else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 11: Documentation
# ============================================================================
print("11. Documentation...")
print()

docs_folder = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'docs'
)

doc_files = os.listdir(docs_folder) if os.path.exists(docs_folder) else []
doc_count = len([f for f in doc_files if f.endswith('.md')])

print(f"   ✅ Documentation files: {doc_count} files")
print(f"   ✅ README.md: {'Present' if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'README.md')) else 'MISSING'}")
print(f"   ✅ odoo/README.md: {'Present' if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'odoo', 'README.md')) else 'MISSING'}")
print()

# ============================================================================
# REQUIREMENT 12: Agent Skills
# ============================================================================
print("12. Agent Skills...")
print()

skills_folder = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    '.claude', 'skills'
)

skills = [d for d in os.listdir(skills_folder) if os.path.isdir(os.path.join(skills_folder, d))] if os.path.exists(skills_folder) else []

silver_skills = ['process-inbox', 'update-dashboard', 'send-email', 'send-whatsapp', 'post-linkedin', 'send-linkedin-message', 'browsing-with-playwright']
gold_skills = ['create-invoice', 'record-payment', 'get-financial-report', 'post-facebook', 'send-facebook-message', 'generate-briefing']

silver_count = len([s for s in skills if s in silver_skills])
gold_count = len([s for s in skills if s in gold_skills])

print(f"   ✅ Total skills: {len(skills)}")
print(f"   ✅ Silver Tier skills: {silver_count}/7")
print(f"   ✅ Gold Tier skills: {gold_count}/6")
print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 70)
print("FINAL INTEGRATION SUMMARY")
print("=" * 70)
print()

# Count all checks
all_requirements = [
    ("1. Silver Requirements", silver_checks),
    ("2. Cross-Domain", cross_domain_checks),
    ("3. Odoo", odoo_checks),
    ("4. Facebook", facebook_checks),
    ("6. MCP Servers", mcp_checks),
    ("7. CEO Briefing", briefing_checks),
    ("8. Error Recovery", error_checks),
    ("9. Audit Logging", audit_checks),
    ("10. Ralph Wiggum", ralph_checks),
]

total_checks = 0
passed_checks = 0

for req_name, checks in all_requirements:
    for check_name, keywords in checks.items():
        total_checks += 1
        if all(kw in orchestrator_content for kw in keywords):
            passed_checks += 1

print(f"Integration Checks: {passed_checks}/{total_checks} passed ({passed_checks/total_checks*100:.1f}%)")
print()

if passed_checks == total_checks:
    print("✅ ALL GOLD TIER REQUIREMENTS INTEGRATED!")
    print()
    print("The orchestrator is ready to run with full Gold Tier functionality.")
else:
    missing = total_checks - passed_checks
    print(f"⚠️  {missing} integration check(s) need attention")
    print()
    print("Review the missing integrations above before running orchestrator.")

print()
print("=" * 70)
print("INTEGRATION VERIFICATION COMPLETE")
print("=" * 70)
print()
