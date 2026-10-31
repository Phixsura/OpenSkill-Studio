import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployChangelogPanel } from "@/components/deploy-changelog-panel";
describe("DeployChangelogPanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployChangelogPanel totalFeatures={3} totalFixes={5}
        entries={[
          { version: "2.1.0", env: "prod", features: 2, fixes: 1, deployer: "alice" },
          { version: "2.0.1", env: "prod", features: 1, fixes: 4, deployer: "ci" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Changelog");
    expect(container.textContent).toContain("2 deploys");
    expect(container.textContent).toContain("3 features");
    expect(container.textContent).toContain("5 fixes");
    expect(container.textContent).toContain("2.1.0");
    expect(container.textContent).toContain("alice");
  });
});
