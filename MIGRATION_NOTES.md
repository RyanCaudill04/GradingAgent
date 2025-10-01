# Database Migration Notes

## Changes Made

The Criteria table schema has been updated to support the new Gemini-based grading system:

### Old Schema
```python
class Criteria(Base):
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    text = Column(Text)  # Old field
```

### New Schema
```python
class Criteria(Base):
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    natural_language_rubric = Column(Text)  # New field
    regex_checks = Column(JSON, nullable=True)  # New field
```

## Migration Steps

### Option 1: Fresh Start (Recommended for Development)

If you don't have important data to preserve:

```bash
# Stop all services
make down

# Remove volumes (this will delete all data)
docker-compose down -v

# Rebuild and start
make up

# The database will be recreated with the new schema
```

### Option 2: Manual Migration (If You Have Data to Preserve)

1. **Backup your database first:**
   ```bash
   ./backup-db.sh
   ```

2. **Connect to the database:**
   ```bash
   docker-compose exec db psql -U postgres -d postgres
   ```

3. **Run migration SQL:**
   ```sql
   -- Add new columns
   ALTER TABLE criteria ADD COLUMN natural_language_rubric TEXT;
   ALTER TABLE criteria ADD COLUMN regex_checks JSON;

   -- Migrate existing data (move 'text' to 'natural_language_rubric')
   UPDATE criteria SET natural_language_rubric = text WHERE text IS NOT NULL;

   -- Drop old column
   ALTER TABLE criteria DROP COLUMN text;
   ```

4. **Exit psql:**
   ```
   \q
   ```

5. **Restart services:**
   ```bash
   make rebuild-services
   ```

### Option 3: Using Alembic (Production - TODO)

For production environments, we should set up Alembic for proper migrations:

```bash
# Install alembic (add to requirements.txt)
pip install alembic

# Initialize alembic
alembic init alembic

# Configure alembic.ini with your database URL

# Create migration
alembic revision --autogenerate -m "Update criteria schema for Gemini integration"

# Apply migration
alembic upgrade head
```

## Verification

After migration, verify the schema:

```bash
docker-compose exec db psql -U postgres -d postgres -c "\d criteria"
```

You should see:
- `natural_language_rubric` (text)
- `regex_checks` (json)

## Rollback

If something goes wrong and you have a backup:

```bash
./restore-db.sh
# Select your backup file when prompted
```
