import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetentionCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-developer-retention-card";

const cohorts = [{ cohort_month: "2025-01", initial_count: 100, retention_1m: 85, retention_3m: 70, retention_12m: 40, health: "excellent" }];

describe("Card", () => {
  it("shows retention", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetentionCard cohorts={cohorts} avgRetention3m={70} appName="App" />);
    expect(container.textContent).toContain("Developer Retention");
    expect(container.textContent).toContain("70% 3m avg");
    expect(container.textContent).toContain("2025-01");
    expect(container.textContent).toContain("1m: 85%");
    expect(container.textContent).toContain("excellent");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformDeveloperRetentionCard cohorts={[]} avgRetention3m={0} appName="App" />);
    expect(container.textContent).toContain("No retention data");
  });
});
