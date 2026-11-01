import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployPipePanel } from "@/components/deploy-pipe-panel";
describe("DeployPipePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployPipePanel success={false} successRate={66.7}
        stages={[
          { stage: "build", status: "passed" },
          { stage: "test", status: "failed" },
          { stage: "deploy", status: "skipped" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Pipeline");
    expect(container.textContent).toContain("Failed");
    expect(container.textContent).toContain("66.7% rate");
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("test");
    expect(container.textContent).toContain("deploy");
  });
});
