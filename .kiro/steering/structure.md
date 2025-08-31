# Project Structure & Organization

## Repository Organization
This is a documentation-heavy project with comprehensive planning documents organized in the `docs/` folder. The project follows a structured approach to product development with detailed PRDs, technical specifications, and operational guidelines.

## Documentation Structure
```
docs/
├── prd_bank_soal_buku_digital_bahasa_inggris_v_1_bagian_*.md  # Core PRD (6 parts)
├── technical_infrastructure_devops.md                         # Infrastructure specs
├── team_structure_organization.md                            # Team & hiring plans
├── quality_assurance_testing.md                             # QA strategy
├── content_strategy_curriculum_design.md                    # Content guidelines
├── go_to_market_strategy.md                                 # Marketing strategy
├── legal_compliance_framework.md                           # Legal requirements
├── user_research_validation_strategy.md                    # User research
├── crisis_management_risk_response.md                      # Risk management
├── prd_improvement_suggestions_2025_08_31.md              # Improvements
└── prd_additional_considerations_2025_08_31.md            # Additional specs
```

## Expected Application Structure
Based on the documentation, the application should follow this structure:
```
src/
├── api/                    # FastAPI backend
│   ├── models/            # Database models
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── web/                   # Next.js frontend
│   ├── components/        # React components
│   ├── pages/             # Next.js pages
│   ├── hooks/             # Custom hooks
│   └── utils/             # Frontend utilities
├── content/               # Educational content
│   ├── lessons/           # Lesson definitions
│   ├── questions/         # Question bank
│   └── schemas/           # Content validation schemas
└── shared/                # Shared utilities
```

## Content Organization
- **Hierarchical Structure**: Path → Unit → Lesson → Section
- **Content Types**: Lessons (concept, examples, practice) + Questions (MCQ, Cloze, etc.)
- **Metadata**: CEFR levels (A1-B2), skills (Grammar/Vocabulary/Reading), difficulty tags
- **Bilingual Support**: Indonesian explanations with English examples

## Team Structure
- **Engineering**: Tech Lead + 4 developers + DevOps engineer
- **Product**: PM + UX/UI Designer + Content Strategist + Data Analyst  
- **Content**: 2 Authors (native EN + Indonesian educator) + Reviewer + QA
- **Growth**: Growth Manager + Digital Marketing + Content Marketing + Community

## Development Workflow
- **Agile/Scrum**: 2-week sprints with daily standups
- **Quality Gates**: Code review required, automated testing, security scans
- **Deployment**: GitOps with blue-green deployments
- **Documentation**: Confluence for technical, Notion for product/process

## Key Conventions
- **Mobile-First**: All features designed for mobile experience first
- **Bilingual**: Indonesian explanations with English examples throughout
- **Performance**: Sub-2s load times on 3G, offline capability for core content
- **Accessibility**: WCAG 2.1 AA compliance for inclusive learning
- **Content Quality**: Multi-stage validation (automated → expert → user testing)