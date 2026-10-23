import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BatchProgressBar } from "@/components/batch-progress-bar";

describe("BatchProgressBar", () => {
  it("renders progress", () => {
    const { container } = render(
      <BatchProgressBar totalItems={250} processed={240} failed={10}
        remaining={0} progressDisplay="100.0%" batchesTotal={3} status="completed" />
    );
    expect(container.textContent).toContain("Batch Processing");
    expect(container.textContent).toContain("100.0%");
    expect(container.textContent).toContain("240");
    expect(container.textContent).toContain("10 failed");
    expect(container.textContent).toContain("completed");
    expect(container.textContent).toContain("3 batches");
  });
});
