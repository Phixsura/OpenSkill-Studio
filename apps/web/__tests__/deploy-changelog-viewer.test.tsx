import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployChangelogViewer } from "@/components/deploy-changelog-viewer";

describe("DeployChangelogViewer", () => {
  it("renders", () => {
    const { container } = render(
      <DeployChangelogViewer version="3.1.0" deployer="alice" commitCount={3}
        sections={[
          { type: "feat", label: "Features", items: ["Add dark mode", "OAuth support"] },
          { type: "fix", label: "Bug Fixes", items: ["Login bug"] },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Changelog v3.1.0");
    expect(container.textContent).toContain("3 commits");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("Features");
    expect(container.textContent).toContain("Add dark mode");
    expect(container.textContent).toContain("Bug Fixes");
    expect(container.textContent).toContain("Login bug");
  });
});
