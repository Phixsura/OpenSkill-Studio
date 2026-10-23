import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickDeployPanel } from "@/components/quick-deploy-panel";

describe("QuickDeployPanel", () => {
  const steps = [
    { name: "Build", status: "completed", icon: "🔨" },
    { name: "Test", status: "running", icon: "🧪" },
    { name: "Deploy", status: "pending", icon: "🚀" },
  ];
  it("renders deploy panel", () => {
    const { container } = render(
      <QuickDeployPanel version="2.0.0" environment="production" status="deploying"
        steps={steps} estimatedSeconds={120} onDeploy={vi.fn()} />
    );
    expect(container.textContent).toContain("Quick Deploy");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("Build");
    expect(container.textContent).toContain("Deploying...");
  });
});
