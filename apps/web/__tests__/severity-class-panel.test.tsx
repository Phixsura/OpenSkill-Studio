import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SeverityClassPanel } from "@/components/severity-class-panel";
describe("SeverityClassPanel", () => {
  it("renders P1", () => {
    const { container } = render(
      <SeverityClassPanel severity="P1" label="Critical" responseTime="15 minutes"
        affectedUsers={10000} servicesDown={3} revenueImpact={50000} dataLoss={true} />
    );
    expect(container.textContent).toContain("P1 — Critical");
    expect(container.textContent).toContain("15 minutes");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("$50,000");
    expect(container.textContent).toContain("YES");
  });
});
