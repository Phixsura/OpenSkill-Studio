"""Scope constants — centralized permission scope definitions."""

# Read scopes
READ_COHORTS = "read:cohorts"
READ_PROJECTS = "read:projects"
READ_SUBMISSIONS = "read:submissions"
READ_SKILLS = "read:skills"
READ_ANALYTICS = "read:analytics"
READ_TALENT = "read:talent"
READ_PACKS = "read:packs"
READ_WORKFLOWS = "read:workflows"

# Write scopes
WRITE_COHORTS = "write:cohorts"
WRITE_PROJECTS = "write:projects"
WRITE_SKILLS = "write:skills"
WRITE_TALENT = "write:talent"
WRITE_EVALUATIONS = "write:evaluations"

# Special scopes
SUBSCRIBE_EVENTS = "subscribe:events"
EXTEND_UI = "extend:ui"
RUN_BACKGROUND = "run:background_jobs"
EXPORT_ANALYTICS = "export:analytics"

ALL_READ = [READ_COHORTS, READ_PROJECTS, READ_SUBMISSIONS, READ_SKILLS, READ_ANALYTICS, READ_TALENT, READ_PACKS, READ_WORKFLOWS]
ALL_WRITE = [WRITE_COHORTS, WRITE_PROJECTS, WRITE_SKILLS, WRITE_TALENT, WRITE_EVALUATIONS]
ALL_SPECIAL = [SUBSCRIBE_EVENTS, EXTEND_UI, RUN_BACKGROUND, EXPORT_ANALYTICS]
ALL_SCOPES = ALL_READ + ALL_WRITE + ALL_SPECIAL
