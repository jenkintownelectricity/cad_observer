#!/usr/bin/env python3
"""
CAD Observer - Persistent Logging Script
Stores CAD observation data locally and/or to Supabase for cross-session learning.
"""

import json
import os
import argparse
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURATION - Update these for your setup
# ============================================================

# Local storage path (create this directory)
LOCAL_STORAGE_PATH = Path.home() / ".cad-observer" / "observations.jsonl"

# Supabase configuration (set these environment variables)
# SUPABASE_URL=your-project-url
# SUPABASE_KEY=your-anon-key

SUPABASE_TABLE = "cad_observations"

# ============================================================
# LOCAL STORAGE FUNCTIONS
# ============================================================

def ensure_local_storage():
    """Create local storage directory if it doesn't exist."""
    LOCAL_STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOCAL_STORAGE_PATH.exists():
        LOCAL_STORAGE_PATH.touch()

def log_local(observation: dict) -> dict:
    """Append observation to local JSONL file."""
    ensure_local_storage()
    
    # Add metadata
    observation["logged_at"] = datetime.utcnow().isoformat()
    observation["storage"] = "local"
    
    with open(LOCAL_STORAGE_PATH, "a") as f:
        f.write(json.dumps(observation) + "\n")
    
    return {"status": "success", "storage": "local", "path": str(LOCAL_STORAGE_PATH)}

def read_local_observations(limit: int = 100) -> list:
    """Read recent observations from local storage."""
    ensure_local_storage()
    
    observations = []
    with open(LOCAL_STORAGE_PATH, "r") as f:
        for line in f:
            if line.strip():
                observations.append(json.loads(line))
    
    return observations[-limit:]  # Return most recent

def get_local_stats() -> dict:
    """Get statistics about local observations."""
    observations = read_local_observations(limit=10000)
    
    if not observations:
        return {"total_sessions": 0, "message": "No observations yet"}
    
    # Aggregate stats
    all_commands = []
    all_layers = []
    session_types = {}
    
    for obs in observations:
        if "observations" in obs:
            all_commands.extend(obs["observations"].get("commands_detected", []))
            all_layers.extend(obs["observations"].get("layer_patterns", []))
        
        st = obs.get("session_type", "unknown")
        session_types[st] = session_types.get(st, 0) + 1
    
    # Count frequencies
    command_freq = {}
    for cmd in all_commands:
        command_freq[cmd] = command_freq.get(cmd, 0) + 1
    
    return {
        "total_sessions": len(observations),
        "session_types": session_types,
        "top_commands": sorted(command_freq.items(), key=lambda x: -x[1])[:10],
        "unique_layers": list(set(all_layers)),
        "first_observation": observations[0].get("logged_at") if observations else None,
        "last_observation": observations[-1].get("logged_at") if observations else None
    }

# ============================================================
# SUPABASE STORAGE FUNCTIONS
# ============================================================

def get_supabase_client():
    """Initialize Supabase client from environment variables."""
    try:
        from supabase import create_client
    except ImportError:
        raise ImportError("Install supabase-py: pip install supabase")
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Set SUPABASE_URL and SUPABASE_KEY environment variables")
    
    return create_client(url, key)

def log_supabase(observation: dict) -> dict:
    """Insert observation into Supabase."""
    client = get_supabase_client()
    
    # Prepare record
    record = {
        "timestamp": observation.get("timestamp", datetime.utcnow().isoformat()),
        "session_type": observation.get("session_type", "unknown"),
        "project_context": observation.get("project_context", ""),
        "observations": json.dumps(observation.get("observations", {})),
        "confidence": observation.get("confidence", 0.5),
        "questions": json.dumps(observation.get("questions_for_user", [])),
        "raw_data": json.dumps(observation)
    }
    
    result = client.table(SUPABASE_TABLE).insert(record).execute()
    
    return {"status": "success", "storage": "supabase", "id": result.data[0]["id"] if result.data else None}

def read_supabase_observations(limit: int = 100) -> list:
    """Read recent observations from Supabase."""
    client = get_supabase_client()
    
    result = client.table(SUPABASE_TABLE)\
        .select("*")\
        .order("timestamp", desc=True)\
        .limit(limit)\
        .execute()
    
    # Parse JSON fields back
    observations = []
    for row in result.data:
        obs = json.loads(row.get("raw_data", "{}"))
        obs["id"] = row.get("id")
        observations.append(obs)
    
    return observations

# ============================================================
# SUPABASE TABLE SETUP SQL
# ============================================================

SUPABASE_SETUP_SQL = """
-- Run this in Supabase SQL Editor to create the table

CREATE TABLE IF NOT EXISTS cad_observations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_type TEXT,
    project_context TEXT,
    observations JSONB,
    confidence FLOAT,
    questions JSONB,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_cad_observations_timestamp 
ON cad_observations(timestamp DESC);

-- Enable RLS (optional, for security)
ALTER TABLE cad_observations ENABLE ROW LEVEL SECURITY;

-- Policy to allow inserts (adjust as needed)
CREATE POLICY "Allow inserts" ON cad_observations
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow reads" ON cad_observations
FOR SELECT USING (true);
"""

# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="CAD Observer - Log and retrieve observations")
    parser.add_argument("--supabase", action="store_true", help="Use Supabase instead of local storage")
    parser.add_argument("--data", type=str, help="JSON observation data to log")
    parser.add_argument("--read", action="store_true", help="Read recent observations")
    parser.add_argument("--stats", action="store_true", help="Show observation statistics")
    parser.add_argument("--setup-sql", action="store_true", help="Print Supabase setup SQL")
    parser.add_argument("--limit", type=int, default=100, help="Limit for read operations")
    
    args = parser.parse_args()
    
    # Print setup SQL
    if args.setup_sql:
        print(SUPABASE_SETUP_SQL)
        return
    
    # Log new observation
    if args.data:
        observation = json.loads(args.data)
        
        if args.supabase:
            result = log_supabase(observation)
        else:
            result = log_local(observation)
        
        print(json.dumps(result, indent=2))
        return
    
    # Read observations
    if args.read:
        if args.supabase:
            observations = read_supabase_observations(args.limit)
        else:
            observations = read_local_observations(args.limit)
        
        print(json.dumps(observations, indent=2))
        return
    
    # Show stats
    if args.stats:
        stats = get_local_stats()
        print(json.dumps(stats, indent=2))
        return
    
    # Default: show help
    parser.print_help()

if __name__ == "__main__":
    main()
