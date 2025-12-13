# Validation Command

Before proceeding with code changes, run validation checks:

## Step 1: Environment Check
Verify .env configuration:
```bash
# Check if .env exists
ls -la roofio-backend/.env

# Verify key variables are set (without revealing values)
grep -E "^(DATABASE_URL|UPSTASH_|GROQ_|JWT_)" roofio-backend/.env | cut -d'=' -f1
```

## Step 2: Run Tests
Execute appropriate tests:

### Backend Tests
```bash
cd roofio-backend && python -m pytest
```

### Database Connection
```bash
cd roofio-backend && python test_postgres.py
```

### Redis Connection
```bash
cd roofio-backend && python test_redis.py
```

### Frontend Test
```bash
cd roofing_intelligence && python app.py
# Then verify http://127.0.0.1:5000 loads
```

## Step 3: Git Status
```bash
git status
git diff --stat
```

## Step 4: Confirm Before Proceeding
After validation:
- [ ] Environment is correctly configured
- [ ] Tests pass (or known failures documented)
- [ ] Git working directory is clean or changes are intentional

---

**Validation complete.** Safe to proceed with code changes? (y/n)
