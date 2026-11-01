import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogRetentionPanel } from "@/components/log-retention-panel";
describe("LogRetentionPanel", () => {
  it("renders", () => {
    const { container } = render(
      <LogRetentionPanel toKeep={100} toDelete={50} sizeFreedMb={700}
        currentGb={50} maxProjectedGb={150} retentionDays={30} />
    );
    expect(container.textContent).toContain("Log Retention");
    expect(container.textContent).toContain("30d policy");
    expect(container.textContent).toContain("700MB reclaimable");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("50");
    expect(container.textContent).toContain("50/150GB");
  });
});
