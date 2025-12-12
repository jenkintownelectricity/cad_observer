"""
ROOFIO Knowledge Base - Skills Docs in Vector DB
=================================================

This is where the Master Architect writes new knowledge to teach
the system. The key insight is:

    MODIFY KNOWLEDGE, NOT CODE

Instead of changing Python files (dangerous), the Master Architect:
- Adds new rules to the vector database
- Updates existing knowledge entries
- Creates error correction entries
- Generates training examples for fine-tuning

Tier 2 (Groq) queries this knowledge base before processing
requests, so the system gets smarter without code changes.

Uses Upstash Vector for serverless vector storage with
built-in embedding models.
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Upstash Vector client
from upstash_vector import Index

# Initialize Upstash Vector
# When creating the index, select an embedding model (e.g., bge-m3 for multilingual)
# This allows us to upsert raw text and query with text - no external embeddings needed
vector_index = Index(
    url=os.environ.get("UPSTASH_VECTOR_REST_URL", ""),
    token=os.environ.get("UPSTASH_VECTOR_REST_TOKEN", ""),
)


# =============================================================================
# KNOWLEDGE CATEGORIES
# =============================================================================

class KnowledgeCategory(str, Enum):
    """Categories for organizing knowledge in the vector DB"""
    
    # Construction Specifications (Division 07)
    SPECS = "specs"              # 07 62 00, 07 50 00, etc.
    
    # Vendor-specific rules
    VENDORS = "vendors"          # "ABC Supply invoices have date in footer"
    
    # Form parsing rules
    FORMS = "forms"              # How to parse JHA, Daily Log, etc.
    
    # Business rules
    RULES = "rules"              # "Always get 3 quotes over $10k"
    
    # Error corrections (learned from failures)
    ERROR_FIXES = "error_fixes"  # How to fix specific errors
    
    # Training examples (for fine-tuning)
    TRAINING = "training"        # Input/output pairs for Tier 2 training
    
    # OSHA and safety regulations
    SAFETY = "safety"            # OSHA 1926, silica rules, etc.
    
    # Weather decision rules
    WEATHER = "weather"          # "Don't pour concrete below 40°F"
    
    # Insurance and compliance
    COMPLIANCE = "compliance"    # OCIP, Wrap-Up, certificate rules
    
    # General procedures
    PROCEDURES = "procedures"    # Standard operating procedures


# Namespace mapping (Upstash Vector supports namespaces)
CATEGORY_NAMESPACES = {
    KnowledgeCategory.SPECS: "roofio:specs",
    KnowledgeCategory.VENDORS: "roofio:vendors",
    KnowledgeCategory.FORMS: "roofio:forms",
    KnowledgeCategory.RULES: "roofio:rules",
    KnowledgeCategory.ERROR_FIXES: "roofio:fixes",
    KnowledgeCategory.TRAINING: "roofio:training",
    KnowledgeCategory.SAFETY: "roofio:safety",
    KnowledgeCategory.WEATHER: "roofio:weather",
    KnowledgeCategory.COMPLIANCE: "roofio:compliance",
    KnowledgeCategory.PROCEDURES: "roofio:procedures",
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class KnowledgeEntry:
    """A single knowledge document in the Skills DB"""
    id: str
    category: KnowledgeCategory
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "human"  # 'human' or 'master_architect'
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 1.0  # 0.0-1.0, lower for auto-generated
    tags: List[str] = field(default_factory=list)
    version: int = 1
    
    def to_metadata(self) -> dict:
        """Convert to metadata dict for vector storage"""
        return {
            "title": self.title,
            "category": self.category.value,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "confidence": self.confidence,
            "tags": ",".join(self.tags),
            "version": self.version,
            **self.metadata,
        }


@dataclass
class QueryResult:
    """Result from a knowledge query"""
    id: str
    score: float
    content: str
    title: str
    category: str
    confidence: float
    metadata: Dict[str, Any]


# =============================================================================
# KNOWLEDGE BASE CLASS
# =============================================================================

class SkillsKnowledgeBase:
    """
    The Knowledge Base that Tier 2 (Groq) queries for context.
    Master Architect adds entries here to "teach" the system.
    
    Key Methods:
    - add_knowledge(): Add a new knowledge entry
    - query(): Query for relevant knowledge
    - add_error_fix(): Add a learned error correction
    - add_vendor_rule(): Add vendor-specific parsing rule
    - add_training_example(): Add fine-tuning example
    """
    
    def __init__(self):
        self.index = vector_index
    
    # -------------------------------------------------------------------------
    # CORE OPERATIONS
    # -------------------------------------------------------------------------
    
    async def add_knowledge(
        self,
        category: KnowledgeCategory,
        title: str,
        content: str,
        metadata: dict = None,
        created_by: str = "human",
        confidence: float = 1.0,
        tags: List[str] = None,
    ) -> str:
        """
        Add new knowledge to the vector database.
        
        Args:
            category: Knowledge category (specs, vendors, etc.)
            title: Short title for the entry
            content: Full content text (will be embedded)
            metadata: Additional metadata
            created_by: 'human' or 'master_architect'
            confidence: 0.0-1.0 (lower for auto-generated)
            tags: List of searchable tags
        
        Returns:
            Document ID
        """
        doc_id = str(uuid.uuid4())
        namespace = CATEGORY_NAMESPACES.get(category, "roofio:general")
        
        entry = KnowledgeEntry(
            id=doc_id,
            category=category,
            title=title,
            content=content,
            metadata=metadata or {},
            created_by=created_by,
            confidence=confidence,
            tags=tags or [],
        )
        
        # Upsert to vector index
        # Upstash handles embedding automatically when index is created with a model
        self.index.upsert(
            vectors=[
                (doc_id, content, entry.to_metadata())
            ],
            namespace=namespace
        )
        
        return doc_id
    
    async def query(
        self,
        query_text: str,
        categories: List[KnowledgeCategory] = None,
        top_k: int = 5,
        min_confidence: float = 0.5,
        min_score: float = 0.7,
    ) -> List[QueryResult]:
        """
        Query knowledge base for relevant context.
        
        Used by Tier 2 (Groq) before processing requests.
        
        Args:
            query_text: The search query
            categories: Optional filter by categories
            top_k: Number of results per namespace
            min_confidence: Minimum confidence threshold
            min_score: Minimum similarity score threshold
        
        Returns:
            List of QueryResult objects sorted by score
        """
        results = []
        
        # Determine which namespaces to query
        if categories:
            namespaces = [
                CATEGORY_NAMESPACES.get(cat)
                for cat in categories
                if cat in CATEGORY_NAMESPACES
            ]
        else:
            namespaces = list(CATEGORY_NAMESPACES.values())
        
        # Query each namespace
        for namespace in namespaces:
            try:
                matches = self.index.query(
                    data=query_text,  # Text query, auto-embedded by Upstash
                    top_k=top_k,
                    namespace=namespace,
                    include_metadata=True,
                    include_data=True,  # Include the original content
                )
                
                for match in matches:
                    confidence = float(match.metadata.get("confidence", 1.0))
                    
                    # Apply filters
                    if confidence < min_confidence:
                        continue
                    if match.score < min_score:
                        continue
                    
                    results.append(QueryResult(
                        id=match.id,
                        score=match.score,
                        content=match.data if hasattr(match, 'data') else "",
                        title=match.metadata.get("title", ""),
                        category=match.metadata.get("category", ""),
                        confidence=confidence,
                        metadata=match.metadata,
                    ))
                    
            except Exception as e:
                # Log but don't fail - partial results are better than none
                print(f"Error querying namespace {namespace}: {e}")
                continue
        
        # Sort by score and return
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k * 2]  # Return more since we queried multiple namespaces
    
    async def update_knowledge(
        self,
        doc_id: str,
        category: KnowledgeCategory,
        content: str = None,
        title: str = None,
        metadata: dict = None,
        confidence: float = None,
    ) -> bool:
        """
        Update an existing knowledge entry.
        
        Creates a new version while preserving the ID.
        """
        namespace = CATEGORY_NAMESPACES.get(category, "roofio:general")
        
        # Fetch existing entry
        try:
            existing = self.index.fetch([doc_id], namespace=namespace)
            if not existing or doc_id not in existing:
                return False
            
            old_entry = existing[doc_id]
            old_metadata = old_entry.metadata
            
            # Merge updates
            new_content = content if content else old_entry.data
            new_metadata = {
                **old_metadata,
                **(metadata or {}),
                "version": int(old_metadata.get("version", 1)) + 1,
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            if title:
                new_metadata["title"] = title
            if confidence is not None:
                new_metadata["confidence"] = confidence
            
            # Upsert updated entry
            self.index.upsert(
                vectors=[(doc_id, new_content, new_metadata)],
                namespace=namespace
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating knowledge {doc_id}: {e}")
            return False
    
    async def delete_knowledge(
        self,
        doc_id: str,
        category: KnowledgeCategory,
    ) -> bool:
        """Delete a knowledge entry"""
        namespace = CATEGORY_NAMESPACES.get(category, "roofio:general")
        
        try:
            self.index.delete([doc_id], namespace=namespace)
            return True
        except Exception as e:
            print(f"Error deleting knowledge {doc_id}: {e}")
            return False
    
    # -------------------------------------------------------------------------
    # SPECIALIZED ADD METHODS (For Master Architect)
    # -------------------------------------------------------------------------
    
    async def add_error_fix(
        self,
        error_pattern: str,
        fix_description: str,
        example_input: str,
        correct_output: str,
        source_interaction_id: str = None,
        error_type: str = None,
    ) -> str:
        """
        Add an error correction entry.
        
        Called by Master Architect when it learns how to fix an error.
        This teaches Tier 2 to handle similar cases in the future.
        
        Args:
            error_pattern: Description of the error pattern
            fix_description: How to fix it
            example_input: Example input that caused the error
            correct_output: The correct output
            source_interaction_id: ID of the original failed interaction
            error_type: Classification of error type
        
        Returns:
            Document ID
        """
        content = f"""ERROR PATTERN: {error_pattern}

FIX: {fix_description}

EXAMPLE INPUT:
{example_input}

CORRECT OUTPUT:
{correct_output}
"""
        
        return await self.add_knowledge(
            category=KnowledgeCategory.ERROR_FIXES,
            title=f"Fix: {error_pattern[:50]}...",
            content=content,
            metadata={
                "error_pattern": error_pattern,
                "error_type": error_type or "unknown",
                "source_interaction": source_interaction_id,
            },
            created_by="master_architect",
            confidence=0.8,  # Lower confidence for auto-generated
            tags=["error_fix", error_type or "general"],
        )
    
    async def add_vendor_rule(
        self,
        vendor_name: str,
        rule_type: str,  # 'invoice', 'submittal', 'quote', etc.
        rule_description: str,
        examples: List[str] = None,
        field_locations: Dict[str, str] = None,
    ) -> str:
        """
        Add vendor-specific parsing rules.
        
        E.g., "ABC Supply invoices have PO# in top-right corner"
        
        Args:
            vendor_name: Name of the vendor
            rule_type: Type of document (invoice, submittal, etc.)
            rule_description: The rule to apply
            examples: Example text snippets
            field_locations: Dict of field -> location descriptions
        
        Returns:
            Document ID
        """
        content = f"""VENDOR: {vendor_name}
DOCUMENT TYPE: {rule_type}

RULE: {rule_description}
"""
        
        if field_locations:
            content += "\nFIELD LOCATIONS:\n"
            for field, location in field_locations.items():
                content += f"- {field}: {location}\n"
        
        if examples:
            content += "\nEXAMPLES:\n"
            for i, example in enumerate(examples, 1):
                content += f"{i}. {example}\n"
        
        return await self.add_knowledge(
            category=KnowledgeCategory.VENDORS,
            title=f"{vendor_name} - {rule_type} Rule",
            content=content,
            metadata={
                "vendor": vendor_name.lower(),
                "document_type": rule_type.lower(),
                "field_locations": json.dumps(field_locations or {}),
            },
            created_by="master_architect",
            confidence=0.85,
            tags=[vendor_name.lower(), rule_type.lower(), "vendor_rule"],
        )
    
    async def add_training_example(
        self,
        task_type: str,
        instruction: str,
        input_text: str,
        output_text: str,
        quality_score: float = 0.8,
        source_interaction_id: str = None,
    ) -> str:
        """
        Add a training example for fine-tuning.
        
        Called by Master Architect to generate training data
        from successful high-rated interactions.
        
        Args:
            task_type: Type of task (summarize, classify, extract, etc.)
            instruction: The instruction given
            input_text: The input provided
            output_text: The expected output
            quality_score: Quality rating (0.0-1.0)
            source_interaction_id: ID of source interaction
        
        Returns:
            Document ID
        """
        content = f"""TASK: {task_type}

INSTRUCTION: {instruction}

INPUT:
{input_text}

OUTPUT:
{output_text}
"""
        
        return await self.add_knowledge(
            category=KnowledgeCategory.TRAINING,
            title=f"Training: {task_type} - {instruction[:30]}...",
            content=content,
            metadata={
                "task_type": task_type,
                "instruction": instruction,
                "quality_score": quality_score,
                "source_interaction": source_interaction_id,
                "status": "pending_review",  # Needs human approval
            },
            created_by="master_architect",
            confidence=quality_score,
            tags=[task_type, "training_data"],
        )
    
    async def add_spec_section(
        self,
        spec_number: str,  # e.g., "07 62 00"
        spec_title: str,
        section_title: str,
        section_content: str,
        source: str = None,
    ) -> str:
        """
        Add a construction specification section.
        
        Args:
            spec_number: CSI spec number (e.g., "07 62 00")
            spec_title: Full spec title (e.g., "Sheet Metal Flashing and Trim")
            section_title: Section within the spec
            section_content: The actual spec content
            source: Source document/URL
        
        Returns:
            Document ID
        """
        content = f"""SPECIFICATION: {spec_number} - {spec_title}
SECTION: {section_title}

{section_content}
"""
        
        return await self.add_knowledge(
            category=KnowledgeCategory.SPECS,
            title=f"{spec_number} - {section_title}",
            content=content,
            metadata={
                "spec_number": spec_number,
                "spec_title": spec_title,
                "section_title": section_title,
                "source": source or "",
            },
            created_by="human",
            confidence=1.0,
            tags=[spec_number, "specification", "division_07"],
        )
    
    async def add_safety_rule(
        self,
        regulation: str,  # e.g., "OSHA 1926.1153"
        title: str,
        rule_text: str,
        triggers: List[str] = None,
        actions_required: List[str] = None,
    ) -> str:
        """
        Add a safety regulation rule.
        
        Args:
            regulation: Regulation reference (e.g., "OSHA 1926.1153")
            title: Rule title
            rule_text: Full rule text
            triggers: Conditions that trigger this rule
            actions_required: Required actions when triggered
        
        Returns:
            Document ID
        """
        content = f"""REGULATION: {regulation}
TITLE: {title}

RULE:
{rule_text}
"""
        
        if triggers:
            content += "\nTRIGGERS:\n"
            for trigger in triggers:
                content += f"- {trigger}\n"
        
        if actions_required:
            content += "\nREQUIRED ACTIONS:\n"
            for action in actions_required:
                content += f"- {action}\n"
        
        return await self.add_knowledge(
            category=KnowledgeCategory.SAFETY,
            title=f"{regulation} - {title}",
            content=content,
            metadata={
                "regulation": regulation,
                "triggers": json.dumps(triggers or []),
                "actions_required": json.dumps(actions_required or []),
            },
            created_by="human",
            confidence=1.0,
            tags=["safety", "osha", regulation],
        )
    
    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------
    
    async def get_context_for_request(
        self,
        task_type: str,
        user_input: str,
        max_tokens: int = 2000,
    ) -> str:
        """
        Get relevant knowledge context for a request.
        
        This is the main method Tier 2 calls before processing.
        
        Args:
            task_type: Type of task being performed
            user_input: The user's input text
            max_tokens: Approximate max tokens in context
        
        Returns:
            Formatted context string for inclusion in prompt
        """
        # Build query combining task type and input
        query = f"{task_type}: {user_input[:500]}"
        
        # Determine relevant categories based on task type
        category_map = {
            "parse_invoice": [KnowledgeCategory.VENDORS, KnowledgeCategory.RULES],
            "summarize_submittal": [KnowledgeCategory.SPECS, KnowledgeCategory.VENDORS],
            "classify_photo": [KnowledgeCategory.RULES, KnowledgeCategory.PROCEDURES],
            "extract_entities": [KnowledgeCategory.VENDORS, KnowledgeCategory.FORMS],
            "safety_check": [KnowledgeCategory.SAFETY, KnowledgeCategory.RULES],
            "weather_decision": [KnowledgeCategory.WEATHER, KnowledgeCategory.RULES],
        }
        
        categories = category_map.get(task_type, None)
        
        # Query knowledge base
        results = await self.query(
            query_text=query,
            categories=categories,
            top_k=5,
            min_confidence=0.5,
        )
        
        if not results:
            return ""
        
        # Format context
        context_parts = []
        total_length = 0
        
        for result in results:
            entry_text = f"[{result.title}]\n{result.content}\n"
            entry_length = len(entry_text)
            
            # Rough token estimate (4 chars per token)
            if total_length + entry_length > max_tokens * 4:
                break
            
            context_parts.append(entry_text)
            total_length += entry_length
        
        return "\n---\n".join(context_parts)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        stats = {
            "total_entries": 0,
            "by_category": {},
            "by_creator": {"human": 0, "master_architect": 0},
        }
        
        for category, namespace in CATEGORY_NAMESPACES.items():
            try:
                info = self.index.info()
                # Note: Upstash Vector info() returns index-level stats
                # For per-namespace counts, we'd need to track separately
                stats["by_category"][category.value] = "N/A"
            except Exception:
                pass
        
        return stats
    
    async def export_training_data(
        self,
        status: str = "approved",
        format: str = "jsonl",
    ) -> List[dict]:
        """
        Export approved training examples for fine-tuning.
        
        Args:
            status: Filter by status ('approved', 'pending_review', etc.)
            format: Output format ('jsonl' for fine-tuning)
        
        Returns:
            List of training examples in the specified format
        """
        # Query all training data
        results = await self.query(
            query_text="training example",  # Broad query
            categories=[KnowledgeCategory.TRAINING],
            top_k=1000,
            min_confidence=0.7,
        )
        
        training_data = []
        
        for result in results:
            if result.metadata.get("status") != status:
                continue
            
            # Parse the content back into structured format
            content = result.content
            
            # Extract parts (simplified parsing)
            parts = content.split("\n\n")
            instruction = ""
            input_text = ""
            output_text = ""
            
            for part in parts:
                if part.startswith("INSTRUCTION:"):
                    instruction = part.replace("INSTRUCTION:", "").strip()
                elif part.startswith("INPUT:"):
                    input_text = part.replace("INPUT:", "").strip()
                elif part.startswith("OUTPUT:"):
                    output_text = part.replace("OUTPUT:", "").strip()
            
            if format == "jsonl":
                training_data.append({
                    "instruction": instruction,
                    "input": input_text,
                    "output": output_text,
                    "metadata": {
                        "id": result.id,
                        "quality_score": result.confidence,
                    }
                })
        
        return training_data


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Global knowledge base instance
knowledge_base = SkillsKnowledgeBase()


# =============================================================================
# TIER 2 INTEGRATION
# =============================================================================

class GroqWithRAG:
    """
    Groq-powered AI that queries Skills Docs before responding.
    
    This is how the system gets smarter without code changes:
    1. Query Skills Docs for relevant knowledge
    2. Include knowledge in prompt to Groq
    3. Process with Groq
    4. Return result
    """
    
    def __init__(self):
        from groq import Groq
        self.groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.knowledge = knowledge_base
    
    async def process(
        self,
        user_input: str,
        task_type: str,
        system_prompt: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.2,
    ) -> dict:
        """
        Process a request with knowledge-enhanced context.
        
        Args:
            user_input: The user's input text
            task_type: Type of task (for knowledge retrieval)
            system_prompt: Additional system instructions
            max_tokens: Max response tokens
            temperature: Response randomness
        
        Returns:
            {
                "response": "...",
                "knowledge_used": ["id1", "id2"],
                "tokens": 150,
            }
        """
        # Step 1: Get relevant knowledge
        knowledge_context = await self.knowledge.get_context_for_request(
            task_type=task_type,
            user_input=user_input,
        )
        
        # Step 2: Build enhanced prompt
        full_system = f"""You are ROOFIO's construction AI assistant.

RELEVANT KNOWLEDGE (use this to inform your response):
{knowledge_context if knowledge_context else "No specific knowledge retrieved."}

{system_prompt}

Be precise, practical, and cite relevant knowledge when applicable.
If the knowledge provides specific rules or formats, follow them exactly."""

        # Step 3: Call Groq
        response = self.groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": full_system},
                {"role": "user", "content": user_input}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return {
            "response": response.choices[0].message.content,
            "knowledge_used": [],  # Would track IDs if we parsed them
            "model": "groq-llama-3.3-70b",
            "tokens": response.usage.total_tokens,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core classes
    "SkillsKnowledgeBase",
    "KnowledgeEntry",
    "QueryResult",
    "KnowledgeCategory",
    
    # Tier 2 integration
    "GroqWithRAG",
    
    # Singleton instance
    "knowledge_base",
    
    # Constants
    "CATEGORY_NAMESPACES",
]
