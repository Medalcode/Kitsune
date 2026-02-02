# Documentation Index

**Complete documentation for Kitsune API Template.**

---

## 📚 Documentation Structure

### For Getting Started

- **[README.md](../README.md)** - Project overview, quick start, and value proposition
- **[QUICKREF.md](QUICKREF.md)** - Fast lookup for common commands and patterns

### For Implementation

- **[GUIDE.md](GUIDE.md)** - Detailed implementation patterns and best practices
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Design decisions and architectural rationale

### For Security & Operations

- **[SECURITY.md](SECURITY.md)** - Security considerations, vulnerabilities, and hardening checklist
- **[BITACORA.md](../BITACORA.md)** - Technical changelog and evolution log

---

## 🎯 Reading Path by Role

### **New Developer** (First Time Using Kitsune)

1. Read [README.md](../README.md) - Understand what Kitsune is and why
2. Follow Quick Start section - Get it running locally
3. Skim [QUICKREF.md](QUICKREF.md) - Bookmark for later
4. Read [GUIDE.md](GUIDE.md) sections 1-3 - Understand core patterns

### **Senior Developer** (Evaluating the Template)

1. Read [README.md](../README.md) - Value proposition and features
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) - Design decisions and trade-offs
3. Read [SECURITY.md](SECURITY.md) - Known vulnerabilities and mitigations
4. Review [BITACORA.md](../BITACORA.md) - Technical debt and roadmap

### **DevOps Engineer** (Deploying to Production)

1. Read [README.md](../README.md) section "Deployment"
2. Read [SECURITY.md](SECURITY.md) section "Security Checklist"
3. Review [docker-compose.yml](../docker-compose.yml) and [Dockerfile](../Dockerfile)
4. Check [BITACORA.md](../BITACORA.md) for known issues

### **Security Auditor**

1. Read [SECURITY.md](SECURITY.md) - Complete security analysis
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) section "What We Explicitly Avoid"
3. Check `src/app/core/security.py` - Implementation details
4. Review `src/app/api/deps.py` - Authentication flow

---

## 📖 Document Summaries

### README.md

**Purpose**: Project overview and getting started  
**Audience**: Everyone  
**Key Sections**:

- Why Kitsune? (value proposition)
- Quick Start (local + Docker)
- Core Features (auth, DB, observability)
- Architecture overview
- Deployment guide

---

### GUIDE.md

**Purpose**: Implementation patterns and best practices  
**Audience**: Developers extending the template  
**Key Sections**:

- Layered architecture explanation
- Step-by-step guide to add new resources
- Advanced patterns (transactions, eager loading)
- Common pitfalls and solutions

**When to read**: When adding new features or endpoints.

---

### ARCHITECTURE.md

**Purpose**: Design decisions and rationale  
**Audience**: Senior developers, architects  
**Key Sections**:

- Core principles (async-first, repository pattern, etc.)
- Trade-offs and alternatives considered
- What we explicitly avoid (CQRS, microservices, etc.)
- When to refactor (scaling triggers)

**When to read**: When evaluating the template or making architectural changes.

---

### SECURITY.md

**Purpose**: Security analysis and hardening guide  
**Audience**: Security engineers, DevOps  
**Key Sections**:

- Implemented security measures
- Known vulnerabilities (with severity ratings)
- Pre-production checklist
- Accepted risks (documented)

**When to read**: Before deploying to production or during security audits.

---

### QUICKREF.md

**Purpose**: Fast lookup for common tasks  
**Audience**: Developers (daily use)  
**Key Sections**:

- Environment setup commands
- Database operations (migrations, queries)
- Testing commands
- API usage examples (curl)
- Troubleshooting

**When to read**: Keep open while developing.

---

### BITACORA.md

**Purpose**: Technical changelog and decisions log  
**Audience**: Team members, future maintainers  
**Key Sections**:

- Version history with rationale
- Architectural decisions made
- Technical debt tracking
- Lessons learned

**When to read**: To understand why things are the way they are.

---

## 🔍 Finding Information

### "How do I...?"

| Task                          | Document        | Section               |
| ----------------------------- | --------------- | --------------------- |
| Get started locally           | README.md       | Quick Start           |
| Add a new endpoint            | GUIDE.md        | Adding a New Resource |
| Run tests                     | QUICKREF.md     | Testing               |
| Create a migration            | QUICKREF.md     | Database Operations   |
| Deploy to production          | README.md       | Deployment            |
| Fix CORS issues               | SECURITY.md     | Known Vulnerabilities |
| Understand repository pattern | ARCHITECTURE.md | Repository Pattern    |
| Generate SECRET_KEY           | QUICKREF.md     | Configuration         |

---

### "Why is it done this way?"

| Question                         | Document        | Section                  |
| -------------------------------- | --------------- | ------------------------ |
| Why async SQLAlchemy?            | ARCHITECTURE.md | Async-First              |
| Why no Unit of Work?             | ARCHITECTURE.md | No Unit of Work (Yet)    |
| Why separate schemas and models? | ARCHITECTURE.md | Pydantic for Validation  |
| Why PostgreSQL?                  | ARCHITECTURE.md | PostgreSQL as Default    |
| Why no microservices?            | ARCHITECTURE.md | What We Explicitly Avoid |

---

### "Is this secure?"

| Concern                  | Document    | Section               |
| ------------------------ | ----------- | --------------------- |
| JWT security             | SECURITY.md | Authentication        |
| Password hashing         | SECURITY.md | Password Security     |
| CORS configuration       | SECURITY.md | CORS Configuration    |
| Known vulnerabilities    | SECURITY.md | Known Vulnerabilities |
| Pre-production checklist | SECURITY.md | Security Checklist    |

---

## 📝 Contributing to Documentation

### When to Update

- **README.md**: When adding major features or changing setup process
- **GUIDE.md**: When adding new patterns or best practices
- **ARCHITECTURE.md**: When making architectural decisions
- **SECURITY.md**: When discovering vulnerabilities or adding security features
- **BITACORA.md**: After every significant change (version bump)
- **QUICKREF.md**: When adding common commands or troubleshooting steps

### Documentation Standards

1. **Be concise**: Developers read docs when stuck, not for fun
2. **Show, don't tell**: Code examples > long explanations
3. **Explain why**: Rationale is more valuable than what
4. **No tutorials**: Assume the reader is a senior developer
5. **Keep it current**: Outdated docs are worse than no docs

---

## 🔗 External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic V2 Docs](https://docs.pydantic.dev/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**Last Updated**: 2026-02-01  
**Maintained by**: Project maintainers
