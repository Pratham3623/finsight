from finsight.config.settings import get_pipeline_settings
from finsight.pipeline.orchestrator import (
    PipelineConfig,
    PipelineOrchestrator,
)


def main() -> None:
    settings = get_pipeline_settings()

    config = PipelineConfig(
        source_path=settings.source_path,
        processed_path=settings.processed_path,
        rejected_path=settings.rejected_path,
    )

    print("FinSight Local ETL Pipeline")
    print("=" * 40)

    result = PipelineOrchestrator(config).run()

    report = result.quality_report
    run = result.run

    print(f"Run ID:           {run.run_id}")
    print(f"Pipeline:         {run.pipeline_name}")
    print(f"Status:           {run.status.value}")
    print()
    print(f"Records extracted: {report.records_extracted:,}")
    print(f"Records processed: {report.records_valid:,}")
    print(f"Records rejected:  {report.records_rejected:,}")
    print()
    print(f"Completeness:    {report.completeness_score:.2f}%")
    print(f"Validity:        {report.validity_score:.2f}%")
    print(f"Uniqueness:      {report.uniqueness_score:.2f}%")
    print(f"Consistency:     {report.consistency_score:.2f}%")
    print(f"Overall quality: {report.overall_quality_score:.2f}%")
    print()
    print(f"Processed: {result.processed_path}")
    print(f"Rejected:  {result.rejected_path}")
    print()
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
