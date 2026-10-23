import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployLogViewer } from "@/components/deploy-log-viewer";

describe("DeployLogViewer", () => {
  it("renders log", () => {
    const { container } = render(
      <DeployLogViewer overall="success" durationDisplay="25.0s" completed={3} totalSteps={3}
        lines={[
          { step: "Build", status: "success", icon: "✅", durationMs: 5000, output: "Built OK" },
          { step: "Test", status: "success", icon: "✅", durationMs: 12000, output: "" },
          { step: "Deploy", status: "success", icon: "✅", durationMs: 8000, output: "" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy Log");
    expect(container.textContent).toContain("3/3 steps");
    expect(container.textContent).toContain("25.0s");
    expect(container.textContent).toContain("success");
    expect(container.textContent).toContain("Build");
    expect(container.textContent).toContain("Built OK");
  });
});
