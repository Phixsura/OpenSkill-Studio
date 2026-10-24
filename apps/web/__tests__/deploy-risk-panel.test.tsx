import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployRiskPanel } from "@/components/deploy-risk-panel";
describe("DeployRiskPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployRiskPanel score={45} level="high" deployName="v2.1.0"
        factors={["production", "db_migration", "multi_service"]} />
    );
    expect(container.textContent).toContain("45/100");
    expect(container.textContent).toContain("HIGH RISK");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("db migration");
  });
});
