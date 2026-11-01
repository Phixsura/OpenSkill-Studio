import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UsageLimitAlerts } from "@/components/usage-limit-alerts";

describe("UsageLimitAlerts", () => {
  const alerts = [
    { resource: "API Calls", pct: 95, severity: "warning", message: "API Calls at 95%" },
    { resource: "Bandwidth", pct: 110, severity: "critical", message: "Bandwidth at 110%" },
  ];
  it("renders alerts", () => {
    const { container } = render(<UsageLimitAlerts alerts={alerts} hasCritical={true} />);
    expect(container.textContent).toContain("API Calls at 95%");
    expect(container.textContent).toContain("Bandwidth at 110%");
    expect(container.textContent).toContain("🚨");
  });
  it("hides when empty", () => {
    const { container } = render(<UsageLimitAlerts alerts={[]} hasCritical={false} />);
    expect(container.innerHTML).toBe("");
  });
});
