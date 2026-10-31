import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitorCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-api-request-rate-monitor-card";

const rates = [{ endpoint: "/api/users", current_rps: 500, avg_rps: 100, peak_rps: 800, load_level: "spike" }];

describe("Card", () => {
  it("shows request rates", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitorCard rates={rates} spikeCount={1} appName="App" />);
    expect(container.textContent).toContain("Request Rate");
    expect(container.textContent).toContain("1 spikes");
    expect(container.textContent).toContain("500 rps");
    expect(container.textContent).toContain("peak: 800");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiRequestRateMonitorCard rates={[]} spikeCount={0} appName="App" />);
    expect(container.textContent).toContain("No rate data");
  });
});
