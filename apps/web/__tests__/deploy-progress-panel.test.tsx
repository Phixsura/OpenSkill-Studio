import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployProgressPanel } from "@/components/deploy-progress-panel";
describe("DeployProgressPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployProgressPanel deployId="d1" progressPct={50} status="in_progress"
        steps={[
          { name: "build", status: "completed" },
          { name: "test", status: "completed" },
          { name: "deploy", status: "pending" },
          { name: "verify", status: "pending" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy: d1");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("in_progress");
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("deploy");
  });
});
