import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BatchProcessorCard from "../src/components/batch-processor-card";

const processingBatch = {
  batch_id: "batch-001",
  status: "processing" as const,
  total: 100,
  processed: 60,
  succeeded: 55,
  failed: 5,
  progress_pct: 60,
  created_at: new Date(Date.now() - 300_000).toISOString(),
};

const completedBatch = {
  batch_id: "batch-002",
  status: "completed" as const,
  total: 50,
  processed: 50,
  succeeded: 50,
  failed: 0,
  progress_pct: 100,
  created_at: new Date(Date.now() - 3_600_000).toISOString(),
};

describe("BatchProcessorCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <BatchProcessorCard batches={[processingBatch]} appName="My App" />,
    );
    expect(container.textContent).toContain("Batch Jobs");
    expect(container.textContent).toContain("My App");
  });

  it("shows active count", () => {
    const { container } = render(<BatchProcessorCard batches={[processingBatch]} appName="App" />);
    expect(container.textContent).toContain("1 active");
  });

  it("renders batch id", () => {
    const { container } = render(<BatchProcessorCard batches={[processingBatch]} appName="App" />);
    expect(container.textContent).toContain("batch-001");
  });

  it("shows progress", () => {
    const { container } = render(<BatchProcessorCard batches={[processingBatch]} appName="App" />);
    expect(container.textContent).toContain("60/100 items");
    expect(container.textContent).toContain("60%");
  });

  it("shows success and failure counts", () => {
    const { container } = render(<BatchProcessorCard batches={[processingBatch]} appName="App" />);
    expect(container.textContent).toContain("55 ok");
    expect(container.textContent).toContain("5 failed");
  });

  it("shows status icons", () => {
    const { container } = render(
      <BatchProcessorCard batches={[processingBatch, completedBatch]} appName="App" />,
    );
    expect(container.textContent).toContain("⚙️");
    expect(container.textContent).toContain("✅");
  });

  it("shows empty state", () => {
    const { container } = render(<BatchProcessorCard batches={[]} appName="App" />);
    expect(container.textContent).toContain("No batch jobs");
  });
});
