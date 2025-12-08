# Modal Integration for Roofing Company OS

## Why Modal?

**Current Tier Architecture:**
```
Tier 0: Python Rules     → $0, instant
Tier 1: Groq (generic)   → $0.0001, fast
Tier 2: Anthropic        → $0.01, smart
```

**Enhanced with Modal:**
```
Tier 0:   Python Rules           → $0, instant
Tier 0.5: Modal (fine-tuned)     → ~$0.00005, fast, domain-expert
Tier 1:   Groq (fallback)        → $0.0001, fast
Tier 2:   Anthropic (complex)    → $0.01, advanced reasoning
```

A fine-tuned model on roofing/construction data will:
- Understand industry terminology natively
- Know spec sections, codes, best practices
- Require less prompt engineering
- Be faster and cheaper than generic models
- Improve over time with your data

## Modal Setup

### 1. Installation & Auth
```bash
pip install modal
modal setup
```

### 2. Project Structure
```
roofing-os/
├── modal_app/
│   ├── __init__.py
│   ├── inference.py      # Production inference
│   ├── training.py       # Fine-tuning pipeline
│   ├── batch.py          # Batch processing
│   └── sandbox.py        # Code execution
├── training_data/
│   ├── conversations/    # Chat logs for training
│   ├── specs/            # Spec section examples
│   └── documents/        # RFIs, submittals, etc.
└── models/
    └── roofing-llm/      # Fine-tuned model weights
```

## Inference Service

```python
"""
modal_app/inference.py
Production inference for fine-tuned roofing model
"""

import modal

# Define the Modal app
app = modal.App("roofing-inference")

# Container image with model dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "accelerate",
        "bitsandbytes",
        "peft",  # For LoRA fine-tuned models
    )
)

# Model volume for persistent storage
model_volume = modal.Volume.from_name("roofing-models", create_if_missing=True)
MODEL_DIR = "/models"


@app.cls(
    gpu="L4",  # Cost-effective for inference (~$0.30/hr)
    image=image,
    volumes={MODEL_DIR: model_volume},
    container_idle_timeout=300,  # Keep warm for 5 min
    allow_concurrent_inputs=10,  # Handle multiple requests
)
class RoofingLLM:
    """Fine-tuned LLM for roofing industry queries"""
    
    @modal.enter()
    def load_model(self):
        """Load model once when container starts"""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch
        
        # Use fine-tuned model or base model
        model_path = f"{MODEL_DIR}/roofing-llm-v1"
        
        # Check if fine-tuned model exists
        import os
        if os.path.exists(model_path):
            self.model_name = model_path
        else:
            # Fallback to base model (Qwen or Llama)
            self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            load_in_4bit=True,  # Quantized for speed
        )
        
        # Roofing-specific system prompt
        self.system_prompt = """You are an expert roofing and waterproofing assistant 
for a commercial roofing contractor. You have deep knowledge of:
- Division 07 specifications (07 50 00 Membrane, 07 60 00 Flashing, etc.)
- TPO, EPDM, PVC, modified bitumen, and BUR systems
- Production rates, material calculations, labor estimating
- Shop drawings, submittals, RFIs, change orders
- OSHA safety requirements for roofing
- Union labor practices (Local 30)

Be direct, practical, and use correct construction terminology.
Reference spec sections when relevant."""

    @modal.method()
    def generate(self, prompt: str, max_tokens: int = 500) -> dict:
        """Generate response for roofing query"""
        import time
        import torch
        
        start = time.time()
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:], 
            skip_special_tokens=True
        )
        
        latency = (time.time() - start) * 1000
        
        return {
            "response": response,
            "latency_ms": latency,
            "model": self.model_name,
            "tier": "modal"
        }
    
    @modal.method()
    def calculate_materials(self, area_sf: float, system: str) -> dict:
        """Specialized material calculation with domain knowledge"""
        
        # This could use the model or be pure Python
        # Hybrid approach: validate with model, calculate with code
        
        COVERAGE = {
            "tpo": 1000,  # SF per roll
            "epdm": 1000,
            "pvc": 1000,
            "polyiso": 32,  # SF per board
        }
        
        WASTE = {
            "tpo": 0.10,
            "epdm": 0.10,
            "pvc": 0.10,
            "polyiso": 0.05,
        }
        
        import math
        
        system_lower = system.lower()
        coverage = COVERAGE.get(system_lower, 1000)
        waste = WASTE.get(system_lower, 0.10)
        
        net_area = area_sf * (1 + waste)
        units = math.ceil(net_area / coverage)
        
        return {
            "area_sf": area_sf,
            "system": system,
            "waste_factor": waste,
            "net_area": net_area,
            "units_needed": units,
            "unit_type": "rolls" if coverage == 1000 else "boards"
        }


# Standalone function for quick queries
@app.function(gpu="L4", image=image, volumes={MODEL_DIR: model_volume})
def quick_query(prompt: str) -> str:
    """Quick inference without class overhead"""
    from transformers import pipeline
    
    pipe = pipeline(
        "text-generation",
        model="Qwen/Qwen2.5-3B-Instruct",  # Smaller for speed
        device_map="auto",
        max_new_tokens=256,
    )
    
    result = pipe(prompt)
    return result[0]["generated_text"]


# Health check endpoint
@app.function()
def health_check() -> dict:
    return {"status": "healthy", "service": "roofing-inference"}
```

## Training Pipeline

```python
"""
modal_app/training.py
Fine-tuning pipeline for roofing domain model
"""

import modal

app = modal.App("roofing-training")

# Training image with full dependencies
training_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "datasets",
        "accelerate",
        "bitsandbytes",
        "peft",
        "trl",  # Transformer Reinforcement Learning
        "wandb",  # Experiment tracking
    )
)

# Volumes for data and models
data_volume = modal.Volume.from_name("roofing-training-data", create_if_missing=True)
model_volume = modal.Volume.from_name("roofing-models", create_if_missing=True)

DATA_DIR = "/data"
MODEL_DIR = "/models"


@app.function(
    gpu="A100",  # Need power for training
    image=training_image,
    volumes={DATA_DIR: data_volume, MODEL_DIR: model_volume},
    timeout=3600 * 4,  # 4 hour timeout for training
)
def fine_tune_roofing_model(
    base_model: str = "Qwen/Qwen2.5-7B-Instruct",
    epochs: int = 3,
    batch_size: int = 4,
):
    """Fine-tune base model on roofing industry data"""
    
    from datasets import load_dataset, Dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        TrainingArguments,
        BitsAndBytesConfig,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    import torch
    import json
    import os
    
    print(f"Starting fine-tuning with base model: {base_model}")
    
    # Load training data
    training_data = []
    data_path = f"{DATA_DIR}/training_conversations.jsonl"
    
    if os.path.exists(data_path):
        with open(data_path, "r") as f:
            for line in f:
                training_data.append(json.loads(line))
    else:
        # Generate sample training data if none exists
        training_data = generate_sample_training_data()
    
    print(f"Loaded {len(training_data)} training examples")
    
    # Convert to dataset
    dataset = Dataset.from_list(training_data)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Quantization config for efficient training
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
    )
    
    model = prepare_model_for_kbit_training(model)
    
    # LoRA config for efficient fine-tuning
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, lora_config)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=f"{MODEL_DIR}/roofing-llm-v1",
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=10,
        save_steps=100,
        fp16=True,
    )
    
    # Format function for training
    def format_example(example):
        return f"""<|im_start|>system
You are an expert roofing assistant.<|im_end|>
<|im_start|>user
{example['prompt']}<|im_end|>
<|im_start|>assistant
{example['response']}<|im_end|>"""
    
    # Train
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
        formatting_func=format_example,
        max_seq_length=2048,
    )
    
    trainer.train()
    
    # Save
    trainer.save_model(f"{MODEL_DIR}/roofing-llm-v1")
    model_volume.commit()
    
    return {"status": "complete", "model_path": f"{MODEL_DIR}/roofing-llm-v1"}


def generate_sample_training_data():
    """Generate sample training data for roofing domain"""
    
    examples = [
        # Production rates
        {
            "prompt": "What's the production rate for TPO adhered membrane?",
            "response": "A 5-man crew can typically install 4,000-5,000 SF per day of adhered TPO membrane. This assumes standard conditions - clean dry substrate, good weather, and experienced crew. Adjust down 10-20% for complex geometry or many penetrations."
        },
        {
            "prompt": "How many square feet can we tear off in a day?",
            "response": "For single-ply tear-off, expect 5,000-6,000 SF per day with a 5-man crew. Multi-layer or BUR tear-off is slower at 3,000-4,000 SF/day due to weight and disposal. Always factor in dumpster availability and crane/hoist access."
        },
        
        # Material calculations
        {
            "prompt": "Calculate membrane for a 15,000 SF roof",
            "response": "For 15,000 SF with 10% waste:\n- Net area: 16,500 SF\n- 10' TPO rolls (1,000 SF each): 17 rolls needed\n- Don't forget: seam tape, adhesive (~165 gallons at 100 SF/gal), and detail membrane for flashings."
        },
        
        # Spec interpretation
        {
            "prompt": "What does 07 52 00 cover?",
            "response": "07 52 00 is Modified Bituminous Membrane Roofing. This includes:\n- SBS and APP modified bitumen sheets\n- Torch-applied, cold-applied, and self-adhered systems\n- Related flashings, accessories, and coatings\n\nTypically 2-ply or 3-ply systems. Check submittal requirements for manufacturer certification."
        },
        
        # RFI writing
        {
            "prompt": "Help me write an RFI about a drain location conflict",
            "response": """RFI #[XXX]
Project: [Name]
Date: [Date]

Subject: Roof Drain Location Conflict with Structural Beam

Description:
Drawing A-501 shows roof drain RD-4 at grid intersection C/3. Structural drawing S-301 indicates a W12×26 beam at this location, creating a conflict.

Request:
Please provide direction on one of the following:
1. Relocate drain to clear beam (suggest 2'-0" north to C/3.5)
2. Provide sump detail to work around beam
3. Confirm alternate drain configuration

Impact if not resolved: Delay to roofing installation in Area C.

Attachments: Marked-up drawings showing conflict."""
        },
        
        # Safety
        {
            "prompt": "What's the OSHA requirement for fall protection on roofs?",
            "response": "Per OSHA 29 CFR 1926.501 (Subpart M), fall protection is required at 6 feet or more on roofing work. Options include:\n\n1. Warning lines at 15' from edge (work inside only)\n2. Warning lines at 6' from edge with safety monitor\n3. Guardrail system (42\" top rail)\n4. Personal fall arrest system (5,000 lb anchor)\n\nLow-slope roofs may use warning line/monitor combination. Document everything in your Fall Protection Plan."
        },
        
        # Estimating
        {
            "prompt": "What's a typical waste factor for insulation?",
            "response": "Standard waste factor for polyiso insulation is 5%. This accounts for:\n- Cuts around penetrations and edges\n- Damaged boards\n- Minor fitting waste\n\nIncrease to 7-8% for complex roofs with many penetrations or irregular shapes. Tapered systems are calculated differently - waste is built into the layout."
        },
        
        # Shop drawings
        {
            "prompt": "What layer should base flashing details be on?",
            "response": "Use layer ROOF-FLASH-BASE with color Yellow (2) and lineweight 0.35mm. This follows standard convention:\n\n- ROOF-MEMB (Cyan) - field membrane\n- ROOF-FLASH-BASE (Yellow) - base flashings\n- ROOF-FLASH-CAP (Red) - counter flashings\n- ROOF-EDGE (Magenta) - edge metal\n\nKeep consistent across all sheets for clarity."
        },
    ]
    
    return examples


@app.function(
    image=training_image,
    volumes={DATA_DIR: data_volume},
)
def prepare_training_data(conversations: list[dict]):
    """Process conversations into training format"""
    
    import json
    
    training_examples = []
    
    for conv in conversations:
        # Extract prompt/response pairs
        if "messages" in conv:
            for i in range(0, len(conv["messages"]) - 1, 2):
                if conv["messages"][i]["role"] == "user":
                    training_examples.append({
                        "prompt": conv["messages"][i]["content"],
                        "response": conv["messages"][i + 1]["content"],
                    })
    
    # Save to volume
    with open(f"{DATA_DIR}/training_conversations.jsonl", "a") as f:
        for example in training_examples:
            f.write(json.dumps(example) + "\n")
    
    data_volume.commit()
    
    return {"examples_added": len(training_examples)}
```

## Batch Processing

```python
"""
modal_app/batch.py
Batch processing for documents, specs, etc.
"""

import modal

app = modal.App("roofing-batch")

image = modal.Image.debian_slim().pip_install(
    "pypdf2",
    "python-docx", 
    "openpyxl",
    "transformers",
    "torch",
)


@app.function(gpu="T4", image=image)
def process_spec_document(pdf_bytes: bytes) -> dict:
    """Extract and categorize content from spec PDF"""
    
    from PyPDF2 import PdfReader
    from io import BytesIO
    
    reader = PdfReader(BytesIO(pdf_bytes))
    
    sections = {
        "07 50 00": [],  # Membrane Roofing
        "07 52 00": [],  # Modified Bitumen
        "07 54 00": [],  # Thermoplastic
        "07 55 00": [],  # EPDM
        "07 60 00": [],  # Flashing
        "07 62 00": [],  # Sheet Metal
    }
    
    current_section = None
    
    for page in reader.pages:
        text = page.extract_text()
        
        # Detect section headers
        for section in sections.keys():
            if section in text:
                current_section = section
        
        if current_section:
            sections[current_section].append(text)
    
    return sections


@app.function(image=image, concurrency_limit=10)
def process_drawings_batch(drawing_files: list[bytes]) -> list[dict]:
    """Process multiple drawings in parallel"""
    
    results = []
    for drawing in drawing_files:
        # Process each drawing
        result = extract_drawing_info(drawing)
        results.append(result)
    
    return results


def extract_drawing_info(drawing_bytes: bytes) -> dict:
    """Extract info from a drawing file"""
    # Placeholder - would use vision model or CAD parsing
    return {
        "extracted": True,
        "size": len(drawing_bytes)
    }


@app.function(image=image)
def generate_submittal_package(project_data: dict) -> bytes:
    """Generate complete submittal package"""
    
    from docx import Document
    from io import BytesIO
    
    doc = Document()
    doc.add_heading(f"Submittal Package - {project_data['project_name']}", 0)
    
    # Add sections based on project data
    doc.add_heading("Section 1: Product Data", level=1)
    doc.add_paragraph(f"Membrane System: {project_data.get('system', 'TPO')}")
    
    doc.add_heading("Section 2: Shop Drawings", level=1)
    doc.add_paragraph("See attached drawings")
    
    # Save to bytes
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
```

## Sandbox for Code Execution

```python
"""
modal_app/sandbox.py
Sandboxed execution for generated code (AutoCAD scripts, etc.)
"""

import modal

app = modal.App("roofing-sandbox")


@app.function()
def run_autocad_script(script: str) -> dict:
    """
    Execute AutoCAD script in sandbox
    Returns validation results
    """
    
    # Create sandbox for code execution
    sandbox = modal.Sandbox.create(
        image=modal.Image.debian_slim().pip_install("ezdxf"),
        timeout=60,
    )
    
    try:
        # Validate script syntax
        process = sandbox.exec("python", "-c", f"""
import ezdxf

# Validate DXF generation script
script = '''{script}'''
exec(script)
print("Script validated successfully")
""")
        
        stdout = process.stdout.read()
        stderr = process.stderr.read()
        
        return {
            "valid": process.returncode == 0,
            "stdout": stdout,
            "stderr": stderr
        }
    finally:
        sandbox.terminate()


@app.function()
def execute_calculation(formula: str, variables: dict) -> dict:
    """Safely execute calculation formulas"""
    
    sandbox = modal.Sandbox.create(
        image=modal.Image.debian_slim(),
        timeout=10,
    )
    
    try:
        # Build safe execution context
        var_assignments = "\n".join(f"{k} = {v}" for k, v in variables.items())
        
        code = f"""
import math

{var_assignments}

result = {formula}
print(result)
"""
        
        process = sandbox.exec("python", "-c", code)
        result = process.stdout.read().strip()
        
        return {
            "result": float(result) if result else None,
            "formula": formula,
            "variables": variables
        }
    finally:
        sandbox.terminate()
```

## Integration with Architect AI

```python
"""
Updated rules_engine.py with Modal integration
"""

import modal
from typing import Dict, Any

# Reference the Modal app
inference_app = modal.App.lookup("roofing-inference")
RoofingLLM = modal.Cls.lookup("roofing-inference", "RoofingLLM")


class Tier:
    PYTHON = 0
    MODAL = 0.5  # New tier!
    GROQ = 1
    ANTHROPIC = 2


async def process_query(query: str, context: Dict = None) -> Dict:
    """
    Enhanced query processing with Modal tier
    """
    
    # Tier 0: Python rules (instant, free)
    tier, handler, params = route_query(query, context)
    if tier == Tier.PYTHON:
        return handle_tier_0(handler, params)
    
    # Tier 0.5: Modal fine-tuned model (fast, cheap, domain-expert)
    # Use for most natural language queries
    try:
        llm = RoofingLLM()
        result = llm.generate.remote(query)
        
        # Check confidence - if low, escalate
        if needs_escalation(result):
            return await handle_tier_1_groq(query, context)
        
        return {
            "tier": "modal",
            "response": result["response"],
            "latency_ms": result["latency_ms"],
            "cost": 0.00005  # Estimated Modal cost
        }
    except Exception as e:
        # Fallback to Groq if Modal fails
        print(f"Modal error: {e}, falling back to Groq")
        return await handle_tier_1_groq(query, context)


def needs_escalation(result: Dict) -> bool:
    """Check if Modal response needs escalation"""
    response = result.get("response", "").lower()
    
    uncertainty_signals = [
        "i'm not sure",
        "i don't know",
        "you should consult",
        "beyond my",
    ]
    
    return any(signal in response for signal in uncertainty_signals)


# Cost comparison
COST_PER_QUERY = {
    "tier_0_python": 0.0,
    "tier_05_modal": 0.00005,  # ~$0.30/hr GPU ÷ queries/hr
    "tier_1_groq": 0.0001,
    "tier_2_anthropic": 0.01,
}

# Expected distribution with Modal
TARGET_DISTRIBUTION = {
    "tier_0": 0.40,   # 40% Python rules
    "tier_05": 0.50,  # 50% Modal (fine-tuned)
    "tier_1": 0.08,   # 8% Groq fallback
    "tier_2": 0.02,   # 2% Anthropic complex
}

# Monthly cost estimate (10K queries)
def estimate_monthly_cost(queries: int = 10000) -> Dict:
    return {
        "tier_0": queries * TARGET_DISTRIBUTION["tier_0"] * COST_PER_QUERY["tier_0_python"],
        "tier_05": queries * TARGET_DISTRIBUTION["tier_05"] * COST_PER_QUERY["tier_05_modal"],
        "tier_1": queries * TARGET_DISTRIBUTION["tier_1"] * COST_PER_QUERY["tier_1_groq"],
        "tier_2": queries * TARGET_DISTRIBUTION["tier_2"] * COST_PER_QUERY["tier_2_anthropic"],
        "total": (
            queries * TARGET_DISTRIBUTION["tier_0"] * COST_PER_QUERY["tier_0_python"] +
            queries * TARGET_DISTRIBUTION["tier_05"] * COST_PER_QUERY["tier_05_modal"] +
            queries * TARGET_DISTRIBUTION["tier_1"] * COST_PER_QUERY["tier_1_groq"] +
            queries * TARGET_DISTRIBUTION["tier_2"] * COST_PER_QUERY["tier_2_anthropic"]
        ),
        "vs_all_anthropic": queries * 0.01,
    }

# Example: 10K queries/month
# Total: ~$5.30 vs $100 all-Anthropic = 95% savings
```

## Training Data Collection

```python
"""
Automatic training data collection from production queries
"""

def log_for_training(query: str, response: str, feedback: str = None):
    """Log successful interactions for training data"""
    
    import json
    from datetime import datetime
    
    # Only log good interactions
    if feedback == "positive" or feedback is None:
        example = {
            "timestamp": datetime.now().isoformat(),
            "prompt": query,
            "response": response,
            "feedback": feedback
        }
        
        # Append to training data volume
        prepare_training_data = modal.Function.lookup(
            "roofing-training", 
            "prepare_training_data"
        )
        prepare_training_data.remote([example])


def trigger_retraining(min_examples: int = 500):
    """Trigger model retraining when enough new data"""
    
    fine_tune = modal.Function.lookup(
        "roofing-training",
        "fine_tune_roofing_model"
    )
    
    # This runs async - takes a few hours
    call = fine_tune.spawn()
    
    return {"training_job": call.object_id}
```

## Deployment Commands

```bash
# Deploy inference service
modal deploy modal_app/inference.py

# Run training job
modal run modal_app/training.py::fine_tune_roofing_model

# Check logs
modal app logs roofing-inference

# Scale settings are automatic based on traffic
```

## Cost Comparison

| Tier | Provider | Cost/Query | Speed | Use Case |
|------|----------|------------|-------|----------|
| 0 | Python | $0 | <10ms | Lookups, calculations |
| 0.5 | Modal | ~$0.00005 | ~200ms | Domain queries (50%) |
| 1 | Groq | ~$0.0001 | ~300ms | Fallback, generic |
| 2 | Anthropic | ~$0.01 | ~2s | Complex reasoning |

**Monthly Estimate (10K queries):**
- With Modal: ~$5-10
- Without Modal (all Groq/Anthropic): ~$50-100
- All Anthropic: ~$100

**Additional Modal Costs:**
- GPU time: ~$0.30-1.50/hr depending on GPU
- Storage: Minimal for model weights
- Training: ~$5-20 per training run (A100 for a few hours)
