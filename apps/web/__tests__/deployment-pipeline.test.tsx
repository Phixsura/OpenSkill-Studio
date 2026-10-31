import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeploymentPipeline } from "@/components/deployment-pipeline";

describe("DeploymentPipeline", () => {
  const stages = [
    { name: "Build", status: "success", icon: "🔨", duration_s: 30 },
    { name: "Test", status: "success", icon: "🧪", duration_s: 45 },
    { name: "Deploy", status: "running", icon: "🚀", duration_s: 0 },
  ];
  it("renders stages", () => {
    const { container } = render(<DeploymentPipeline stages={stages} overall="running" totalDurationS={75} />);
    expect(container.textContent).toContain("Build");
    expect(container.textContent).toContain("Test");
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("running");
    expect(container.textContent).toContain("75s");
  });
});
