import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeprecationScheduleCard from "../src/components/api-developer-platform-sdk-api-platform-api-deprecation-schedule-card";

const schedules = [{ endpoint: "/api/v1/users", version: "v1", sunset_at: "2025-06-01", replacement: "/api/v2/users", active_consumers: 30, migration_pct: 70, urgency: "high" }];

describe("Card", () => {
  it("shows deprecation schedule", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeprecationScheduleCard schedules={schedules} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("Deprecation Schedule");
    expect(container.textContent).toContain("/api/v1/users");
    expect(container.textContent).toContain("70% migrated");
    expect(container.textContent).toContain("30 remaining");
    expect(container.textContent).toContain("/api/v2/users");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeprecationScheduleCard schedules={[]} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("No deprecation schedules");
  });
});
