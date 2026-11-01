import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RolloutRiskCard } from "@/components/rollout-risk-card";

describe("RolloutRiskCard", () => {
  it("renders", () => {
    const { container } = render(
      <RolloutRiskCard riskScore={75} riskLevel="critical" recommendCanary={true}
        riskFactors={["large_change", "multi_service", "database_migration"]} />
    );
    expect(container.textContent).toContain("75");
    expect(container.textContent).toContain("Rollout Risk");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("Canary deploy recommended");
    expect(container.textContent).toContain("large change");
    expect(container.textContent).toContain("database migration");
  });
});
