import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqBatchPanel } from "@/components/req-batch-panel";
describe("ReqBatchPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqBatchPanel bufferSize={25} maxBatchSize={50} batchesFlushed={100} />
    );
    expect(container.textContent).toContain("Request Batcher");
    expect(container.textContent).toContain("100 batches flushed");
    expect(container.textContent).toContain("25/50");
  });
});
