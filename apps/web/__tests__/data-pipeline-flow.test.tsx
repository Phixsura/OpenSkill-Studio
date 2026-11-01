import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataPipelineFlow } from "@/components/data-pipeline-flow";

describe("DataPipelineFlow", () => {
  it("renders", () => {
    const { container } = render(
      <DataPipelineFlow name="Analytics ETL" sourceType="postgres" destinationType="bigquery"
        transforms={[{ step: 1, type: "filter" }]} status="active" schedule="0 3 * * *"
        onRun={vi.fn()} onPause={vi.fn()} />
    );
    expect(container.textContent).toContain("Analytics ETL");
    expect(container.textContent).toContain("🐘");
    expect(container.textContent).toContain("📊");
    expect(container.textContent).toContain("🔍");
    expect(container.textContent).toContain("active");
  });
  it("run", () => {
    const fn = vi.fn();
    const { container } = render(
      <DataPipelineFlow name="X" sourceType="postgres" destinationType="s3"
        transforms={[]} status="active" schedule={null} onRun={fn} onPause={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Run Now")!);
    expect(fn).toHaveBeenCalled();
  });
});
