import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployDiffRptPanel } from "@/components/deploy-diff-rpt-panel";
describe("DeployDiffRptPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployDiffRptPanel totalChanges={3} added={["new-svc"]} removed={["old-svc"]}
        upgraded={[{ service: "api", from: "1.0", to: "2.0" }]} downgraded={[]} />
    );
    expect(container.textContent).toContain("Deploy Diff");
    expect(container.textContent).toContain("3 changes");
    expect(container.textContent).toContain("+ new-svc");
    expect(container.textContent).toContain("- old-svc");
    expect(container.textContent).toContain("api: 1.0 → 2.0");
  });
});
