import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetentionChart } from "@/components/retention-chart";

describe("RetentionChart", () => {
  const cohorts = [{ cohort: "2026-W40", size: 100, weeklyRetention: [80, 60, 50, 45] }];
  it("renders chart", () => {
    const { container } = render(<RetentionChart cohorts={cohorts} avgWeek1={80} avgWeek4={45} />);
    expect(container.textContent).toContain("Retention Cohorts");
    expect(container.textContent).toContain("2026-W40");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("W1: 80%");
  });
});
