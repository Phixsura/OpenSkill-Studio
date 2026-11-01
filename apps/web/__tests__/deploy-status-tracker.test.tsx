import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployStatusTracker } from "@/components/deploy-status-tracker";

describe("DeployStatusTracker", () => {
  it("renders tracker", () => {
    const { container } = render(
      <DeployStatusTracker deployId="d1" version="2.0" environment="production"
        status="in_progress" progress={67}
        steps={[
          { name: "build", status: "completed", durationMs: 5000 },
          { name: "test", status: "completed", durationMs: 3000 },
          { name: "deploy", status: "pending", durationMs: 0 },
        ]} />
    );
    expect(container.textContent).toContain("Deploy d1");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("build");
    expect(container.textContent).toContain("5.0s");
  });
});
