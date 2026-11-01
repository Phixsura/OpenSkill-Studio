import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LeadTimeTrendPanel } from "@/components/lead-time-trend-panel";
describe("LeadTimeTrendPanel", () => { it("renders", () => {
    const { container } = render(<LeadTimeTrendPanel trend="improving" recentAvg={3} olderAvg={42} />);
    expect(container.textContent).toContain("Lead Time Trend");
    expect(container.textContent).toContain("improving");
    expect(container.textContent).toContain("3h");
  });
});
