import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployPage } from "@/components/deploy-page";

describe("DeployPage", () => {
  const envs = [
    { environment: "development", currentVersion: null, deployed: false, icon: "🟢" },
    { environment: "production", currentVersion: "2.0.0", deployed: true, icon: "🔴" },
  ];
  it("renders deploy page", () => {
    const { container } = render(
      <DeployPage appName="SuperApp" environments={envs}
        availableVersions={["2.1.0", "2.0.0"]} onDeploy={vi.fn()} />
    );
    expect(container.textContent).toContain("Deploy SuperApp");
    expect(container.textContent).toContain("development");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Not deployed");
  });
});
