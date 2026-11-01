import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployNotifLog } from "@/components/deploy-notif-log";

describe("DeployNotifLog", () => {
  it("renders", () => {
    const { container } = render(
      <DeployNotifLog total={5} notifications={[
        { deploymentId: "d1", version: "3.0", environment: "production", deployer: "alice", deployStatus: "success", channelsNotified: 3 },
        { deploymentId: "d2", version: "3.1", environment: "staging", deployer: "bob", deployStatus: "failed", channelsNotified: 2 },
      ]} />
    );
    expect(container.textContent).toContain("Deploy Notifications");
    expect(container.textContent).toContain("5 notifications");
    expect(container.textContent).toContain("v3.0");
    expect(container.textContent).toContain("production");
    expect(container.textContent).toContain("alice");
    expect(container.textContent).toContain("3 channels");
  });
});
