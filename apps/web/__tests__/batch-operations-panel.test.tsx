import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BatchOperationsPanel } from "@/components/batch-operations-panel";

describe("BatchOperationsPanel", () => {
  const results = [
    { item: "app1", status: "success", reason: null },
    { item: "app2", status: "failed", reason: "not found" },
  ];
  it("renders results", () => {
    const { container } = render(
      <BatchOperationsPanel action="delete" results={results} succeeded={1} failed={1} skipped={0} total={2} dryRun={false} />
    );
    expect(container.textContent).toContain("delete");
    expect(container.textContent).toContain("app1");
    expect(container.textContent).toContain("1✓");
    expect(container.textContent).toContain("1✗");
  });
});
