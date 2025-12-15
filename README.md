# Intelligent Excel Transformation System

An AI-powered system that automatically transforms messy, unstructured Excel files into clean, database-ready formats using LLM-based analysis and dynamic code generation.

## Overview

This system uses Large Language Models (LLMs) to:
- **Analyze** any messy Excel format (no hardcoded logic)
- **Understand** business semantics and data structure
- **Generate** custom transformation Python code
- **Validate** output against ground truth samples
- **Self-optimize** through iterative improvement
- **Learn** from successful patterns for future reuse

## Key Features

- **Zero-Shot Excel Processing:** Works with unknown Excel formats without manual coding
- **LLM-Powered Analysis:** Intelligently detects patterns, headers, blocks, and structure
- **Dynamic Code Generation:** Generates custom transformation scripts for each file
- **Self-Validating:** Compares output with ground truth (≥99% accuracy required)
- **Iterative Optimization:** Automatically debugs and improves code if validation fails
- **Pattern Learning:** Builds a library of successful transformations for reuse
- **Complete Audit Trail:** Saves analysis reports, generated code, and validation results

## System Architecture

```
Input (Messy Excel + Ground Truth Sample)
    ↓
Phase 1: LLM-Powered Analysis
    ├─ Structure Discovery (layout, headers, blocks, patterns)
    ├─ Semantic Understanding (entities, metrics, dimensions)
    └─ Transformation Planning (compare source vs target)
    ↓
Phase 2: Dynamic Code Generation
    └─ LLM generates custom Python transformation script
    ↓
Phase 3: Execution & Validation
    ├─ Run generated code in sandbox
    └─ Validate against ground truth (schema + values)
    ↓
Phase 4: Iterative Optimization (if accuracy < 99%)
    ├─ Error analysis
    ├─ LLM-powered debugging
    └─ Re-generate improved code
    ↓
Phase 5: Output & Learning
    ├─ Save cleaned data (CSV, Excel, SQLite, JSON)
    ├─ Save artifacts (code, analysis, reports)
    └─ Update pattern library
```

## Directory Structure

```
intelligent-excel-cleaner/
│
├── main.py                          # CLI orchestrator
├── config.yaml                      # System configuration
├── requirements.txt                 # Dependencies
│
├── core/
│   ├── orchestrator.py              # Main pipeline coordinator
│   └── llm_client.py                # LLM API client (OpenAI/Anthropic)
│
├── analyzer/
│   ├── structure_analyzer.py        # Detect Excel patterns (LLM-assisted)
│   ├── semantic_analyzer.py         # Understand business meaning (LLM)
│   ├── ground_truth_comparator.py   # Compare messy vs ground truth
│   ├── prompts/                     # LLM prompt templates
│   │   ├── structure_analysis.txt
│   │   ├── semantic_analysis.txt
│   │   └── transformation_planning.txt
│   └── analysis_report.py           # Generate analysis JSON
│
├── generator/
│   ├── code_generator.py            # Generate transformation code (LLM)
│   ├── prompt_builder.py            # Build code generation prompts
│   ├── code_templates/              # Reusable code snippets
│   │   ├── base_template.py
│   │   ├── unpivot_template.py
│   │   └── block_extraction_template.py
│   └── generated/                   # Generated transform scripts
│
├── executor/
│   ├── sandbox.py                   # Safe code execution environment
│   ├── runner.py                    # Execute generated transformation
│   └── error_handler.py             # Capture and parse errors
│
├── validator/
│   ├── schema_validator.py          # Compare schemas
│   ├── data_validator.py            # Compare data values
│   ├── metrics.py                   # Calculate accuracy metrics
│   └── mismatch_reporter.py         # Report differences
│
├── optimizer/
│   ├── error_analyzer.py            # Analyze validation failures
│   ├── code_optimizer.py            # LLM-powered code improvement
│   ├── prompts/
│   │   └── debug_and_fix.txt        # Debugging prompt template
│   └── iteration_manager.py         # Manage optimization loops
│
├── output/
│   ├── exporter.py                  # Export cleaned data
│   ├── artifact_saver.py            # Save analysis, code, reports
│   └── metadata_generator.py        # Generate lineage metadata
│
├── learning/
│   ├── pattern_library.py           # Store successful patterns
│   ├── similarity_matcher.py        # Match new files to patterns
│   └── patterns/                    # Saved patterns (JSON)
│
├── utils/
│   ├── logger.py                    # Logging configuration
│   ├── excel_reader.py              # Excel utilities
│   ├── helpers.py                   # Common utilities
│   └── config_loader.py             # Load config.yaml
│
├── tests/
│   ├── test_analyzer.py
│   ├── test_generator.py
│   ├── test_validator.py
│   └── fixtures/
│
├── data/                            # Input files
│   ├── messy/
│   └── ground_truth/
│
└── results/                         # Output directory
    ├── cleaned_data/
    ├── artifacts/
    └── reports/
```

## Installation

### Prerequisites

- Python 3.8+
- API key for LLM provider (Anthropic Claude or OpenAI)

### Setup

```bash
# Clone repository
cd ExcelSheetAnalysis

# Install dependencies
pip install -r requirements.txt

# Set up API key (choose one)
export ANTHROPIC_API_KEY="your-api-key"
# OR
export OPENAI_API_KEY="your-api-key"

# Configure system (optional - edit config.yaml)
# Set LLM provider, model, thresholds, etc.
```

## Usage

### Basic Transformation

```bash
python main.py \
    --messy data/messy/messy_sales_report_only.xlsx \
    --ground-truth data/ground_truth/sales_data_ground_truth_only.xlsx \
    --output results/cleaned_data/
```

### With Optimization

```bash
python main.py \
    --messy data/messy/messy_sales_report_only.xlsx \
    --ground-truth data/ground_truth/sales_data_ground_truth_only.xlsx \
    --output results/cleaned_data/ \
    --max-iterations 5 \
    --verbose
```

### Reuse Pattern Library

```bash
python main.py \
    --messy data/messy/new_file.xlsx \
    --ground-truth data/ground_truth/new_target.xlsx \
    --output results/cleaned_data/ \
    --check-library
```

### Command Line Options

```
--messy PATH              Path to messy Excel file (required)
--ground-truth PATH       Path to ground truth sample (required)
--output PATH             Output directory for cleaned data
--max-iterations N        Max optimization iterations (default: 5)
--accuracy-threshold N    Required accuracy 0-1 (default: 0.99)
--check-library           Check pattern library for similar transformations
--format FORMAT           Output format: csv, excel, sqlite, json (default: csv,excel)
--verbose                 Enable verbose logging
--save-artifacts          Save analysis and generated code (default: true)
```

## How It Works

### 1. Structure Analysis

The system uses an LLM to analyze the messy Excel file and identify:
- Layout patterns (wide format, blocks, merged cells, etc.)
- Header structure and hierarchy
- Data row boundaries
- Repeating patterns
- Noise elements (totals, footers, empty rows)

### 2. Semantic Understanding

LLM extracts business meaning:
- Entities (Region, Product, Customer, etc.)
- Metrics (Revenue, Units Sold, etc.)
- Dimensions (Time, Geography, Category)
- Relationships and grain

### 3. Transformation Planning

By comparing the messy file with ground truth:
- Determines required transformations (pivot, unpivot, merge, etc.)
- Maps source fields to target schema
- Plans calculation and filtering logic

### 4. Code Generation

LLM generates a complete Python script with:
- Data extraction functions
- Transformation logic
- Validation checks
- Error handling

### 5. Execution & Validation

- Runs generated code in a safe sandbox
- Validates output against ground truth
- Checks schema match and value accuracy
- Generates detailed comparison report

### 6. Optimization Loop

If validation fails (accuracy < 99%):
- Analyzes error patterns
- LLM debugs the code
- Generates improved version
- Re-executes and validates
- Repeats up to max iterations

### 7. Learning

Successful transformations are saved as patterns:
- Future similar files can reuse the pattern
- Skips analysis and generation phases
- Faster processing for known formats

## Output

### Cleaned Data

```
results/cleaned_data/
├── cleaned_20241214_1945.csv
├── cleaned_20241214_1945.xlsx
└── cleaned_20241214_1945.db
```

### Artifacts

```
results/artifacts/
├── analysis_20241214_1945.json          # Structure analysis
├── transform_20241214_1945.py           # Generated code
├── validation_20241214_1945.json        # Validation report
└── execution_20241214_1945.log          # Execution logs
```

### Reports

```
results/reports/
└── summary_20241214_1945.html           # Human-readable summary
```

## Configuration

Edit `config.yaml` to customize:

```yaml
llm:
  provider: "anthropic"              # or "openai"
  model: "claude-sonnet-4"          # or "gpt-4"
  api_key_env: "ANTHROPIC_API_KEY"
  temperature: 0.1

validation:
  accuracy_threshold: 0.99           # 99% match required

optimization:
  max_iterations: 5
  enable_learning: true

output:
  formats: ["csv", "excel", "sqlite"]
  save_artifacts: true
```

## Examples

### Example 1: Quarterly Sales Report

**Input:** Wide-format quarterly blocks with merged headers
**Output:** Normalized long format (3,200 rows)
**Accuracy:** 100% match with ground truth

### Example 2: Inventory Report (Future)

**Input:** Pivot table with nested categories
**Output:** Flat table ready for database
**Processing:** Reuses similar pattern from library

## Success Criteria

- ✅ Works with ANY Excel format (not hardcoded)
- ✅ Achieves ≥99% accuracy vs ground truth
- ✅ Minimal human intervention required
- ✅ Complete audit trail maintained
- ✅ Learns and improves over time

## Testing

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/test_end_to_end.py

# Test with sample data
python main.py --messy tests/fixtures/sample_messy.xlsx \
               --ground-truth tests/fixtures/sample_truth.xlsx
```

## Troubleshooting

### Low Validation Accuracy

- Check ground truth sample quality (ensure it's representative)
- Increase max iterations
- Review validation report for patterns
- Manually inspect generated code

### LLM API Errors

- Verify API key is set correctly
- Check API rate limits
- Reduce sample_rows in config if hitting token limits

### Missing Dependencies

```bash
pip install -r requirements.txt --upgrade
```

## Requirements

- Python 3.8+
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- anthropic >= 0.8.0 (if using Claude)
- openai >= 1.0.0 (if using OpenAI)
- pyyaml >= 6.0
- See requirements.txt for full list

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Roadmap

- [ ] Support for multiple ground truth samples
- [ ] Web UI for monitoring transformations
- [ ] Support for additional LLM providers
- [ ] Batch processing mode
- [ ] Real-time transformation suggestions
- [ ] Excel template generation from target schema
