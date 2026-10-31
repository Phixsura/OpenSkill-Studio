import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployHistPanel } from "@/components/deploy-hist-panel";
describe("DeployHistPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployHistPanel successRate={90}
        deploys={[{ version: "2.0", env: "prod", deployer: "alice", status: "success" }]} />
    );
    expect(container.textContent).toContain("Deploy History");
    expect(container.textContent).toContain("2.0");
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("alice");
  });
});
