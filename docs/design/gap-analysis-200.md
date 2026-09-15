# 200-Item Gap Analysis: OpenSkill Talent Layer vs World-Class Platforms

Compared against: Eightfold AI, Workday Skills Cloud, LinkedIn Talent Solutions, Gloat, Credly/Open Badges 3.0, Greenhouse, Lever, Phenom, iCIMS, Degreed, BambooHR, Cornerstone OnDemand

---

## A. Skill Intelligence & Ontology (20 gaps)

1. **No AI/LLM-powered skill extraction** — current `skill_inference.py` uses regex tokenization only; Eightfold uses deep learning on 1.6M skills
2. **No skill taxonomy import from ESCO/O\*NET** — `external_ids` field exists but no bulk import endpoint or ETL pipeline
3. **No skill taxonomy admin UI** — no frontend page to manage capabilities, edges, mappings
4. **No skill version history** — capabilities have no changelog or version tracking
5. **No skill deprecation workflow UI** — merge/deprecate is API-only, no admin flow
6. **No skill category taxonomy tree view** — no hierarchical visualization of parent_id relationships
7. **No skill auto-suggestion while typing** — no typeahead/autocomplete endpoint for skill names
8. **No skill frequency analytics** — no tracking of how often each skill is searched/viewed
9. **No skill co-occurrence analysis** — no computation of which skills frequently appear together
10. **No skill semantic embeddings** — no vector-based skill similarity (Eightfold uses embeddings)
11. **No industry-specific skill taxonomies** — no pre-built taxonomies for specific verticals
12. **No skill mapping confidence scoring** — `contribution_weight` exists but no automated confidence
13. **No skill mapping bulk import/export** — no CSV/JSON import for capability mappings
14. **No multi-language skill search** — `translations` field exists but search doesn't use it
15. **No skill relationship strength scoring** — edges have no weight/strength attribute
16. **No skill graph visualization frontend** — no interactive graph view of capability relationships
17. **No skill API versioning** — no v2 compatibility layer for ontology changes
18. **No skill suggestion from job market data** — no external data source integration
19. **No skill normalization pipeline** — no automated deduplication across sources
20. **No skill governance workflow** — no approval process for adding new capabilities

## B. Evidence & Scoring (15 gaps)

21. **No evidence quality scoring** — all evidence treated equally within verification level
22. **No evidence expiration alerts** — no notification when evidence is about to expire
23. **No evidence bulk import** — bulk API exists but no CSV/file upload
24. **No evidence dispute/challenge flow** — no way to contest an evidence entry
25. **No evidence endorsement by third party** — endorsements create new evidence but can't endorse existing
26. **No scoring simulation** — no "what-if" tool to see how adding evidence would change score
27. **No scoring explanation UI** — scores shown as numbers but no breakdown visualization
28. **No scoring calibration tools** — no way to adjust weights platform-wide
29. **No scoring A/B testing** — no framework to test new scoring algorithms
30. **No scoring audit trail** — `CapabilityScoreSnapshot` exists but no UI to view history
31. **No evidence chain visualization** — provenance chain is API-only, no frontend
32. **No evidence type distribution analytics** — no dashboard showing evidence source mix
33. **No cross-org evidence portability** — evidence doesn't transfer between organizations
34. **No evidence import from external platforms** — no LinkedIn/Credly import
35. **No automated evidence generation from platform activity** — no hooks from existing project/skill modules

## C. Passport & Privacy (15 gaps)

36. **No passport PDF export** — no downloadable PDF version of the passport
37. **No passport QR code** — no QR code for quick verification
38. **No passport custom branding** — no org-specific passport theming
39. **No passport comparison view** — no side-by-side comparison of two passport versions
40. **No passport change notifications** — no alerts when passport data changes
41. **No passport analytics** — no tracking of who viewed/verified snapshots
42. **No passport field-level sharing UI** — `visible_fields` exists but no frontend toggle
43. **No passport template system** — no customizable passport layouts
44. **No granular consent per viewer** — `specific_employer` scope exists but no per-employer field selection
45. **No passport embedding** — no embeddable widget for external sites
46. **No passport social proof badges** — no "Verified by OpenSkill" badge for websites
47. **No passport revision history UI** — no timeline of passport changes
48. **No passport completeness action items on dashboard** — service exists but not wired to dashboard
49. **No snapshot comparison** — no diff view between two snapshots
50. **No passport data minimization by context** — same fields shown regardless of viewing context

## D. Assessment & Credentials (15 gaps)

51. **No assessment question bank** — no reusable question library for assessments
52. **No assessment proctoring** — no monitoring during assessment runs
53. **No assessment rubric templates** — rubrics are ad-hoc per assessment
54. **No assessment analytics dashboard** — no pass/fail rates, difficulty analysis
55. **No assessment adaptive difficulty** — no item response theory or adaptive testing
56. **No credential badge image generation** — `badge_sharing.py` generates URLs but no actual badge SVG/PNG
57. **No credential verification landing page** — `/verify/credential/{id}` doesn't exist (only passport verify)
58. **No credential revocation notification** — no email/notification when credential is revoked
59. **No credential renewal workflow** — `revalidation_at` exists but no renewal flow
60. **No credential stacking progress visualization** — pathway page exists but no visual progress tree
61. **No credential endorsement by issuer** — issuer can't add notes after issuance
62. **No credential template designer** — no UI to design credential appearance
63. **No assessment scheduling** — no way to schedule an assessment for a future date
64. **No peer assessment flow** — peer review creates evidence but no structured peer assessment
65. **No assessment result appeal process** — no way to challenge assessment results

## E. Matching & Search (15 gaps)

66. **No semantic search** — search uses ILIKE only, no vector/embedding search
67. **No saved search email alerts** — saved searches have `notify_frequency` but no delivery mechanism
68. **No search filters for compensation range** — no salary/compensation filtering
69. **No search filters for experience level** — no years-of-experience filtering
70. **No search filters for organization size** — no company size filtering
71. **No search result caching** — every search hits the database
72. **No search analytics** — no tracking of popular searches, zero-result queries
73. **No match score explanation detail page** — match reasons shown as chips, no detailed breakdown
74. **No match result export** — no CSV export of match results
75. **No match quality feedback loop** — no "was this match helpful?" rating
76. **No match result filtering by tier** — can't filter to "strong match" only
77. **No geographic proximity matching** — no distance-based filtering
78. **No match notification when new opportunities match** — no proactive "new match" alerts
79. **No Boolean search operators** — no AND/OR/NOT search syntax
80. **No search suggestion/autocomplete** — no typeahead for search queries

## F. Application Pipeline (15 gaps)

81. **No application form builder** — no custom questions per opportunity
82. **No application auto-screening rules** — no automated initial filtering
83. **No application duplicate detection** — only checks same user+opportunity, not similar applications
84. **No application notes/tags by candidate** — candidate can't add notes to their own applications
85. **No application withdrawal reason collection** — no structured withdrawal reasons
86. **No application timeline on frontend** — `StatusStepper` exists but no detailed timeline with dates
87. **No application batch actions for employers** — no multi-select reject/advance
88. **No application email notifications with templates** — notifications are in-app only, no email
89. **No application status change webhooks delivery** — events recorded but not delivered via HTTP
90. **No application reference check workflow** — no reference collection/verification
91. **No application score/ranking for employers** — match score not shown on application list
92. **No application stage time-limit enforcement** — no automatic expiry per stage
93. **No application document upload** — `resume_asset_id` exists but no upload flow
94. **No application cover letter preview** — `cover_note` not rendered with formatting
95. **No application kanban board for employers** — no drag-and-drop pipeline view

## G. Interview & Scheduling (10 gaps)

96. **No calendar provider integration** — .ics files generated but no Google/Outlook OAuth
97. **No interviewer availability management** — no availability calendar per interviewer
98. **No candidate self-scheduling** — no shareable booking link
99. **No interview reminder notifications** — no automatic reminders before interview
100.  **No video interview link generation** — `meeting_url` is manual entry, no Zoom/Meet integration
101.  **No interview feedback form templates** — scorecards exist but no per-stage form templates
102.  **No interview debrief workflow** — no structured post-interview team discussion
103.  **No interview panel scheduling** — no multi-interviewer coordination
104.  **No interview no-show tracking** — no status for missed interviews
105.  **No interview recording consent management** — no consent tracking for recorded interviews

## H. Offers & Onboarding (10 gaps)

106. **No offer letter PDF generation** — offer data stored but no PDF rendering
107. **No offer e-signature** — no digital signature workflow (DocuSign-like)
108. **No offer comparison for candidates** — candidates can't compare multiple offers
109. **No offer deadline reminder** — no notification before offer expires
110. **No onboarding task assignment notification** — no alerts when tasks are assigned
111. **No onboarding document e-sign** — no signature collection for onboarding documents
112. **No onboarding progress dashboard for employer** — service exists but no frontend
113. **No onboarding buddy/mentor assignment flow** — field exists but no workflow
114. **No onboarding checklist completion celebration** — no gamification on completion
115. **No probation period tracking** — no probation milestones or review dates

## I. Employer Features (15 gaps)

116. **No employer job posting distribution** — no publishing to external job boards
117. **No employer analytics export** — dashboard is view-only, no export
118. **No employer team/department hierarchy** — flat org structure, no departments
119. **No employer role-based access control UI** — roles exist but no management interface
120. **No employer billing for job postings** — no pay-per-post or subscription
121. **No employer candidate pipeline stages customization** — fixed 11-state machine
122. **No employer talent pool automation rules** — pool `rule_config` exists but not evaluated
123. **No employer career page customization UI** — career page exists but no visual editor
124. **No employer interview kit/guide** — no structured interview preparation materials
125. **No employer compliance reporting** — no EEO/diversity compliance reports
126. **No employer candidate relationship timeline** — CRM notes exist but no relationship timeline
127. **No employer co-hiring across orgs** — no shared hiring pipeline between organizations
128. **No employer requisition approval workflow** — no approval chain for new job postings
129. **No employer brand health metrics** — reputation score exists but no trend tracking
130. **No employer event/career fair management** — no virtual career fair functionality

## J. Candidate Features (15 gaps)

131. **No candidate profile video introduction** — no video upload/embed
132. **No candidate availability calendar** — `availability_status` is a string, not a calendar
133. **No candidate job alert preferences** — no saved preference for automatic matching
134. **No candidate application tracker dashboard** — applications page exists but no Sankey/funnel
135. **No candidate salary expectation setting** — no compensation preference field
136. **No candidate skill gap auto-detection** — learning plan requires manual trigger
137. **No candidate portfolio drag-and-drop reorder** — reorder service exists but no DnD UI
138. **No candidate work sample upload** — portfolio items have URLs but no file upload
139. **No candidate peer connection/networking** — no ability to connect with other candidates
140. **No candidate mentorship matching** — no mentor/mentee pairing system
141. **No candidate interview preparation tips** — no stage-specific preparation guidance
142. **No candidate progress gamification** — no badges/streaks/achievements for platform activity
143. **No candidate profile import from LinkedIn** — no OAuth import flow
144. **No candidate mobile-optimized experience** — pages are responsive but no PWA features
145. **No candidate dark mode preference persistence** — uses system theme only

## K. Communication (10 gaps)

146. **No email notification delivery** — notifications are in-app only
147. **No push notifications** — no browser/mobile push
148. **No SMS notifications** — no phone-based alerts
149. **No notification digest (daily/weekly summary)** — no batched notification emails
150. **No message attachments upload** — message attachments are links only
151. **No message read receipt visibility** — read_at tracked but not shown to sender
152. **No message templates for common responses** — no quick-reply templates
153. **No bulk messaging for employers** — no mass outreach to pool members
154. **No message translation** — no auto-translate for cross-language communication
155. **No in-app chat (real-time)** — messages are async HTTP, no WebSocket

## L. Analytics & Reporting (15 gaps)

156. **No custom report builder** — all reports are pre-defined
157. **No scheduled report delivery** — no email scheduled reports
158. **No analytics dashboard embedding** — no iframe/embed for external dashboards
159. **No cohort analysis** — no comparison of outcomes by cohort group
160. **No funnel drop-off analysis with reasons** — dropoffs counted but no reason collection
161. **No time-to-fill by opportunity type** — hiring analytics not segmented by type
162. **No source attribution tracking** — no UTM-style tracking for candidate sources
163. **No ROI calculation per learning content** — skill ROI is theoretical, not outcome-based
164. **No predictive hiring success model** — no ML model for hire quality prediction
165. **No benchmark comparisons** — no industry/peer benchmarking
166. **No real-time analytics streaming** — all analytics are batch/on-demand
167. **No analytics access control** — any authenticated user can see intelligence endpoints
168. **No analytics data warehouse export** — no integration with Snowflake/BigQuery
169. **No custom KPI tracking** — no configurable key performance indicators
170. **No analytics annotation/commenting** — no ability to annotate data points

## M. Integration & API (10 gaps)

171. **No API key management** — no per-org API keys for external integration
172. **No OAuth2 provider for third-party apps** — no auth server for external apps
173. **No HRIS integration schema** — no standard schema for Workday/BambooHR sync
174. **No ATS integration connectors** — no Greenhouse/Lever/iCIMS connectors
175. **No calendar provider OAuth** — no Google Calendar/Outlook integration
176. **No Slack/Teams integration** — no chat platform notifications
177. **No webhook retry queue persistence** — retry delays are in-memory, not Redis/DB
178. **No webhook payload signature verification endpoint** — no public endpoint for receivers to verify
179. **No API rate limit per endpoint** — rate limit is global per user, not per endpoint
180. **No GraphQL API** — REST only, no GraphQL alternative

## N. Security & Compliance (10 gaps)

181. **No two-factor authentication for employer actions** — no MFA for sensitive operations
182. **No audit log export** — activity log has no export endpoint
183. **No data classification labels** — no sensitivity labels on fields
184. **No IP allowlist for API access** — no per-org IP restrictions
185. **No session management UI** — no view of active sessions
186. **No role escalation prevention** — no detection of unusual privilege changes
187. **No data breach notification workflow** — no automated breach response
188. **No cookie consent management** — no GDPR cookie banner integration
189. **No SOC 2 compliance evidence collection** — no automated compliance artifacts
190. **No penetration test scheduling** — no automated security scanning

## O. Platform Operations (10 gaps)

191. **No feature flag system** — no ability to toggle features per org
192. **No A/B testing framework** — no experimentation infrastructure
193. **No health check dashboard** — `/health` endpoint exists but no monitoring UI
194. **No database migration dry-run** — no preview of migration effects
195. **No system status page** — no public uptime/status page
196. **No automated backup verification** — no backup testing workflow
197. **No multi-region deployment support** — no region-aware data handling
198. **No usage metering per org** — no tracking of API calls per organization
199. **No tenant data isolation verification** — no automated cross-tenant test suite
200. **No documentation site generation** — ADR exists but no auto-generated API docs site
