from dataclasses import dataclass

@dataclass
class ParsedQualityResults:
    file_name: str
    test_status: str
    test_duration: str

@dataclass
class ParsedOverviewQualityResults:
    overview_name: str
    overview_value: str