import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeploymentPipelineView } from "@/components/deployment-pipeline-view";

describe("DeploymentPipelineView", () => {
  const stages = [
    { name: "build", status: "success" },
    { name: "test", status: "in_progress" },
    { name: "staging", status: "pending" },
    { name: "production", status: "pending" },
  ];
  it("renders", () => {
    const { container } = render(
      <DeploymentPipelineView deploymentId="dep_abc" version="2.0.0" strategy="canary"
        stages={stages} status="in_progress" onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Deployment");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("canary");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⏳");
  });
  it("cancel", () => {
    const fn = vi.fn();
    const { container } = render(
      <DeploymentPipelineView deploymentId="dep_abc" version="2.0.0" strategy="rolling"
        stages={stages} status="in_progress" onCancel={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Cancel Deployment")!);
    expect(fn).toHaveBeenCalled();
  });
});
