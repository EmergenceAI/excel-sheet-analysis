"""
Intelligent Excel Transformation System
AI-powered transformation of messy Excel files to clean, database-ready formats
"""

import argparse
import sys
import os
from utils.config_loader import load_config
from utils.logger import setup_logging
from core.orchestrator import PipelineOrchestrator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI-powered Excel transformation system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transformation
  python main.py --messy data/messy/file.xlsx --ground-truth data/ground_truth/target.xlsx

  # With custom output directory
  python main.py --messy input.xlsx --ground-truth target.xlsx --output results/

  # With pattern library check
  python main.py --messy input.xlsx --ground-truth target.xlsx --check-library

  # Verbose mode
  python main.py --messy input.xlsx --ground-truth target.xlsx --verbose
        """
    )

    # Required arguments
    parser.add_argument(
        "--messy",
        required=True,
        help="Path to messy Excel file"
    )
    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Path to ground truth sample Excel file"
    )

    # Optional arguments
    parser.add_argument(
        "--output",
        default="results",
        help="Output directory for cleaned data and artifacts (default: results/)"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="Maximum optimization iterations (overrides config)"
    )
    parser.add_argument(
        "--accuracy-threshold",
        type=float,
        help="Required accuracy threshold 0.0-1.0 (overrides config)"
    )
    parser.add_argument(
        "--check-library",
        action="store_true",
        help="Check pattern library for similar transformations"
    )
    parser.add_argument(
        "--format",
        nargs="+",
        choices=["csv", "excel", "sqlite", "json"],
        help="Output formats (overrides config)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Validate input files exist
    if not os.path.exists(args.messy):
        print(f"Error: Messy Excel file not found: {args.messy}")
        sys.exit(1)

    if not os.path.exists(args.ground_truth):
        print(f"Error: Ground truth file not found: {args.ground_truth}")
        sys.exit(1)

    try:
        # Load configuration
        config = load_config(args.config)

        # Override config with CLI arguments
        if args.max_iterations:
            config['optimization']['max_iterations'] = args.max_iterations
        if args.accuracy_threshold:
            config['validation']['accuracy_threshold'] = args.accuracy_threshold
        if args.format:
            config['output']['formats'] = args.format
        if args.verbose:
            config['logging']['level'] = 'DEBUG'

        # Setup logging
        logger = setup_logging(config)

        logger.info("="*80)
        logger.info("Intelligent Excel Transformation System")
        logger.info("="*80)
        logger.info(f"Messy file: {args.messy}")
        logger.info(f"Ground truth: {args.ground_truth}")
        logger.info(f"Output directory: {args.output}")
        logger.info(f"Max iterations: {config['optimization']['max_iterations']}")
        logger.info(f"Accuracy threshold: {config['validation']['accuracy_threshold']}")

        # Create orchestrator and run pipeline
        orchestrator = PipelineOrchestrator(config)

        results = orchestrator.run(
            messy_path=args.messy,
            ground_truth_path=args.ground_truth,
            output_dir=args.output,
            check_library=args.check_library
        )

        # Print results summary
        print("\n" + "="*80)
        print("RESULTS SUMMARY")
        print("="*80)

        if results['success']:
            print("✓ Status: SUCCESS")
            print(f"✓ Iterations: {results.get('iterations', 'N/A')}")
            print(f"✓ Accuracy: {results.get('validation_report', {}).get('value_accuracy', 0)*100:.2f}%")
            print(f"✓ Cleaned data: {results.get('cleaned_data', 'N/A')}")
            if results.get('exported_files'):
                print(f"✓ Exported files: {len(results['exported_files'])}")
                for f in results['exported_files']:
                    print(f"  - {f}")
            if results.get('pattern_id'):
                print(f"✓ Pattern saved: {results['pattern_id']}")
        else:
            print("✗ Status: FAILED")
            if results.get('error'):
                print(f"✗ Error: {results['error']}")
            if results.get('validation_report'):
                report = results['validation_report']
                print(f"✗ Accuracy: {report.get('value_accuracy', 0)*100:.2f}%")
                print(f"✗ Mismatches: {report.get('mismatches_count', 'N/A')}")

        print("="*80)

        # Exit with appropriate code
        sys.exit(0 if results['success'] else 1)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
