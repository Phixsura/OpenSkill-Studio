import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeploymentMonitor } from "@/components/deployment-monitor";

describe("DeploymentMonitor", () => {
  const phases = [
    { id: "build", label: "Build", icon: "🔨", status: "completed", statusIcon: "✅" },
    { id: "test", label: "Test", icon: "🧪", status: "running", statusIcon: "⏳" },
    { id: "deploy", label: "Deploy", icon: "🚀", status: "pending", statusIcon: "⬜" },
  ];
  it("renders monitor", () => {
    const { container } = render(
      <DeploymentMonitor appName="SuperApp" version="2.0.0" environment="production"
        phases={phases} progress={33} overall="in_progress" currentPhase="test" />
    );
    expect(container.textContent).toContain("Deploying SuperApp");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("Build");
    expect(container.textContent).toContain("Test");
  });
});
