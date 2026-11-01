import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStatsCard from "../src/components/api-developer-platform-sdk-api-platform-api-api-response-compression-stats-card";

const stats = [{ endpoint: "/api/users", savings_pct: 70, compression_rate: 95, bandwidth_saved_bytes: 7000000, total_responses: 50000 }];

describe("Card", () => {
  it("shows compression stats", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStatsCard stats={stats} totalSavingsBytes={10485760} appName="App" />);
    expect(container.textContent).toContain("Compression Stats");
    expect(container.textContent).toContain("10.0MB saved");
    expect(container.textContent).toContain("70% saved");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiApiResponseCompressionStatsCard stats={[]} totalSavingsBytes={0} appName="App" />);
    expect(container.textContent).toContain("No compression data");
  });
});
