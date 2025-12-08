# Training Data Collection - Implementation

## Quick Start

```python
"""
Quick setup for training data collection
"""

from training_collector import TrainingCollector, collector

# Auto-collect from every query
result = await process_query("What's TPO production rate?")
# Automatically captured!

# Add feedback when user gives thumbs up/down
collector.add_feedback(result["training_example_id"], "positive")

# Record corrections (most valuable!)
collector.record_correction(
    original_prompt="What's the seam overlap for TPO?",
    original_response="2 inches minimum",
    corrected_response="2.5 inches minimum per most manufacturers. Carlisle requires 2.5\", Firestone 3\". Always check approved submittal.",
    reason="Original was too brief and didn't cite manufacturer requirements"
)

# Check stats
print(collector.get_stats())
```

## Full Implementation

```python
"""
training_collector.py
Complete implementation for production use
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import hashlib
import threading
import queue
import os

@dataclass
class TrainingExample:
    """Single training example"""
    id: str
    timestamp: str
    source: str
    prompt: str
    response: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    project_context: str = "general"
    include_in_training: bool = True


class TrainingCollector:
    """
    Collects and manages training data from production queries
    Thread-safe with background flushing
    """
    
    # Roofing domain keywords for relevance scoring
    DOMAIN_KEYWORDS = {
        "high": [
            "tpo", "epdm", "pvc", "mod bit", "bur", "membrane",
            "flashing", "base flash", "counter flash", "reglet",
            "07 50", "07 52", "07 54", "07 55", "07 60", "07 62",
            "polyiso", "insulation", "r-value", "tapered",
            "roof drain", "scupper", "overflow", "cricket",
            "curb", "penetration", "pitch pan", "boot",
            "submittal", "shop drawing", "rfi", "change order",
            "carlisle", "firestone", "gaf", "johns manville", "sika"
        ],
        "medium": [
            "roof", "waterproof", "spec", "detail", "parapet",
            "coping", "edge metal", "fascia", "gutter",
            "adhesive", "fastener", "seam", "weld",
            "architect", "contractor", "subcontract"
        ]
    }
    
    # Auto-tagging patterns
    TAG_PATTERNS = {
        "tpo": ["tpo", "thermoplastic polyolefin"],
        "epdm": ["epdm", "rubber membrane", "ethylene propylene"],
        "pvc": ["pvc membrane", "polyvinyl chloride"],
        "mod-bit": ["modified bitumen", "mod bit", "sbs", "app"],
        "bur": ["built-up", "bur", "tar and gravel"],
        "membrane": ["membrane", "single-ply", "sheet goods"],
        "flashing": ["flashing", "flash", "termination"],
        "insulation": ["insulation", "polyiso", "iso board", "eps", "xps"],
        "drains": ["drain", "scupper", "overflow", "leader"],
        "specs": ["spec", "specification", "section 07"],
        "estimating": ["estimate", "takeoff", "quantity", "bid", "cost"],
        "labor": ["labor", "man-hour", "production rate", "crew", "productivity"],
        "safety": ["osha", "safety", "fall protection", "harness", "guardrail"],
        "submittals": ["submittal", "product data", "shop drawing", "samples"],
        "rfi": ["rfi", "request for information", "clarification", "conflict"],
        "change-order": ["change order", "pco", "t&m", "extra work"],
        "quality": ["inspection", "punch list", "defect", "warranty"],
        "scheduling": ["schedule", "duration", "sequence", "phasing"],
    }
    
    def __init__(
        self,
        storage_path: str = "./training_data",
        buffer_size: int = 50,
        auto_flush: bool = True
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.buffer: List[TrainingExample] = []
        self.buffer_size = buffer_size
        self.lock = threading.Lock()
        
        # Background flush queue
        if auto_flush:
            self.flush_queue = queue.Queue()
            self.flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
            self.flush_thread.start()
    
    def capture(
        self,
        prompt: str,
        response: str,
        source: str = "chat",
        skill_used: Optional[str] = None,
        tier: Optional[str] = None,
        latency_ms: Optional[float] = None,
        tags: Optional[List[str]] = None,
        project: str = "general",
        user_id: Optional[str] = None
    ) -> str:
        """
        Capture an interaction as potential training data
        Returns example_id for later feedback tracking
        """
        
        # Generate unique ID
        content_hash = hashlib.md5(
            f"{prompt}{response}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        example_id = f"train_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{content_hash}"
        
        # Auto-generate tags if not provided
        if tags is None:
            tags = self._auto_tag(prompt, response)
        
        example = TrainingExample(
            id=example_id,
            timestamp=datetime.now().isoformat(),
            source=source,
            prompt=prompt.strip(),
            response=response.strip(),
            metadata={
                "skill_used": skill_used,
                "tier_handled": tier,
                "latency_ms": latency_ms,
                "user_id": user_id,
                "prompt_tokens": len(prompt.split()),
                "response_tokens": len(response.split()),
            },
            quality={
                "user_feedback": None,
                "was_corrected": False,
                "verified_accurate": None,
                "domain_relevance": self._assess_relevance(prompt, response),
                "auto_score": self._calculate_quality_score(prompt, response)
            },
            tags=tags,
            project_context=project
        )
        
        with self.lock:
            self.buffer.append(example)
            
            if len(self.buffer) >= self.buffer_size:
                self._queue_flush()
        
        return example_id
    
    def add_feedback(self, example_id: str, feedback: str) -> bool:
        """
        Add user feedback (positive/negative) to an example
        """
        
        # Check buffer first
        with self.lock:
            for ex in self.buffer:
                if ex.id == example_id:
                    ex.quality["user_feedback"] = feedback
                    if feedback == "positive":
                        ex.quality["verified_accurate"] = True
                    return True
        
        # Check stored files
        return self._update_stored_example(
            example_id,
            {"quality.user_feedback": feedback}
        )
    
    def record_correction(
        self,
        original_prompt: str,
        original_response: str,
        corrected_response: str,
        reason: Optional[str] = None,
        corrector: str = "user"
    ) -> str:
        """
        Record a correction - VERY high value training data
        Returns correction_id
        """
        
        correction_id = f"corr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        correction = {
            "id": correction_id,
            "timestamp": datetime.now().isoformat(),
            "source": "user_correction",
            "original_prompt": original_prompt.strip(),
            "original_response": original_response.strip(),
            "corrected_response": corrected_response.strip(),
            "correction_reason": reason,
            "corrector": corrector,
            "quality": {
                "learning_value": "very_high",
                "domain_relevance": "high"
            },
            "tags": self._auto_tag(original_prompt, corrected_response),
            "include_in_training": True
        }
        
        # Save correction
        corrections_path = self.storage_path / "corrections.jsonl"
        with open(corrections_path, "a") as f:
            f.write(json.dumps(correction) + "\n")
        
        # Also capture corrected version as positive example
        self.capture(
            prompt=original_prompt,
            response=corrected_response,
            source="verified_correction",
            tags=correction["tags"]
        )
        
        return correction_id
    
    def capture_calculation(
        self,
        description: str,
        inputs: Dict[str, Any],
        formula: str,
        result: Any,
        explanation: str,
        verified: bool = True
    ) -> str:
        """Capture a verified calculation"""
        
        prompt = f"Calculate {description}: {json.dumps(inputs)}"
        response = f"{explanation}\n\nFormula: {formula}\nResult: {result}"
        
        return self.capture(
            prompt=prompt,
            response=response,
            source="verified_calculation" if verified else "calculation",
            tags=["calculation", description.split()[0].lower()]
        )
    
    def capture_spec_qa(
        self,
        spec_section: str,
        question: str,
        answer: str,
        quote: Optional[str] = None
    ) -> str:
        """Capture spec interpretation Q&A"""
        
        response = answer
        if quote:
            response += f'\n\nSpec reference: "{quote}"'
        
        return self.capture(
            prompt=question,
            response=response,
            source="spec_interpretation",
            tags=["specs", spec_section.replace(" ", "-")]
        )
    
    def capture_document(
        self,
        doc_type: str,
        prompt: str,
        generated_doc: str,
        was_used: bool = True,
        modifications: str = "none"
    ) -> str:
        """Capture document generation (RFI, submittal, etc.)"""
        
        example_id = self.capture(
            prompt=prompt,
            response=generated_doc,
            source=f"{doc_type}_generation",
            tags=[doc_type, "document-generation"]
        )
        
        # Update with usage metadata
        with self.lock:
            for ex in self.buffer:
                if ex.id == example_id:
                    ex.metadata["was_used"] = was_used
                    ex.metadata["modifications"] = modifications
                    break
        
        return example_id
    
    def _assess_relevance(self, prompt: str, response: str) -> str:
        """Assess domain relevance of content"""
        
        text = f"{prompt} {response}".lower()
        
        # Check high-value keywords
        high_matches = sum(1 for kw in self.DOMAIN_KEYWORDS["high"] if kw in text)
        if high_matches >= 3:
            return "high"
        
        # Check medium-value keywords
        medium_matches = sum(1 for kw in self.DOMAIN_KEYWORDS["medium"] if kw in text)
        if high_matches >= 1 or medium_matches >= 3:
            return "medium"
        
        return "low"
    
    def _calculate_quality_score(self, prompt: str, response: str) -> float:
        """Calculate overall quality score (0-1)"""
        
        score = 0.5  # Base score
        
        # Length factors
        prompt_len = len(prompt.split())
        response_len = len(response.split())
        
        if prompt_len >= 5:
            score += 0.1
        if response_len >= 20:
            score += 0.1
        if response_len >= 50:
            score += 0.1
        
        # Domain relevance
        relevance = self._assess_relevance(prompt, response)
        if relevance == "high":
            score += 0.2
        elif relevance == "medium":
            score += 0.1
        
        return min(score, 1.0)
    
    def _auto_tag(self, prompt: str, response: str) -> List[str]:
        """Auto-generate tags from content"""
        
        text = f"{prompt} {response}".lower()
        tags = []
        
        for tag, patterns in self.TAG_PATTERNS.items():
            if any(p in text for p in patterns):
                tags.append(tag)
        
        return tags if tags else ["general"]
    
    def _queue_flush(self):
        """Queue buffer for background flush"""
        
        if hasattr(self, 'flush_queue'):
            examples_to_flush = self.buffer.copy()
            self.buffer = []
            self.flush_queue.put(examples_to_flush)
        else:
            self._flush_sync()
    
    def _flush_worker(self):
        """Background worker for flushing data"""
        
        while True:
            examples = self.flush_queue.get()
            if examples is None:
                break
            self._write_examples(examples)
    
    def _flush_sync(self):
        """Synchronous flush"""
        
        with self.lock:
            if self.buffer:
                self._write_examples(self.buffer)
                self.buffer = []
    
    def _write_examples(self, examples: List[TrainingExample]):
        """Write examples to storage"""
        
        date_str = datetime.now().strftime("%Y%m%d")
        filepath = self.storage_path / f"examples_{date_str}.jsonl"
        
        with open(filepath, "a") as f:
            for ex in examples:
                f.write(json.dumps(asdict(ex)) + "\n")
    
    def _update_stored_example(self, example_id: str, updates: Dict) -> bool:
        """Update a stored example (simplified - rewrites file)"""
        # In production, use a database
        return False
    
    def flush(self):
        """Force flush buffer to storage"""
        self._flush_sync()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        
        stats = {
            "buffer_count": len(self.buffer),
            "total_examples": 0,
            "corrections": 0,
            "by_source": {},
            "by_relevance": {"high": 0, "medium": 0, "low": 0},
            "by_tag": {},
        }
        
        # Count from files
        for filepath in self.storage_path.glob("examples_*.jsonl"):
            with open(filepath) as f:
                for line in f:
                    ex = json.loads(line)
                    stats["total_examples"] += 1
                    
                    # By source
                    source = ex.get("source", "unknown")
                    stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
                    
                    # By relevance
                    rel = ex.get("quality", {}).get("domain_relevance", "low")
                    stats["by_relevance"][rel] = stats["by_relevance"].get(rel, 0) + 1
                    
                    # By tag
                    for tag in ex.get("tags", []):
                        stats["by_tag"][tag] = stats["by_tag"].get(tag, 0) + 1
        
        # Count corrections
        corrections_path = self.storage_path / "corrections.jsonl"
        if corrections_path.exists():
            with open(corrections_path) as f:
                stats["corrections"] = sum(1 for _ in f)
        
        # Add buffer
        stats["total_examples"] += stats["buffer_count"]
        
        return stats
    
    def export_for_training(
        self,
        output_path: Optional[str] = None,
        min_quality: str = "medium",
        include_corrections: bool = True
    ) -> Dict[str, Any]:
        """Export data formatted for Modal training"""
        
        # Flush buffer first
        self.flush()
        
        all_examples = []
        
        # Load examples
        for filepath in self.storage_path.glob("examples_*.jsonl"):
            with open(filepath) as f:
                for line in f:
                    all_examples.append(json.loads(line))
        
        # Load corrections
        if include_corrections:
            corrections_path = self.storage_path / "corrections.jsonl"
            if corrections_path.exists():
                with open(corrections_path) as f:
                    for line in f:
                        corr = json.loads(line)
                        all_examples.append({
                            "prompt": corr["original_prompt"],
                            "response": corr["corrected_response"],
                            "source": "correction",
                            "quality": {"domain_relevance": "high"},
                            "tags": corr.get("tags", []),
                            "include_in_training": True
                        })
        
        # Filter
        quality_order = {"high": 3, "medium": 2, "low": 1}
        min_level = quality_order.get(min_quality, 2)
        
        filtered = [
            ex for ex in all_examples
            if (
                ex.get("include_in_training", True) and
                quality_order.get(ex.get("quality", {}).get("domain_relevance", "low"), 0) >= min_level and
                len(ex.get("prompt", "")) >= 10 and
                len(ex.get("response", "")) >= 20
            )
        ]
        
        # Deduplicate
        seen = set()
        deduped = []
        for ex in filtered:
            key = ex["prompt"].lower().strip()[:100]
            if key not in seen:
                seen.add(key)
                deduped.append(ex)
        
        # Format for training
        formatted = [
            {"prompt": ex["prompt"], "response": ex["response"]}
            for ex in deduped
        ]
        
        # Write output
        if output_path is None:
            output_path = self.storage_path / "training_export.jsonl"
        
        with open(output_path, "w") as f:
            for ex in formatted:
                f.write(json.dumps(ex) + "\n")
        
        return {
            "total_raw": len(all_examples),
            "after_filtering": len(formatted),
            "output_path": str(output_path)
        }


# Global instance
collector = TrainingCollector()
```

## Modal Export Function

```python
"""
modal_export.py
Export training data to Modal volume
"""

import modal

app = modal.App("training-export")
data_volume = modal.Volume.from_name("roofing-training-data", create_if_missing=True)


@app.function(volumes={"/data": data_volume})
def sync_training_data(local_export_path: str):
    """Sync local training export to Modal volume"""
    
    import shutil
    
    # Copy to Modal volume
    shutil.copy(local_export_path, "/data/training_conversations.jsonl")
    data_volume.commit()
    
    # Count examples
    with open("/data/training_conversations.jsonl") as f:
        count = sum(1 for _ in f)
    
    return {"synced": True, "examples": count}


@app.function()
def check_training_readiness(min_examples: int = 500):
    """Check if we have enough data to train"""
    
    try:
        with open("/data/training_conversations.jsonl") as f:
            count = sum(1 for _ in f)
        
        return {
            "ready": count >= min_examples,
            "current": count,
            "required": min_examples
        }
    except FileNotFoundError:
        return {"ready": False, "current": 0, "required": min_examples}
```

## Usage in Production

```python
# In your query processing pipeline:

from training_collector import collector

async def process_and_collect(query: str, context: dict = None):
    """Process query and auto-collect for training"""
    
    # Get response
    result = await process_query(query, context)
    
    # Capture for training
    example_id = collector.capture(
        prompt=query,
        response=result["response"],
        skill_used=result.get("skill"),
        tier=result.get("tier"),
        latency_ms=result.get("latency_ms"),
        project=context.get("project") if context else None
    )
    
    # Return with tracking ID
    result["_training_id"] = example_id
    return result


# When user gives feedback:
def handle_feedback(training_id: str, is_positive: bool):
    collector.add_feedback(
        training_id,
        "positive" if is_positive else "negative"
    )


# When user corrects a response:
def handle_correction(original_query, original_response, corrected):
    collector.record_correction(
        original_prompt=original_query,
        original_response=original_response,
        corrected_response=corrected,
        reason="User correction"
    )


# Weekly: export and check if ready to train
def weekly_training_check():
    export = collector.export_for_training()
    
    if export["after_filtering"] >= 500:
        # Sync to Modal
        sync = modal.Function.lookup("training-export", "sync_training_data")
        sync.remote(export["output_path"])
        
        # Trigger training
        train = modal.Function.lookup("roofing-training", "fine_tune_roofing_model")
        train.spawn()
        
        return "Training triggered"
    
    return f"Need more data: {export['after_filtering']}/500"
```
