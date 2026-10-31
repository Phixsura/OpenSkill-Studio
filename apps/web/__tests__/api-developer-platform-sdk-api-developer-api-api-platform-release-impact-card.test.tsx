import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpactCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-release-impact-card";

const impacts = [{ version: "v3.0", error_delta: 4.9, latency_delta_ms: 155, impact_severity: "high", consumers_affected: 50, rollback_needed: false }];

describe("Card", () => {
  it("shows release impact", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpactCard impacts={impacts} highImpactCount={1} appName="App" />);
    expect(container.textContent).toContain("Release Impact");
    expect(container.textContent).toContain("1 high impact");
    expect(container.textContent).toContain("v3.0");
    expect(container.textContent).toContain("+4.9%");
    expect(container.textContent).toContain("+155ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformReleaseImpactCard impacts={[]} highImpactCount={0} appName="App" />);
    expect(container.textContent).toContain("No release impacts");
  });
});
