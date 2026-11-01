import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CostAlertBanner } from "@/components/cost-alert-banner";

describe("CostAlertBanner", () => {
  it("renders warning", () => {
    const alerts = [{ level: "warning", message: "90% consumed" }];
    const { container } = render(
      <CostAlertBanner currentSpend={900} budget={1000} pctUsed={90}
        projectedSpend={1200} alerts={alerts} status="warning" onManage={vi.fn()} />
    );
    expect(container.textContent).toContain("Cost Monitor");
    expect(container.textContent).toContain("$900.00");
    expect(container.textContent).toContain("$1000.00");
    expect(container.textContent).toContain("90%");
    expect(container.textContent).toContain("⚠️");
    expect(container.textContent).toContain("90% consumed");
  });
});
