import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ExecHealthReport } from "@/components/exec-health-report";

describe("ExecHealthReport", () => {
  it("renders", () => {
    const { container } = render(
      <ExecHealthReport score={92} grade="A" status="excellent"
        kpis={{ uptime: "99.95%", revenue: "$100,000", users: "5,000",
                deploys_week: 15, incidents: 2, mttr_min: 15 }} />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("92/100");
    expect(container.textContent).toContain("excellent");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("$100,000");
    expect(container.textContent).toContain("5,000");
  });
});
