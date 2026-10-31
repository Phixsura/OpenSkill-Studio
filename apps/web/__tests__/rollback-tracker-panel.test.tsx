import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RollbackTrackerPanel } from "@/components/rollback-tracker-panel";
describe("RollbackTrackerPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RollbackTrackerPanel total={3} automated={2}
        rollbacks={[
          { service: "api", from: "2.0", to: "1.9", reason: "high_error_rate", triggeredBy: "automated" },
        ]} />
    );
    expect(container.textContent).toContain("Rollback Tracker");
    expect(container.textContent).toContain("3 rollbacks");
    expect(container.textContent).toContain("2 auto");
    expect(container.textContent).toContain("api: 2.0 → 1.9");
    expect(container.textContent).toContain("high_error_rate");
  });
});
