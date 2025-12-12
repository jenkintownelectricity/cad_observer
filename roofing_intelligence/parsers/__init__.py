"""
ROOFIO Document Parser Framework
AI-powered document parsing with learning feedback loop

The beauty: Start a new project by dumping documents into parsers.
AI suggests values - click to confirm, or correct to teach it.
"""

from .base_parser import BaseParser, ParserResult, Suggestion
from .contract_parser import ContractParser
from .spec_parser import SpecificationParser
from .assembly_parser import AssemblyLetterParser
from .roof_plan_parser import RoofPlanParser
from .sov_parser import ScheduleOfValuesParser

# Parser registry - maps document types to parser classes
PARSER_REGISTRY = {
    'contract': ContractParser,
    'subcontract': ContractParser,
    'specs': SpecificationParser,
    'assembly-letter': AssemblyLetterParser,
    'roof-plan': RoofPlanParser,
    'drawings': RoofPlanParser,
    'sov': ScheduleOfValuesParser,
}

def get_parser(doc_type: str) -> BaseParser:
    """Get the appropriate parser for a document type"""
    parser_class = PARSER_REGISTRY.get(doc_type)
    if parser_class:
        return parser_class()
    return BaseParser()

def parse_document(doc_type: str, content: str, filename: str = None) -> ParserResult:
    """Parse a document and return extracted data with suggestions"""
    parser = get_parser(doc_type)
    return parser.parse(content, filename)

__all__ = [
    'BaseParser',
    'ParserResult',
    'Suggestion',
    'ContractParser',
    'SpecificationParser',
    'AssemblyLetterParser',
    'RoofPlanParser',
    'ScheduleOfValuesParser',
    'get_parser',
    'parse_document',
    'PARSER_REGISTRY',
]
