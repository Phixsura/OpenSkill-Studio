import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeploymentHistoryList } from "@/components/deployment-history-list";

describe("DeploymentHistoryList", () => {
  const deployments = [
    { deployment_id: "d1", version: "2.0", environment: "production", deployed_by: "alice",
      status: "success", started_at: "2026-10-23T12:00:00", duration_sec: 120 },
    { deployment_id: "d2", version: "1.9", environment: "staging", deployed_by: "bob",
      status: "failed", started_at: "2026-10-22T10:00:00", duration_sec: 30 },
  ];
  it("renders", () => {
    const { container } = render(
      <DeploymentHistoryList deployments={deployments} successRate={50} avgDurationSec={75} />
    );
    expect(container.textContent).toContain("Deployments");
    expect(container.textContent).toContain("50% success");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("❌");
  });
});
