import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IrDashboardPanel } from "@/components/ir-dashboard-panel";
describe("IrDashboardPanel", () => {
  it("renders", () => {
    const { container } = render(
      <IrDashboardPanel activeCount={2} resolvedToday={3} primaryOncall="alice"
        escalationNeeded={true} severityCounts={{ P1: 1, P3: 1 }} />
    );
    expect(container.textContent).toContain("2 ACTIVE INCIDENTS");
    expect(container.textContent).toContain("ESCALATION NEEDED");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("3");
  });
});
