import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DepRiskCard } from "@/components/dep-risk-card";

describe("DepRiskCard", () => {
  it("renders", () => {
    const { container } = render(
      <DepRiskCard service="web" directDeps={1} transitiveDeps={4}
        maxDepth={3} riskScore={85} riskLevel="critical" />
    );
    expect(container.textContent).toContain("Dependency Risk: web");
    expect(container.textContent).toContain("critical");
    expect(container.textContent).toContain("85/100");
    expect(container.textContent).toContain("1");
    expect(container.textContent).toContain("4");
    expect(container.textContent).toContain("3");
  });
});
