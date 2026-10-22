import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OrgDashboardHeader } from "@/components/org-dashboard-header";

describe("OrgDashboardHeader", () => {
  it("shows all stats", () => {
    const { container } = render(<OrgDashboardHeader activeApps={5} totalExecutions={1000} errorRate={2.5} health="healthy" pendingUpgrades={1} />);
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("2.5%");
    expect(container.textContent).toContain("healthy");
  });
  it("renders 5 cards", () => {
    const { container } = render(<OrgDashboardHeader activeApps={0} totalExecutions={0} errorRate={0} health="healthy" pendingUpgrades={0} />);
    expect(container.querySelectorAll("[class*='rounded-lg']").length).toBe(5);
  });
});
