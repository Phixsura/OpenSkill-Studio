import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-batch-request-processor-card";

describe("BatchProcessorCard", () => {
  it("shows batches", () => {
    const batches = [{ batch_id: "b1", item_count: 10, success_count: 8, error_count: 2, total_duration_ms: 150 }];
    const { container } = render(<Card batches={batches} appName="App" />);
    expect(container.textContent).toContain("Batch Processor");
    expect(container.textContent).toContain("b1 (10 items)");
    expect(container.textContent).toContain("150ms");
  });
  it("shows empty", () => {
    const { container } = render(<Card batches={[]} appName="App" />);
    expect(container.textContent).toContain("No batches processed");
  });
});
