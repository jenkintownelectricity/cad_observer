# Training Data Collection Skill

## Purpose

Systematically collect high-quality training examples from real work to continuously improve the fine-tuned roofing LLM. Every interaction is a potential training example - this skill captures, validates, and prepares data for Modal training pipeline.

## Data Collection Strategy

### What Makes Good Training Data

```
IDEAL TRAINING EXAMPLE:
┌─────────────────────────────────────────┐
│ Clear prompt (what user actually asked) │
│ + Accurate response (verified correct)  │
│ + Domain-specific (roofing knowledge)   │
│ + Properly formatted                    │
│ + Positive feedback (if available)      │
└─────────────────────────────────────────┘

AVOID:
✗ Vague or ambiguous queries
✗ Generic responses (could be any industry)
✗ Incorrect information
✗ Incomplete conversations
✗ Sensitive/private data
```

### Collection Sources

| Source | Type | Quality | Volume |
|--------|------|---------|--------|
| Chat interactions | Prompt/response pairs | High | Daily |
| RFIs written | Document generation | High | Weekly |
| Submittals prepared | Structured data | High | Weekly |
| Spec interpretations | Q&A | Very High | As needed |
| Calculations verified | Math + context | High | Daily |
| Corrections made | Learning signal | Very High | As needed |
| Shop drawing notes | Domain knowledge | High | Per project |

## Data Schema

### Core Training Example

```json
{
  "id": "train_20250115_001",
  "timestamp": "2025-01-15T14:30:00Z",
  "source": "chat_interaction",
  
  "prompt": "What's the minimum base flashing height per code?",
  "response": "Per IBC and most manufacturer requirements, base flashing must extend minimum 8 inches above the roof surface. Some specs require more - always check 07 62 00 for project-specific requirements. At parapets, terminate into reglet or under counter flashing.",
  
  "metadata": {
    "skill_used": "pm-submittals",
    "tier_handled": "modal",
    "latency_ms": 180,
    "tokens_in": 12,
    "tokens_out": 58
  },
  
  "quality": {
    "user_feedback": "positive",
    "was_corrected": false,
    "verified_accurate": true,
    "domain_relevance": "high"
  },
  
  "tags": ["flashing", "code", "specifications", "base-flashing"],
  "project_context": "general",
  "include_in_training": true
}
```

### Correction Example (High Value)

```json
{
  "id": "correction_20250115_001",
  "timestamp": "2025-01-15T15:45:00Z",
  "source": "user_correction",
  
  "original_prompt": "What's TPO seam overlap requirement?",
  "original_response": "TPO seams require 2 inch minimum overlap.",
  "corrected_response": "TPO seams require minimum 2.5 inch overlap per most manufacturers (Carlisle, Firestone, GAF). Some specs call for 3 inches. The welded seam width should be minimum 1.5 inches. Always verify against specific manufacturer requirements in approved submittal.",
  
  "correction_reason": "Original was incomplete - missing manufacturer variation and weld width",
  "corrector": "armand",
  
  "quality": {
    "learning_value": "very_high",
    "domain_relevance": "high"
  },
  
  "tags": ["tpo", "seams", "membrane", "manufacturer-specs"],
  "include_in_training": true
}
```

### Document Generation Example

```json
{
  "id": "doc_20250115_001",
  "timestamp": "2025-01-15T16:00:00Z",
  "source": "rfi_generation",
  
  "prompt": "Write an RFI about the drain sump depth shown on A-501 being only 2 inches when spec calls for 4 inch minimum",
  "response": "RFI #[XXX]\nProject: [Name]\nDate: [Date]\n\nSubject: Roof Drain Sump Depth Discrepancy - Drawing A-501\n\nDescription:\nArchitectural drawing A-501 detail 3 indicates roof drain sumps at 2\" depth. Specification section 07 54 00, paragraph 3.5.B requires minimum 4\" sump depth at all primary roof drains to ensure proper drainage and prevent ponding.\n\nRequest:\nPlease confirm:\n1. Sump depth should be 4\" minimum per specification, or\n2. Provide revised detail if 2\" depth is intended, with justification for variance from spec.\n\nImpact: Coordination with structural for sump framing. Affects drain installation sequence.\n\nAttachments:\n- Marked A-501 detail\n- Spec section 07 54 00 excerpt",
  
  "document_type": "rfi",
  "was_used": true,
  "modifications_made": "minor",
  
  "tags": ["rfi", "drains", "specifications", "conflicts"],
  "include_in_training": true
}
```

## Collection Methods

### 1. Automatic Collection (Passive)

```python
"""
training_collector.py
Runs in background, captures all interactions
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
import json
import hashlib

@dataclass
class TrainingExample:
    id: str
    timestamp: str
    source: str
    prompt: str
    response: str
    metadata: dict
    quality: dict
    tags: List[str]
    project_context: str
    include_in_training: bool = True

class TrainingCollector:
    def __init__(self, storage_path: str = "/data/training"):
        self.storage_path = storage_path
        self.buffer = []
        self.buffer_size = 100
        
    def capture(
        self,
        prompt: str,
        response: str,
        source: str = "chat",
        skill_used: str = None,
        tier: str = None,
        latency_ms: float = None,
        tags: List[str] = None,
        project: str = "general"
    ) -> str:
        """Capture an interaction as potential training data"""
        
        # Generate unique ID
        content_hash = hashlib.md5(f"{prompt}{response}".encode()).hexdigest()[:8]
        example_id = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{content_hash}"
        
        example = TrainingExample(
            id=example_id,
            timestamp=datetime.now().isoformat(),
            source=source,
            prompt=prompt,
            response=response,
            metadata={
                "skill_used": skill_used,
                "tier_handled": tier,
                "latency_ms": latency_ms,
            },
            quality={
                "user_feedback": None,  # To be filled later
                "was_corrected": False,
                "verified_accurate": None,
                "domain_relevance": self._assess_relevance(prompt, response)
            },
            tags=tags or self._auto_tag(prompt, response),
            project_context=project
        )
        
        self.buffer.append(example)
        
        if len(self.buffer) >= self.buffer_size:
            self._flush()
        
        return example_id
    
    def add_feedback(self, example_id: str, feedback: str):
        """Add user feedback to an example"""
        # Update in buffer or storage
        for ex in self.buffer:
            if ex.id == example_id:
                ex.quality["user_feedback"] = feedback
                # Positive feedback = high value training data
                if feedback == "positive":
                    ex.quality["verified_accurate"] = True
                return
        
        # If not in buffer, update in storage
        self._update_stored(example_id, {"quality.user_feedback": feedback})
    
    def record_correction(
        self,
        original_prompt: str,
        original_response: str,
        corrected_response: str,
        reason: str = None
    ) -> str:
        """Record a correction - these are VERY valuable"""
        
        example_id = f"correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store both original and corrected
        correction = {
            "id": example_id,
            "timestamp": datetime.now().isoformat(),
            "source": "user_correction",
            "original_prompt": original_prompt,
            "original_response": original_response,
            "corrected_response": corrected_response,
            "correction_reason": reason,
            "quality": {
                "learning_value": "very_high",
                "domain_relevance": "high"
            },
            "tags": self._auto_tag(original_prompt, corrected_response),
            "include_in_training": True
        }
        
        self._save_correction(correction)
        
        # Also save the corrected version as a positive example
        self.capture(
            prompt=original_prompt,
            response=corrected_response,
            source="verified_correction",
            tags=correction["tags"]
        )
        
        return example_id
    
    def _assess_relevance(self, prompt: str, response: str) -> str:
        """Auto-assess domain relevance"""
        
        roofing_terms = [
            "roof", "membrane", "tpo", "epdm", "pvc", "flashing",
            "drain", "curb", "penetration", "insulation", "polyiso",
            "spec", "07 ", "submittal", "rfi", "detail", "coping",
            "parapet", "scupper", "cricket", "tapered", "fastener"
        ]
        
        text = (prompt + " " + response).lower()
        matches = sum(1 for term in roofing_terms if term in text)
        
        if matches >= 5:
            return "high"
        elif matches >= 2:
            return "medium"
        else:
            return "low"
    
    def _auto_tag(self, prompt: str, response: str) -> List[str]:
        """Auto-generate tags from content"""
        
        tag_patterns = {
            "tpo": ["tpo", "thermoplastic"],
            "epdm": ["epdm", "rubber"],
            "pvc": ["pvc", "vinyl"],
            "mod-bit": ["modified", "mod bit", "sbs", "app"],
            "membrane": ["membrane", "sheet", "roll"],
            "flashing": ["flashing", "flash", "base flash"],
            "insulation": ["insulation", "polyiso", "iso", "eps", "xps"],
            "drains": ["drain", "scupper", "overflow"],
            "specs": ["spec", "specification", "07 "],
            "estimating": ["estimate", "takeoff", "quantity", "cost"],
            "labor": ["labor", "man-hour", "production rate", "crew"],
            "safety": ["osha", "safety", "fall protection", "ppe"],
            "submittals": ["submittal", "product data", "shop drawing"],
            "rfi": ["rfi", "request for information", "clarification"],
            "change-order": ["change order", "pco", "t&m"],
        }
        
        text = (prompt + " " + response).lower()
        tags = []
        
        for tag, patterns in tag_patterns.items():
            if any(p in text for p in patterns):
                tags.append(tag)
        
        return tags if tags else ["general"]
    
    def _flush(self):
        """Write buffer to storage"""
        import os
        
        os.makedirs(self.storage_path, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y%m%d")
        filepath = f"{self.storage_path}/examples_{date_str}.jsonl"
        
        with open(filepath, "a") as f:
            for example in self.buffer:
                f.write(json.dumps(asdict(example)) + "\n")
        
        self.buffer = []
    
    def _save_correction(self, correction: dict):
        """Save correction to dedicated file"""
        import os
        
        os.makedirs(self.storage_path, exist_ok=True)
        filepath = f"{self.storage_path}/corrections.jsonl"
        
        with open(filepath, "a") as f:
            f.write(json.dumps(correction) + "\n")
    
    def _update_stored(self, example_id: str, updates: dict):
        """Update a stored example"""
        # Implementation depends on storage backend
        pass
    
    def get_stats(self) -> dict:
        """Get collection statistics"""
        import os
        import glob
        
        files = glob.glob(f"{self.storage_path}/examples_*.jsonl")
        
        total = 0
        by_source = {}
        by_relevance = {}
        
        for filepath in files:
            with open(filepath, "r") as f:
                for line in f:
                    ex = json.loads(line)
                    total += 1
                    
                    source = ex.get("source", "unknown")
                    by_source[source] = by_source.get(source, 0) + 1
                    
                    relevance = ex.get("quality", {}).get("domain_relevance", "unknown")
                    by_relevance[relevance] = by_relevance.get(relevance, 0) + 1
        
        return {
            "total_examples": total,
            "by_source": by_source,
            "by_relevance": by_relevance,
            "corrections": self._count_corrections()
        }
    
    def _count_corrections(self) -> int:
        import os
        
        filepath = f"{self.storage_path}/corrections.jsonl"
        if not os.path.exists(filepath):
            return 0
        
        with open(filepath, "r") as f:
            return sum(1 for _ in f)


# Global collector instance
collector = TrainingCollector()
```

### 2. Manual Curation Interface

```python
"""
training_curator.py
Interface for manually curating training data
"""

class TrainingCurator:
    def __init__(self, collector: TrainingCollector):
        self.collector = collector
    
    def review_pending(self, limit: int = 20) -> List[dict]:
        """Get examples pending review"""
        # Return examples without verified_accurate flag
        pass
    
    def approve(self, example_id: str):
        """Mark example as approved for training"""
        self.collector.add_feedback(example_id, "positive")
    
    def reject(self, example_id: str, reason: str = None):
        """Reject example from training"""
        # Mark include_in_training = False
        pass
    
    def edit_and_approve(self, example_id: str, new_response: str):
        """Edit response and approve"""
        # Create correction record
        pass
    
    def bulk_approve_by_tag(self, tag: str):
        """Approve all examples with a specific tag"""
        pass
    
    def export_for_training(self, min_quality: str = "medium") -> str:
        """Export approved examples for Modal training"""
        pass
```

### 3. Project-Based Collection

```python
"""
Collect training data organized by project
"""

def capture_project_knowledge(
    project_name: str,
    spec_sections: List[str],
    key_details: List[dict],
    lessons_learned: List[str]
):
    """Capture project-specific knowledge as training data"""
    
    examples = []
    
    # Spec interpretations
    for section in spec_sections:
        examples.append({
            "prompt": f"What are the key requirements in spec section {section['number']} for {project_name}?",
            "response": section["summary"],
            "tags": ["specs", section["number"].replace(" ", "-")]
        })
    
    # Detail decisions
    for detail in key_details:
        examples.append({
            "prompt": f"How did we detail {detail['condition']} on {project_name}?",
            "response": detail["solution"],
            "tags": ["details", detail["type"]]
        })
    
    # Lessons learned
    for lesson in lessons_learned:
        examples.append({
            "prompt": f"What did we learn about {lesson['topic']} from {project_name}?",
            "response": lesson["lesson"],
            "tags": ["lessons-learned", lesson["topic"]]
        })
    
    return examples
```

## Data Quality Pipeline

### Stage 1: Collection
```
All interactions → Buffer → Raw storage
```

### Stage 2: Filtering
```python
QUALITY_FILTERS = {
    "min_prompt_length": 10,        # Skip very short prompts
    "min_response_length": 50,      # Skip trivial responses
    "required_relevance": "medium", # Skip low relevance
    "exclude_sources": ["error", "timeout"],
}

def filter_for_training(examples: List[dict]) -> List[dict]:
    """Apply quality filters"""
    
    filtered = []
    for ex in examples:
        # Length checks
        if len(ex["prompt"]) < QUALITY_FILTERS["min_prompt_length"]:
            continue
        if len(ex["response"]) < QUALITY_FILTERS["min_response_length"]:
            continue
        
        # Relevance check
        relevance = ex.get("quality", {}).get("domain_relevance", "low")
        if relevance == "low":
            continue
        
        # Source check
        if ex.get("source") in QUALITY_FILTERS["exclude_sources"]:
            continue
        
        # Explicit exclusion
        if not ex.get("include_in_training", True):
            continue
        
        filtered.append(ex)
    
    return filtered
```

### Stage 3: Deduplication
```python
def deduplicate(examples: List[dict]) -> List[dict]:
    """Remove near-duplicate examples"""
    
    seen_prompts = set()
    unique = []
    
    for ex in examples:
        # Normalize prompt
        normalized = ex["prompt"].lower().strip()
        
        # Simple dedup - could use embedding similarity
        if normalized not in seen_prompts:
            seen_prompts.add(normalized)
            unique.append(ex)
    
    return unique
```

### Stage 4: Formatting for Training
```python
def format_for_modal(examples: List[dict]) -> List[dict]:
    """Format examples for Modal fine-tuning"""
    
    formatted = []
    for ex in examples:
        formatted.append({
            "prompt": ex["prompt"],
            "response": ex["response"],
            # Add system context if needed
            "system": "You are an expert roofing and waterproofing assistant."
        })
    
    return formatted
```

## Specialized Data Collection

### Calculation Examples
```python
def capture_calculation(
    description: str,
    inputs: dict,
    formula: str,
    result: float,
    explanation: str
):
    """Capture verified calculations"""
    
    prompt = f"Calculate {description} given: {json.dumps(inputs)}"
    response = f"{explanation}\n\nFormula: {formula}\nResult: {result}"
    
    collector.capture(
        prompt=prompt,
        response=response,
        source="verified_calculation",
        tags=["calculation", description.split()[0].lower()]
    )
```

### Spec Interpretation Examples
```python
def capture_spec_interpretation(
    spec_section: str,
    question: str,
    interpretation: str,
    source_quote: str = None
):
    """Capture spec Q&A"""
    
    response = interpretation
    if source_quote:
        response += f"\n\nSpec reference: \"{source_quote}\""
    
    collector.capture(
        prompt=question,
        response=response,
        source="spec_interpretation",
        tags=["specs", spec_section.replace(" ", "-")]
    )
```

### Shop Drawing Notes
```python
def capture_detail_decision(
    condition: str,
    decision: str,
    reasoning: str,
    project: str = None
):
    """Capture detail/drawing decisions"""
    
    prompt = f"How should we detail {condition}?"
    response = f"{decision}\n\nReasoning: {reasoning}"
    
    collector.capture(
        prompt=prompt,
        response=response,
        source="detail_decision",
        tags=["details", "shop-drawings"],
        project=project
    )
```

## Integration with Architect AI

```python
"""
Hook into query processing to auto-collect
"""

async def process_query_with_collection(query: str, context: dict = None):
    """Process query and collect training data"""
    
    # Get response from tiered system
    result = await process_query(query, context)
    
    # Capture for training (async, don't block)
    example_id = collector.capture(
        prompt=query,
        response=result["response"],
        source="production_query",
        skill_used=result.get("skill_used"),
        tier=result.get("tier"),
        latency_ms=result.get("latency_ms"),
        project=context.get("project") if context else None
    )
    
    # Attach example_id to result for feedback tracking
    result["training_example_id"] = example_id
    
    return result


def record_user_feedback(example_id: str, feedback: str):
    """Record feedback from thumbs up/down"""
    
    if feedback in ["positive", "negative"]:
        collector.add_feedback(example_id, feedback)
        
        # Negative feedback might trigger correction flow
        if feedback == "negative":
            return {"action": "request_correction"}
    
    return {"recorded": True}
```

## Export for Modal Training

```python
"""
Export pipeline for Modal
"""

import modal

app = modal.App("training-data-export")
data_volume = modal.Volume.from_name("roofing-training-data", create_if_missing=True)


@app.function(volumes={"/data": data_volume})
def export_training_data(
    min_quality: str = "medium",
    min_examples: int = 100
) -> dict:
    """Export collected data to Modal volume for training"""
    
    import json
    import glob
    
    # Load all examples
    all_examples = []
    for filepath in glob.glob("/data/training/examples_*.jsonl"):
        with open(filepath, "r") as f:
            for line in f:
                all_examples.append(json.loads(line))
    
    # Load corrections (high value)
    corrections = []
    corrections_path = "/data/training/corrections.jsonl"
    if os.path.exists(corrections_path):
        with open(corrections_path, "r") as f:
            for line in f:
                corr = json.loads(line)
                # Convert correction to training format
                corrections.append({
                    "prompt": corr["original_prompt"],
                    "response": corr["corrected_response"],
                    "source": "correction",
                    "quality": {"domain_relevance": "high"}
                })
    
    # Combine and filter
    combined = all_examples + corrections
    filtered = filter_for_training(combined)
    deduped = deduplicate(filtered)
    formatted = format_for_modal(deduped)
    
    if len(formatted) < min_examples:
        return {
            "status": "insufficient_data",
            "count": len(formatted),
            "required": min_examples
        }
    
    # Write to Modal volume
    output_path = "/data/training_conversations.jsonl"
    with open(output_path, "w") as f:
        for ex in formatted:
            f.write(json.dumps(ex) + "\n")
    
    data_volume.commit()
    
    return {
        "status": "exported",
        "total_raw": len(all_examples),
        "corrections": len(corrections),
        "after_filtering": len(formatted),
        "output_path": output_path
    }


@app.function()
def get_collection_stats() -> dict:
    """Get current collection statistics"""
    return collector.get_stats()


@app.function()
def trigger_training_if_ready(min_examples: int = 500):
    """Check if we have enough data and trigger training"""
    
    stats = get_collection_stats()
    
    if stats["total_examples"] >= min_examples:
        # Export data
        export_result = export_training_data.remote()
        
        if export_result["status"] == "exported":
            # Trigger Modal training
            fine_tune = modal.Function.lookup(
                "roofing-training",
                "fine_tune_roofing_model"
            )
            training_job = fine_tune.spawn()
            
            return {
                "status": "training_triggered",
                "examples": export_result["after_filtering"],
                "job_id": training_job.object_id
            }
    
    return {
        "status": "waiting",
        "current": stats["total_examples"],
        "required": min_examples
    }
```

## Dashboard Integration

```
┌─────────────────────────────────────────────────────────────┐
│  TRAINING DATA COLLECTION                                   │
├─────────────────────────────────────────────────────────────┤
│  Total Examples: 1,247                                      │
│  ████████████████████░░░░░░░░░░ 62% to next training (2000) │
│                                                             │
│  By Source:                                                 │
│  • Production queries: 892                                  │
│  • Corrections: 47 ⭐ (high value)                          │
│  • Document generation: 156                                 │
│  • Calculations: 89                                         │
│  • Spec interpretations: 63                                 │
│                                                             │
│  Quality Distribution:                                      │
│  High relevance:   ████████████████ 68%                    │
│  Medium relevance: ████████ 27%                            │
│  Low (excluded):   ██ 5%                                   │
│                                                             │
│  Recent Corrections (review these!):                        │
│  • TPO seam overlap → Updated to 2.5" minimum              │
│  • Base flash height → Added code reference                │
│  • Drain sump depth → Spec section citation                │
├─────────────────────────────────────────────────────────────┤
│  [Export Data]  [Trigger Training]  [Review Queue: 23]     │
└─────────────────────────────────────────────────────────────┘
```

## Best Practices

### DO Collect:
- ✅ Every spec interpretation question
- ✅ All verified calculations
- ✅ Successful document generations
- ✅ User corrections (VERY valuable)
- ✅ Project-specific decisions
- ✅ Detail/drawing explanations

### DON'T Collect:
- ❌ Personal/private information
- ❌ Failed/error responses
- ❌ Generic non-roofing queries
- ❌ Very short trivial exchanges
- ❌ Duplicate questions

### Review Priority:
1. **Corrections** - Always review, highest learning value
2. **Negative feedback** - Understand what went wrong
3. **New topics** - Expand model knowledge
4. **Edge cases** - Improve robustness
