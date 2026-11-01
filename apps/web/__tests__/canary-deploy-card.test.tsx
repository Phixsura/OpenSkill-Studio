import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import CanaryDeployCard from "../src/components/canary-deploy-card";

const deploys = [
  {
    deploy_id: "d1",
    version: "v2.1.0",
    current_stage: 1,
    status: "in_progress" as const,
    stages: [
      { stage_id: "s1", traffic_pct: 5, duration_seconds: 60, healthy: true },
      { stage_id: "s2", traffic_pct: 25, duration_seconds: 120, healthy: null },
      { stage_id: "s3", traffic_pct: 100, duration_seconds: 300, healthy: null },
    ],
  },
  {
    deploy_id: "d2",
    version: "v2.0.0",
    current_stage: 2,
    status: "completed" as const,
    stages: [
      { stage_id: "s1", traffic_pct: 10, duration_seconds: 60, healthy: true },
      { stage_id: "s2", traffic_pct: 50, duration_seconds: 120, healthy: true },
      { stage_id: "s3", traffic_pct: 100, duration_seconds: 300, healthy: true },
    ],
  },
];

describe("CanaryDeployCard", () => {
  it("renders header and count", () => {
    const { container } = render(<CanaryDeployCard deploys={deploys} appName="My App" />);
    expect(container.textContent).toContain("Canary Deploys");
    expect(container.textContent).toContain("2 deploys");
  });

  it("shows version names", () => {
    const { container } = render(<CanaryDeployCard deploys={deploys} appName="App" />);
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("v2.0.0");
  });

  it("shows status badges", () => {
    const { container } = render(<CanaryDeployCard deploys={deploys} appName="App" />);
    expect(container.textContent).toContain("in progress");
    expect(container.textContent).toContain("completed");
  });

  it("shows traffic percentages", () => {
    const { container } = render(<CanaryDeployCard deploys={deploys} appName="App" />);
    expect(container.textContent).toContain("5%");
    expect(container.textContent).toContain("25%");
    expect(container.textContent).toContain("100%");
  });

  it("shows empty state", () => {
    const { container } = render(<CanaryDeployCard deploys={[]} appName="App" />);
    expect(container.textContent).toContain("No canary deploys");
  });
});
