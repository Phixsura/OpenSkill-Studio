import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RevenueDashboard } from "@/components/revenue-dashboard";

describe("RevenueDashboard", () => {
  it("renders earnings", () => {
    const earnings = { totalGross: 10000, totalNet: 8500, totalFees: 1500, transactionCount: 25 };
    const { container } = render(<RevenueDashboard earnings={earnings} />);
    expect(container.textContent).toContain("$85.00");
    expect(container.textContent).toContain("$100.00");
    expect(container.textContent).toContain("$15.00");
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("Net Earnings");
  });
});
