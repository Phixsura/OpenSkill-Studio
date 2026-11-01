import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployPipelineBuilder } from "@/components/deploy-pipeline-builder";

describe("DeployPipelineBuilder", () => {
  it("renders pipeline", () => {
    const onApprove = vi.fn();
    const { container, getByText } = render(
      <DeployPipelineBuilder name="Production" progressPct={60} blocked={true}
        onApprove={onApprove} stages={[
          { index: 0, name: "Build", type: "build", environment: "ci", approvalRequired: false, status: "completed" },
          { index: 1, name: "Approval", type: "gate", environment: "staging", approvalRequired: true, status: "awaiting_approval" },
          { index: 2, name: "Deploy", type: "deploy", environment: "production", approvalRequired: false, status: "pending" },
        ]} />
    );
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("60%");
    expect(container.textContent).toContain("Awaiting Approval");
    expect(container.textContent).toContain("Build");
    fireEvent.click(getByText("Approve"));
    expect(onApprove).toHaveBeenCalledWith(1);
  });
});
