import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlannerCard from "../src/components/api-developer-platform-sdk-api-platform-api-consumer-migration-planner-card";

const plans = [{ consumer_id: "acme", from_version: "v1", to_version: "v2", complexity: "medium", status: "in_progress", breaking_changes: 5, estimated_effort_hours: 16 }];

describe("Card", () => {
  it("shows migration plans", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlannerCard plans={plans} blockedCount={1} pendingCount={3} appName="App" />);
    expect(container.textContent).toContain("Migration Planner");
    expect(container.textContent).toContain("3 pending");
    expect(container.textContent).toContain("1 blocked");
    expect(container.textContent).toContain("v1 → v2");
    expect(container.textContent).toContain("medium complexity");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlannerCard plans={[]} blockedCount={0} pendingCount={0} appName="App" />);
    expect(container.textContent).toContain("No migration plans");
  });
});
