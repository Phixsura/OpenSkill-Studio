import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ChangeRiskCard } from "@/components/change-risk-card";

describe("ChangeRiskCard", () => {
  it("renders", () => {
    const { container } = render(
      <ChangeRiskCard riskScore={25} riskLevel="low" deployCaution={false}
        factors={[
          { factor: "files_changed", value: 3, threshold: 50, riskContribution: 1.2, high: false },
          { factor: "services_affected", value: 1, threshold: 5, riskContribution: 5, high: false },
        ]} />
    );
    expect(container.textContent).toContain("25");
    expect(container.textContent).toContain("Change Risk Score");
    expect(container.textContent).toContain("low risk");
    expect(container.textContent).toContain("files changed");
    expect(container.textContent).toContain("3/50");
  });
});
