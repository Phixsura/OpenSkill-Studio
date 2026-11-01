import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployImpactPanel } from "@/components/deploy-impact-panel";
describe("DeployImpactPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployImpactPanel risk="high" env="production" impactPct={40}
        usersAffected={5000} requireApproval={true}
        servicesAffected={["api", "db"]}
        riskFactors={["database_migration", "production_deployment"]} />
    );
    expect(container.textContent).toContain("HIGH RISK");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("40% blast radius");
    expect(container.textContent).toContain("5,000 users");
    expect(container.textContent).toContain("api, db");
    expect(container.textContent).toContain("database migration");
    expect(container.textContent).toContain("Approval required");
  });
});
