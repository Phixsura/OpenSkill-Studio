import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployConfidence } from "@/components/deploy-confidence";

describe("DeployConfidence", () => {
  it("renders", () => {
    const { container } = render(
      <DeployConfidence confidenceScore={85} riskLevel="low" deployRecommended={true}
        checks={[
          { check: "tests_passing", weight: 25, passed: true },
          { check: "no_critical_vulns", weight: 20, passed: true },
          { check: "canary_healthy", weight: 15, passed: false },
        ]} />
    );
    expect(container.textContent).toContain("85%");
    expect(container.textContent).toContain("Deploy Confidence");
    expect(container.textContent).toContain("Deploy Recommended");
    expect(container.textContent).toContain("tests passing");
    expect(container.textContent).toContain("25pts");
  });
});
