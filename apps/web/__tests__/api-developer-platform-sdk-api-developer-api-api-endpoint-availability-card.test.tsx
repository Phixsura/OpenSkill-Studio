import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiEndpointAvailabilityCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-endpoint-availability-card";

const endpoints = [
  { endpoint: "/api/users", availability_pct: 99.99, nines: "4 nines", current_status: "up" },
  { endpoint: "/api/search", availability_pct: 98.5, nines: "< 2 nines", current_status: "down" },
];

describe("Card", () => {
  it("shows availability", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiEndpointAvailabilityCard endpoints={endpoints} overallAvailability={99.5} belowTargetCount={1} appName="App" />);
    expect(container.textContent).toContain("Availability");
    expect(container.textContent).toContain("99.5%");
    expect(container.textContent).toContain("1 below SLA");
    expect(container.textContent).toContain("4 nines");
    expect(container.textContent).toContain("< 2 nines");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiEndpointAvailabilityCard endpoints={[]} overallAvailability={100} belowTargetCount={0} appName="App" />);
    expect(container.textContent).toContain("No availability data");
  });
});
