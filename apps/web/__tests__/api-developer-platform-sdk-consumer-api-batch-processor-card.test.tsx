import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BatchProcessorCard from "../src/components/api-developer-platform-sdk-consumer-api-batch-processor-card";

describe("BatchProcessorCard", () => {
  it("renders title and jobs", () => {
    const { container } = render(<BatchProcessorCard />);
    expect(container.textContent).toContain("Batch Processor");
    expect(container.textContent).toContain("b-001");
    expect(container.textContent).toContain("b-003");
  });

  it("shows status and count", () => {
    const { container } = render(<BatchProcessorCard />);
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("3 batch jobs");
  });
});
