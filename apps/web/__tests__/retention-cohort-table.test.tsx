import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RetentionCohortTable } from "@/components/retention-cohort-table";

describe("RetentionCohortTable", () => {
  const cohorts = [{
    period: "2026-Q3", initial_users: 1000,
    retention_rates: [90, 80, 70, 60, 55, 50, 45, 40], day_30: 60, day_90: 45,
  }];
  it("renders", () => {
    const { container } = render(
      <RetentionCohortTable cohorts={cohorts} avgDay30={60} avgDay90={45} />
    );
    expect(container.textContent).toContain("Retention Cohorts");
    expect(container.textContent).toContain("D30: 60%");
    expect(container.textContent).toContain("D90: 45%");
    expect(container.textContent).toContain("2026-Q3");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("90%");
  });
});
