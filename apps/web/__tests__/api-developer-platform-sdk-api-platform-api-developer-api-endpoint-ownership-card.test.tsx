import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnershipCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-api-endpoint-ownership-card";

const ownership = [{ endpoint: "/api/users", owner_team: "platform", oncall_contact: "oncall@acme.com", sla_tier: "critical" }];

describe("Card", () => {
  it("shows ownership", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnershipCard ownership={ownership} teamDistribution={{ platform: 5, commerce: 3 }} unownedCount={2} appName="App" />);
    expect(container.textContent).toContain("Endpoint Ownership");
    expect(container.textContent).toContain("2 unowned");
    expect(container.textContent).toContain("platform: 5");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("critical");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiEndpointOwnershipCard ownership={[]} teamDistribution={{}} unownedCount={0} appName="App" />);
    expect(container.textContent).toContain("No ownership data");
  });
});
