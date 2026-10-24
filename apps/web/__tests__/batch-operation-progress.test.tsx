import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { BatchOperationProgress } from "@/components/batch-operation-progress";

describe("BatchOperationProgress", () => {
  it("renders", () => {
    const { container } = render(
      <BatchOperationProgress batchId="batch_abc" operation="tag" total={10}
        completed={7} failed={1} progressPct={70} status="in_progress" onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("tag Batch");
    expect(container.textContent).toContain("batch_abc");
    expect(container.textContent).toContain("70%");
    expect(container.textContent).toContain("✅ 7");
    expect(container.textContent).toContain("❌ 1");
    expect(container.textContent).toContain("Cancel");
  });
});
