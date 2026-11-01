import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployGatePanel } from "@/components/deploy-gate-panel";
describe("DeployGatePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployGatePanel canDeploy={false} passed={1} total={2}
        gates={[
          { name: "tests", passed: true, required: true },
          { name: "security", passed: false, required: true },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Gates");
    expect(container.textContent).toContain("Blocked");
    expect(container.textContent).toContain("1/2");
    expect(container.textContent).toContain("tests");
    expect(container.textContent).toContain("security");
  });
});
