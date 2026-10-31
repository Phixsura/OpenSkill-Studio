import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployHistoryList } from "@/components/deploy-history-list";

describe("DeployHistoryList", () => {
  it("renders history", () => {
    const { container } = render(
      <DeployHistoryList total={3} successDisplay="67%" deploys={[
        { version: "2.1.0", environment: "production", status: "success", deployer: "alice", timestamp: "5m ago", durationSec: 120 },
        { version: "2.0.4", environment: "production", status: "failed", deployer: "alice", timestamp: "1h ago", durationSec: 45 },
      ]} />
    );
    expect(container.textContent).toContain("Deploy History");
    expect(container.textContent).toContain("3 deploys");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("v2.1.0");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("alice");
  });
});
