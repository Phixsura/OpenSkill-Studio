import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { BurnAlertPanel } from "@/components/burn-alert-panel";
describe("BurnAlertPanel", () => {
  it("renders firing", () => {
    const { container } = render(
      <BurnAlertPanel firing={true} currentBurnRate={14} mostSevere="critical"
        alerts={[{ window: "5m", burnRate: 14, threshold: 1, severity: "critical" }]} />
    );
    expect(container.textContent).toContain("Burn Alert");
    expect(container.textContent).toContain("CRITICAL");
    expect(container.textContent).toContain("14x");
    expect(container.textContent).toContain("5m");
  });
});
