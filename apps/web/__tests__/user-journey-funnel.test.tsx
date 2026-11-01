import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UserJourneyFunnel } from "@/components/user-journey-funnel";

describe("UserJourneyFunnel", () => {
  const steps = [
    { step: 1, name: "Landing", users: 1000, drop_off: 0, conversion_pct: 100, avg_time_sec: 15 },
    { step: 2, name: "Sign Up", users: 400, drop_off: 600, conversion_pct: 40, avg_time_sec: 60 },
    { step: 3, name: "Action", users: 200, drop_off: 200, conversion_pct: 20, avg_time_sec: 45 },
  ];
  it("renders", () => {
    const { container } = render(
      <UserJourneyFunnel steps={steps} startUsers={1000} overallConversion={20} bottleneck="Sign Up" />
    );
    expect(container.textContent).toContain("User Journey");
    expect(container.textContent).toContain("20% overall conversion");
    expect(container.textContent).toContain("Landing");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("-600");
    expect(container.textContent).toContain("Biggest drop-off: Sign Up");
  });
});
