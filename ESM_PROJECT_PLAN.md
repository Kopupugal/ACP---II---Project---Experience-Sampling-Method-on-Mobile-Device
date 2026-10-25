# LLM-Powered ESM Platform: Project Plan and Requirements Gap Analysis

## Important limitation

The supplied SharePoint link requires University of Oulu authentication. The document itself could not be downloaded; only the sign-in page was accessible. The repository currently contains only a minimal `README.md`, with no implementation to inspect.

This document is therefore a domain-based architecture and gap analysis for an LLM-powered Experience Sampling Method platform. A direct `.docx` upload would allow a precise requirement-by-requirement comparison.

## 1. Proposed system components

### Participant mobile application

- User registration and consent
- Study joining
- Survey notifications
- Dynamic questionnaires
- Offline completion and synchronization
- Progress, reminders, and withdrawal
- Sensor/context permission management

### Researcher/admin web portal

- Study creation and configuration
- Participant management
- Questionnaire and condition builder
- Sampling schedule configuration
- Context rules and triggers
- Live monitoring
- Data export
- Dashboard and visualizations
- Audit logs

### Backend API

- Authentication and authorization
- Study and participant management
- Survey delivery
- Response submission
- Context data ingestion
- LLM orchestration
- Reporting and exports

### Scheduling and notification service

- Fixed-time sampling
- Random sampling within time windows
- Event-triggered sampling
- Context-triggered sampling
- Quiet hours
- Time zones
- Retry and escalation policies
- Push notifications

### Context-awareness engine

- Location
- Activity and motion
- Device usage
- Calendar events
- Time and date
- Weather
- Connectivity
- User-defined context
- Privacy-aware filtering

### LLM and agent layer

- Question generation and adaptation
- Context interpretation
- Response clarification
- Personalization
- Researcher-facing summarization
- Anomaly and data-quality detection
- Safety escalation

### Data and analytics layer

- Transactional database
- Time-series/context storage
- Analytics warehouse or reporting database
- Data export pipeline
- Data retention and deletion jobs

### Platform services

- Identity provider
- Push notification provider
- Object storage
- Secrets management
- Logging and monitoring
- Backup and disaster recovery

## 2. Step-by-step project plan

### Phase 1: Requirements clarification

Define:

- Participant and researcher roles
- Study lifecycle
- Required platforms: Android, iOS, and web
- Supported sensors and context sources
- Whether the LLM operates during a study or only after data collection
- Human approval requirements for generated questions
- Data retention periods
- Ethical approval and consent requirements
- Required export formats
- Expected participant count and response volume

Create:

- User stories
- Acceptance criteria
- Privacy impact assessment
- Threat model
- Architecture decision records
- MVP and non-MVP scope

### Phase 2: Core study model

Implement the foundational entities:

- Users
- Roles
- Studies
- Study memberships
- Consent records
- Questionnaires
- Questions
- Question options
- Survey versions
- Sampling plans
- Sampling windows
- Notifications
- Survey instances
- Responses
- Context observations
- LLM executions
- Audit events

Questionnaires must be versioned. A study must reference the exact questionnaire version used for each participant.

### Phase 3: Authentication and consent

Implement:

- Email or university identity login
- Researcher and participant roles
- Study invitation and enrollment
- Consent collection
- Consent withdrawal
- Device permissions
- Data deletion requests
- Role-based access control
- Study-level data isolation

Consent should separately cover:

- Survey responses
- Location data
- Activity data
- Device usage data
- LLM processing
- Data sharing with researchers
- Long-term storage

### Phase 4: Researcher portal

Build this workflow:

1. Create a study.
2. Define objectives and target population.
3. Create questionnaire templates.
4. Configure sampling schedules.
5. Define context conditions.
6. Configure LLM behavior.
7. Invite participants.
8. Launch the study.
9. Monitor participation.
10. Pause, modify, or end the study.
11. Export and analyze data.

Changes to a running study should create a new configuration version instead of silently changing historical behavior.

### Phase 5: Participant application

Implement:

- Enrollment
- Consent screens
- Study instructions
- Notification handling
- Survey presentation
- Conditional questions
- LLM-generated follow-up questions
- Offline mode
- Draft responses
- Synchronization
- Missed survey handling
- Accessibility
- Localization
- Battery-conscious context collection

The app must distinguish between required, optional, AI-generated, context-triggered, and previous-answer-based questions.

### Phase 6: Sampling and context engine

Start with a deterministic rule engine before introducing complex AI behavior.

Example rule:

> If a participant has been stationary for at least 30 minutes, it is between 09:00 and 21:00, and no survey was completed within the previous hour, issue a survey.

Each rule should define:

- Trigger
- Conditions
- Required context
- Confidence threshold
- Cooldown
- Quiet hours
- Priority
- Maximum daily frequency
- Expiry
- Fallback behavior
- Audit explanation

Context-dependent behavior must handle:

- Context confidence scores
- Missing or stale context
- Conflicting rules
- User privacy settings
- Battery limits
- Collection frequency
- Local versus server-side processing
- Uncertainty

The LLM must not directly trigger unrestricted notifications. A policy engine must enforce frequency, privacy, and study constraints.

### Phase 7: LLM agent architecture

Use multiple controlled agents rather than one general-purpose agent.

#### Question-generation agent

- Generate questions only from researcher-approved templates
- Adapt wording to participant context
- Respect question types and answer scales
- Avoid introducing new constructs
- Return structured JSON
- Provide rationale and confidence

#### Context interpretation agent

- Convert raw context into structured signals
- Detect relevant events
- Identify uncertainty
- Avoid unnecessary sensitive inferences

#### Personalization agent

- Select approved question variants
- Adjust language and difficulty
- Use prior responses only within the study scope
- Avoid psychological diagnosis

#### Response follow-up agent

- Ask a limited follow-up question
- Detect ambiguous responses
- Remain optional where appropriate
- Avoid leading or judgmental wording

#### Researcher summary agent

- Summarize aggregated data
- Cite the underlying response period
- Separate observations from interpretations
- Avoid presenting correlations as causation

#### Data-quality agent

- Detect duplicate, rushed, contradictory, or impossible responses
- Flag data for researcher review
- Never silently delete participant data

#### Safety agent

- Detect predefined safety-related signals
- Apply a configured escalation policy
- Show emergency resources where required
- Never pretend to provide clinical care

Every agent needs:

- A narrowly defined responsibility
- Structured input/output schemas
- Prompt versioning
- Model version tracking
- Token and cost limits
- Timeout and retry handling
- Human-review rules
- Fallback behavior
- Full audit logging

## 3. Recommended database structure

PostgreSQL is suitable for core transactional data.

### Identity and access

- `users`
- `roles`
- `user_roles`
- `researchers`
- `participants`
- `devices`
- `sessions`
- `consents`
- `permission_grants`

### Study management

- `studies`
- `study_memberships`
- `study_configurations`
- `study_versions`
- `study_invitations`
- `study_events`

### Questionnaires

- `questionnaires`
- `questionnaire_versions`
- `questions`
- `question_options`
- `questionnaire_rules`
- `questionnaire_assignments`

### Sampling

- `sampling_plans`
- `sampling_windows`
- `sampling_rules`
- `survey_instances`
- `survey_deliveries`
- `notification_attempts`

### Responses

- `responses`
- `response_answers`
- `response_metadata`
- `response_edits`
- `response_flags`

### Context

- `context_observations`
- `context_sources`
- `context_permissions`
- `context_features`
- `context_events`

Context data should be separated from survey answers so access can be controlled independently.

### AI and audit

- `agent_definitions`
- `prompt_versions`
- `llm_executions`
- `llm_inputs`
- `llm_outputs`
- `ai_generated_questions`
- `human_reviews`
- `safety_events`
- `audit_logs`

Every LLM execution should store the model name, prompt version, input references, output, latency, cost, and validation status.

## 4. Requirements probably missing from the source document

### Privacy and ethics

- Consent versioning
- Withdrawal behavior
- Data deletion
- Data minimization
- Sensitive-data classification
- GDPR compliance
- Research ethics approval
- Participant de-identification
- Pseudonymization key management
- Data residency
- Researcher access restrictions

### Context behavior

- Context uncertainty
- Context freshness
- Sensor failure
- Offline context collection
- Battery impact
- Location accuracy
- Context permission revocation
- Conflicting context signals
- Quiet hours
- Notification fatigue
- Cooldowns and daily limits

### LLM governance

- Hallucination prevention
- Prompt injection protection
- Sensitive-data leakage prevention
- Human approval of generated questions
- Prompt and model versioning
- Reproducibility
- Cost limits
- Rate limits
- Model fallback
- Structured-output validation
- AI disclosure to participants
- Prohibition of diagnosis or unsupported conclusions

### Mobile reliability

- Offline mode
- Duplicate submission prevention
- Clock changes
- Time-zone changes
- App force termination
- Device replacement
- Push-token rotation
- Background execution limits
- Synchronization conflicts
- App updates during active studies

### Study methodology

- Randomization
- Counterbalancing
- Experimental groups
- Question order randomization
- Questionnaire branching
- Missing-data definitions
- Compliance metrics
- Participant burden limits
- Study pause/resume
- Configuration immutability
- Pilot studies

### Security

- Encryption in transit and at rest
- Key rotation
- MFA for researchers
- Session expiration
- Rate limiting
- Audit logging
- Backup encryption
- Vulnerability scanning
- Dependency management
- Incident response

### Analytics

- Completion rate
- Response latency
- Notification delivery rate
- Participant burden
- Missingness analysis
- Context-trigger frequency
- AI intervention frequency
- Data-quality dashboards
- Export reproducibility
- Separation of raw and derived data

### Operations

- Monitoring and alerting
- Database backups
- Disaster recovery
- Migration strategy
- Deployment environments
- Feature flags
- Cost monitoring
- Error tracking
- Support tools
- Data retention jobs

## 5. Recommended MVP

### Include in the first release

- Participant mobile app
- Researcher web portal
- Authentication and consent
- Fixed and random sampling
- Basic push notifications
- Questionnaire versioning
- Offline response queue
- PostgreSQL database
- CSV and JSON export
- Basic dashboard
- Simple rule-based context triggers
- One constrained LLM feature: approved follow-up question generation
- Audit logging
- Data deletion and study withdrawal

### Defer until after the pilot

- Fully autonomous agents
- Complex behavioral inference
- Broad sensor integration
- Continuous location tracking
- Automated psychological interpretation
- Cross-study participant profiling
- Real-time predictive modeling
- Unreviewed AI-generated questionnaires

## 6. Recommended implementation order

1. Requirements and ethical constraints
2. Threat model and data classification
3. Database schema and API contract
4. Authentication, roles, and consent
5. Researcher study-management portal
6. Questionnaire and versioning system
7. Participant survey experience
8. Scheduling and notifications
9. Offline synchronization
10. Basic rule-based context engine
11. Data export and analytics
12. LLM gateway and structured-output validation
13. Controlled follow-up-question agent
14. Monitoring, auditing, and security hardening
15. Pilot study
16. Usability, battery, and reliability testing
17. Production deployment

## 7. Core architectural principle

Keep study rules, privacy policies, and notification limits deterministic. Use the LLM only for bounded language and personalization tasks. This prevents the model from making uncontrolled decisions about participant contact or sensitive research data.
