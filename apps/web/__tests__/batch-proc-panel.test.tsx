import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BatchProcPanel } from "@/components/batch-proc-panel";

describe("BatchProcPanel", () => {
  it("renders", () => {
    const { container } = render(
      <BatchProcPanel totalItems={10} batchSize={3} totalBatches={4}
        failedBatches={1} elapsedMs={50}
        batches={[
          { batch: 1, size: 3, status: "success" },
          { batch: 2, size: 3, status: "failed" },
          { batch: 3, size: 3, status: "success" },
          { batch: 4, size: 1, status: "success" },
        ]} />
    );
    expect(container.textContent).toContain("Batch Processor");
    expect(container.textContent).toContain("3/4 OK");
    expect(container.textContent).toContain("50ms");
    expect(container.textContent).toContain("10 items");
  });
});
