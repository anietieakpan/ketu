# Database Setup and Configuration

## Database Architecture

### Primary Database (license_plates.db)
```sql
CREATE TABLE detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    plate_text TEXT NOT NULL,
    confidence REAL NOT NULL,
    x1 INTEGER, y1 INTEGER,
    x2 INTEGER, y2 INTEGER,
    source_type TEXT,
    persistence_count INTEGER
);

-- Indexes for performance
CREATE INDEX idx_detections_plate ON detections(plate_text);
CREATE INDEX idx_detections_time ON detections(timestamp);
CREATE INDEX idx_detections_confidence ON detections(confidence);
```

### Analysis Database (analysis.db)
```sql
-- Following patterns table
CREATE TABLE following_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_number TEXT NOT NULL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    detection_count INTEGER NOT NULL,
    confidence_score REAL NOT NULL,
    pattern_type TEXT NOT NULL,
    analysis_timestamp TEXT NOT NULL
);

-- Analysis results table
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id INTEGER NOT NULL,
    plate_number TEXT NOT NULL,
    analysis_type TEXT NOT NULL,
    result_data TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES following_patterns(id)
);
```

## Database Optimization

### Performance Settings
```sql
-- Enable WAL mode for better write performance
PRAGMA journal_mode = WAL;

-- Adjust synchronization settings
PRAGMA synchronous = NORMAL;

-- Optimize cache
PRAGMA cache_size = -2000000;  -- Approximately 2GB of cache
PRAGMA temp_store = MEMORY;

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;
```

### Index Optimization
```sql
-- Create optimized indexes for common queries
CREATE INDEX idx_patterns_time ON following_patterns(first_seen, last_seen);
CREATE INDEX idx_results_analysis ON analysis_results(analysis_id, timestamp);
CREATE INDEX idx_confidence_plate ON detections(confidence, plate_text);
```

## Database Maintenance

### Automatic Cleanup
```python
def cleanup_old_records():
    """Remove records older than retention period"""
    with sqlite3.connect('license_plates.db') as conn:
        retention_days = 30
        conn.execute('''
            DELETE FROM detections 
            WHERE datetime(timestamp) < datetime('now', '-? days')
        ''', (retention_days,))
        conn.commit()
```

### Database Optimization
```python
def optimize_database():
    """Perform database optimization"""
    with sqlite3.connect('license_plates.db') as conn:
        # Analyze for query optimization
        conn.execute('ANALYZE')
        
        # Rebuild indexes
        conn.execute('REINDEX')
        
        # Compact database
        conn.execute('VACUUM')
```

## Backup and Recovery

### Backup Configuration
```python
class DatabaseBackup:
    def create_backup(self):
        """Create database backup"""
        backup_path = f"backup/license_plates_{datetime.now():%Y%m%d}.db"
        with sqlite3.connect('license_plates.db') as conn:
            backup = sqlite3.connect(backup_path)
            conn.backup(backup)
            backup.close()

    def restore_from_backup(self, backup_path):
        """Restore database from backup"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup not found: {backup_path}")
            
        # Create temporary database
        temp_db = f"temp_{int(time.time())}.db"
        
        try:
            # Restore to temporary database first
            with sqlite3.connect(backup_path) as backup:
                temp = sqlite3.connect(temp_db)
                backup.backup(temp)
                temp.close()
            
            # Verify temporary database
            if self._verify_database(temp_db):
                # Replace main database
                os.replace(temp_db, 'license_plates.db')
            else:
                raise ValueError("Database verification failed")
                
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
```

## Data Migration

### Migration Scripts
```python
class DatabaseMigration:
    def __init__(self):
        self.migrations = []
        self._load_migrations()

    def run_migrations(self):
        """Run pending database migrations"""
        with sqlite3.connect('license_plates.db') as conn:
            current_version = self._get_db_version(conn)
            pending_migrations = [m for m in self.migrations 
                                if m.version > current_version]
            
            for migration in pending_migrations:
                try:
                    migration.apply(conn)
                    self._update_db_version(conn, migration.version)
                except Exception as e:
                    logger.error(f"Migration failed: {str(e)}")
                    conn.rollback()
                    raise
```

## Monitoring and Logging

### Database Metrics
```python
class DatabaseMonitor:
    def collect_metrics(self):
        """Collect database performance metrics"""
        with sqlite3.connect('license_plates.db') as conn:
            return {
                'size': self._get_db_size(),
                'table_counts': self._get_table_counts(conn),
                'index_stats': self._get_index_stats(conn),
                'query_stats': self._get_query_stats(conn)
            }

    def _get_table_counts(self, conn):
        """Get record counts for all tables"""
        tables = conn.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table'
        ''').fetchall()
        
        counts = {}
        for (table,) in tables:
            count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            counts[table] = count
        return counts
```

## Security Configuration

### Access Control
```python
class DatabaseSecurity:
    def setup_security(self):
        """Configure database security settings"""
        with sqlite3.connect('license_plates.db') as conn:
            # Enable encryption (if using SQLCipher)
            conn.execute('PRAGMA key = ?', (self.encryption_key,))
            
            # Set secure delete
            conn.execute('PRAGMA secure_delete = ON')
            
            # Enable trusted schema
            conn.execute('PRAGMA trusted_schema = OFF')
```

### Audit Logging
```python
class DatabaseAuditor:
    def setup_audit_logging(self):
        """Setup audit logging for database operations"""
        with sqlite3.connect('license_plates.db') as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    user_id TEXT,
                    details TEXT
                )
            ''')
```

## Troubleshooting

### Common Issues and Solutions
1. Database Locked
```python
def handle_db_locked():
    """Handle database locked errors"""
    # Increase timeout
    conn = sqlite3.connect('license_plates.db', timeout=30)
    
    # Check for stuck transactions
    with conn:
        conn.execute('PRAGMA busy_timeout = 30000')
```

2. Corruption Recovery
```python
def recover_corrupt_database():
    """Recover from database corruption"""
    try:
        # Attempt integrity check
        with sqlite3.connect('license_plates.db') as conn:
            conn.execute('PRAGMA integrity_check')
            
    except sqlite3.DatabaseError:
        # Recover using backup
        self._recover_from_backup()
```

### Performance Diagnostics
```python
def diagnose_performance():
    """Diagnose database performance issues"""
    with sqlite3.connect('license_plates.db') as conn:
        # Check index usage
        conn.execute('ANALYZE')
        index_stats = conn.execute('PRAGMA index_info').fetchall()
        
        # Check for slow queries
        conn.execute('PRAGMA query_plan')
        
        # Check for fragmentation
        page_count = conn.execute('PRAGMA page_count').fetchone()[0]
        free_pages = conn.execute('PRAGMA freelist_count').fetchone()[0]
        
        return {
            'index_stats': index_stats,
            'fragmentation': free_pages / page_count,
            'page_size': conn.execute('PRAGMA page_size').fetchone()[0]
        }
```

This completes the database_setup.md documentation with all necessary details for setup, configuration, maintenance, and troubleshooting.