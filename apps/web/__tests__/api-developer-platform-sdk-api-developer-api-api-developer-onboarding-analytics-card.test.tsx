import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalyticsCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-developer-onboarding-analytics-card";

const analytics = { total_started: 500, total_completed: 400, completion_rate: 80, avg_time_to_first_call_hours: 2.5, drop_off_step: "webhook_setup", quality: "excellent" };

describe("Card", () => {
  it("shows onboarding analytics", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiDeveloperOnboardingAnalyticsCard analytics={analytics} appName="App" />);
    expect(container.textContent).toContain("Onboarding Analytics");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("400");
    expect(container.textContent).toContain("2.5h");
    expect(container.textContent).toContain("webhook_setup");
  });
});
