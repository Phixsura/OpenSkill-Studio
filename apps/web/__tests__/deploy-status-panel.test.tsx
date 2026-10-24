import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployStatusPanel } from "@/components/deploy-status-panel";
describe("DeployStatusPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployStatusPanel allSuccess={false} perDay={2.1} successRate={93.3}
        envs={[
          { env: "prod", success: 2, failed: 0, inProgress: 0, total: 2 },
          { env: "staging", success: 0, failed: 1, inProgress: 1, total: 2 },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Status");
    expect(container.textContent).toContain("2.1/day");
    expect(container.textContent).toContain("93.3% success");
    expect(container.textContent).toContain("prod");
    expect(container.textContent).toContain("staging");
  });
});
