"""
Groq API Client for Roofio - Division 07 AI Expert

Fast, affordable AI responses using Groq's LLM API.
Tier 1: ~$0.0001 per query (Llama 3.1 70B)
"""

import os
import json
from pathlib import Path

# Try to import groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq package not installed. Run: pip install groq")


# Roofio system prompt
ROOFIO_SYSTEM_PROMPT = """You are ROOFIO, the world's smartest Division 07 (Roofing & Waterproofing) AI expert.

You have deep expertise in:
- ASCE 7-22 wind loads and calculations
- IBC/IRC building codes for roofing
- FM Global standards and approvals
- NRCA Roofing Manual best practices
- All roofing systems: TPO, EPDM, PVC, Modified Bitumen, BUR, Metal
- Manufacturer specifications: Carlisle, Firestone, GAF, Johns Manville, Sika
- Leak detection methods: EFVM, IR thermography, nuclear moisture testing
- Shop drawing standards and CAD detailing

When answering:
1. Be specific and cite codes/standards when relevant
2. Use tables for comparisons
3. Ask clarifying questions if needed (location, building height, system type)
4. Provide actionable recommendations
5. Include relevant spec sections (e.g., "07 54 23 - TPO Membrane")

Format responses with markdown for readability. Use 🏗️ emoji sparingly for personality.
"""


def load_skill_content(skill_ids: list) -> str:
    """Load relevant skill content to inject into the prompt."""
    skill_content = []
    skills_dir = Path(__file__).parent / "skills"

    # Map skill IDs to folder names
    skill_map = {
        'wind': 'wind-uplift-asce',
        'uplift': 'wind-uplift-asce',
        'asce': 'wind-uplift-asce',
        'fm': 'fm-global',
        'nrca': 'nrca',
        'leak': 'leak-detection',
        'tpo': 'roofing-systems',
        'epdm': 'roofing-systems',
        'pvc': 'roofing-systems',
        'membrane': 'roofing-systems',
        'carlisle': 'manufacturers',
        'firestone': 'manufacturers',
        'gaf': 'manufacturers',
        'ibc': 'codes-irc-icc',
        'irc': 'codes-irc-icc',
        'code': 'codes-irc-icc',
        'drafting': 'drafting-innovations',
        'detail': 'drafting-innovations',
        'spri': 'spri',
        'iibec': 'iibec',
        'inspection': 'div07-inspections',
        'testing': 'div07-testing',
    }

    # Find matching skills
    loaded_skills = set()
    for skill_id in skill_ids:
        skill_id_lower = skill_id.lower()
        for keyword, folder in skill_map.items():
            if keyword in skill_id_lower and folder not in loaded_skills:
                skill_path = skills_dir / folder / "SKILL.md"
                if skill_path.exists():
                    try:
                        content = skill_path.read_text()
                        # Truncate if too long (keep first 4000 chars)
                        if len(content) > 4000:
                            content = content[:4000] + "\n...[truncated]"
                        skill_content.append(f"## {folder.upper()} KNOWLEDGE:\n{content}")
                        loaded_skills.add(folder)
                    except Exception as e:
                        print(f"Error loading skill {folder}: {e}")

    return "\n\n".join(skill_content) if skill_content else ""


def ask_groq(question: str, context: dict = None, model: str = "llama-3.1-70b-versatile") -> dict:
    """
    Send a question to Groq API and get a response.

    Args:
        question: User's question
        context: Optional context dict with keywords, query_type, etc.
        model: Groq model to use (default: llama-3.1-70b-versatile)

    Returns:
        dict with 'response', 'citations', 'cost', 'model'
    """
    if not GROQ_AVAILABLE:
        return {
            'response': "Groq package not installed. Run: `pip install groq`",
            'citations': [],
            'cost': 0,
            'model': None,
            'error': 'groq_not_installed'
        }

    # Get API key from environment
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return {
            'response': """🏗️ **Groq API Key Required**

To enable AI-powered responses, set your Groq API key:

**Windows (PowerShell):**
```
$env:GROQ_API_KEY = "your-api-key-here"
```

**Get a free key at:** https://console.groq.com/keys

Groq offers fast, affordable AI (~$0.0001 per query).""",
            'citations': [],
            'cost': 0,
            'model': None,
            'error': 'no_api_key'
        }

    try:
        client = Groq(api_key=api_key)

        # Build context-aware prompt
        system_prompt = ROOFIO_SYSTEM_PROMPT

        # Load relevant skill content based on keywords
        if context and context.get('keywords'):
            skill_content = load_skill_content(context['keywords'])
            if skill_content:
                system_prompt += f"\n\n# REFERENCE MATERIAL:\n{skill_content}"

        # Make API call
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        response_text = completion.choices[0].message.content

        # Calculate approximate cost (Llama 3.1 70B: $0.59/1M input, $0.79/1M output)
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens
        cost = (input_tokens * 0.00000059) + (output_tokens * 0.00000079)

        # Extract citations from response (look for code references)
        citations = extract_citations(response_text)

        return {
            'response': response_text,
            'citations': citations,
            'cost': round(cost, 6),
            'model': model,
            'tokens': {
                'input': input_tokens,
                'output': output_tokens,
                'total': input_tokens + output_tokens
            }
        }

    except Exception as e:
        return {
            'response': f"🏗️ **Error connecting to Groq:**\n\n{str(e)}",
            'citations': [],
            'cost': 0,
            'model': model,
            'error': str(e)
        }


def extract_citations(text: str) -> list:
    """Extract code/standard citations from response text."""
    citations = []

    # Common patterns to look for
    patterns = [
        'ASCE 7', 'IBC', 'IRC', 'FM', 'NRCA', 'ASTM', 'SPRI', 'IIBEC',
        'Section', 'Chapter', 'DS 1-', 'Table', 'Figure'
    ]

    # Simple extraction - look for references
    import re
    for pattern in patterns:
        matches = re.findall(rf'{pattern}[\s\-]?[\d\.\-]+', text, re.IGNORECASE)
        citations.extend(matches[:3])  # Limit per pattern

    # Deduplicate and limit
    seen = set()
    unique_citations = []
    for c in citations:
        c_clean = c.strip()
        if c_clean.lower() not in seen:
            seen.add(c_clean.lower())
            unique_citations.append(c_clean)

    return unique_citations[:5]


# Quick test
if __name__ == "__main__":
    print("Testing Groq client...")
    result = ask_groq("What FM rating do I need for a corner zone in Miami?")
    print(json.dumps(result, indent=2))
