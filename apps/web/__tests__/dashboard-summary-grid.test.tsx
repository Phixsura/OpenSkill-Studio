import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DashboardSummaryGrid } from "@/components/dashboard-summary-grid";

describe("DashboardSummaryGrid", () => {
  it("shows all metrics", () => {
    const { container } = render(<DashboardSummaryGrid totalApps={5} published={3} apiCalls={1000} executions={500} webhooks={200} avgHealth={95} />);
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("95%");
  });
  it("renders 6 cards", () => {
    const { container } = render(<DashboardSummaryGrid totalApps={0} published={0} apiCalls={0} executions={0} webhooks={0} avgHealth={100} />);
    expect(container.querySelectorAll("[class*='rounded-lg']").length).toBe(6);
  });
});
