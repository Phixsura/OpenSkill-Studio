import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployEnvManager } from "@/components/deploy-env-manager";

describe("DeployEnvManager", () => {
  it("renders envs", () => {
    const { container } = render(
      <DeployEnvManager inSync={false} onDeploy={vi.fn()} environments={[
        { name: "development", tier: "dev", autoDeploy: true, approvalRequired: false, version: "2.1" },
        { name: "staging", tier: "non-prod", autoDeploy: true, approvalRequired: false, version: "2.0" },
        { name: "production", tier: "prod", autoDeploy: false, approvalRequired: true, version: "2.0" },
      ]} />
    );
    expect(container.textContent).toContain("Environments");
    expect(container.textContent).toContain("Out of Sync");
    expect(container.textContent).toContain("development");
    expect(container.textContent).toContain("v2.1");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("prod");
  });
});
