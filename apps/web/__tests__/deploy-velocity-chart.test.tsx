import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployVelocityChart } from "@/components/deploy-velocity-chart";

describe("DeployVelocityChart", () => {
  it("renders", () => {
    const { container } = render(
      <DeployVelocityChart total={45} perDay={1.5} successRate={100}
        fastestTeam="platform"
        byTeam={{ platform: 30, frontend: 15 }}
        byEnvironment={{ production: 30, staging: 15 }} />
    );
    expect(container.textContent).toContain("Deploy Velocity");
    expect(container.textContent).toContain("45 deploys");
    expect(container.textContent).toContain("1.5/day");
    expect(container.textContent).toContain("platform");
    expect(container.textContent).toContain("30");
    expect(container.textContent).toContain("production");
  });
});
