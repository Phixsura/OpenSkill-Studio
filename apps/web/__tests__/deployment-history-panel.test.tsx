import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeploymentHistoryPanel } from "@/components/deployment-history-panel";

const mockDeployments = [
  { id: "d1", version: "2.1.0", environment: "production" as const, status: "success" as const,
    deployedBy: "alice", startedAt: "10m ago", duration: "45s", changes: 12 },
  { id: "d2", version: "2.0.5", environment: "staging" as const, status: "failed" as const,
    deployedBy: "bob", startedAt: "2h ago", duration: "30s", changes: 3 },
  { id: "d3", version: "2.0.4", environment: "canary" as const, status: "success" as const,
    deployedBy: "alice", startedAt: "1d ago", duration: "1m", changes: 8, rollbackOf: "d0" },
];

describe("DeploymentHistoryPanel", () => {
  it("renders deployments with versions and environments", () => {
    const { container } = render(<DeploymentHistoryPanel deployments={mockDeployments} />);
    expect(container.textContent).toContain("Deployment History");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("staging");
    expect(container.textContent).toContain("canary");
  });

  it("shows rollback indicator", () => {
    const { container } = render(<DeploymentHistoryPanel deployments={mockDeployments} />);
    expect(container.textContent).toContain("rollback of d0");
  });

  it("shows rollback button for success", () => {
    const onRollback = vi.fn();
    const { getByText, getAllByText } = render(
      <DeploymentHistoryPanel deployments={mockDeployments} onRollback={onRollback} />
    );
    const btns = getAllByText("↩ Rollback"); fireEvent.click(btns[0]);
    expect(onRollback).toHaveBeenCalledWith("d1");
  });

  it("shows redeploy button for failed", () => {
    const onRedeploy = vi.fn();
    const { getByText, getAllByText } = render(
      <DeploymentHistoryPanel deployments={mockDeployments} onRedeploy={onRedeploy} />
    );
    fireEvent.click(getByText("🔄 Redeploy"));
    expect(onRedeploy).toHaveBeenCalledWith("d2");
  });
});
