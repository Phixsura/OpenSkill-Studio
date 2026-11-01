import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeploymentPanel } from "@/components/deployment-panel";

const mockDeployments = [
  { deployId: "d1", fromVersion: "1.0", toVersion: "2.0", strategy: "canary" as const,
    status: "in_progress" as const, trafficPercent: 25, healthPassed: true,
    createdAt: "2024-01-15" },
  { deployId: "d2", fromVersion: "0.9", toVersion: "1.0", strategy: "immediate" as const,
    status: "completed" as const, trafficPercent: 100, healthPassed: true,
    createdAt: "2024-01-01" },
];

describe("DeploymentPanel", () => {
  it("renders deployments", () => {
    const { container } = render(
      <DeploymentPanel deployments={mockDeployments} activeVersion="1.0" />
    );
    expect(container.textContent).toContain("v1.0 → v2.0");
    expect(container.textContent).toContain("canary");
    expect(container.textContent).toContain("Active: 1.0");
  });

  it("shows traffic bar for canary", () => {
    const { container } = render(
      <DeploymentPanel deployments={mockDeployments} activeVersion="1.0" />
    );
    expect(container.textContent).toContain("25%");
  });

  it("calls onPromote", () => {
    const onPromote = vi.fn();
    const { getByText } = render(
      <DeploymentPanel deployments={mockDeployments} activeVersion="1.0" onPromote={onPromote} />
    );
    fireEvent.click(getByText("Promote"));
    expect(onPromote).toHaveBeenCalledWith("d1");
  });

  it("shows health status", () => {
    const { container } = render(
      <DeploymentPanel deployments={mockDeployments} activeVersion="1.0" />
    );
    expect(container.textContent).toContain("Healthy");
  });
});
