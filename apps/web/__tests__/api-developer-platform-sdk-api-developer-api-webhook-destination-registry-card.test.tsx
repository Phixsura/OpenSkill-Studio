import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistryCard from "../src/components/api-developer-platform-sdk-api-developer-api-webhook-destination-registry-card";

const destinations = [{ destination_id: "d1", url: "https://hook.example.com", name: "Production", active: true, total_deliveries: 50000, subscribed_events: ["push", "issue"] }];

describe("Card", () => {
  it("shows destinations", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistryCard destinations={destinations} activeCount={1} appName="App" />);
    expect(container.textContent).toContain("Destination Registry");
    expect(container.textContent).toContain("1/1 active");
    expect(container.textContent).toContain("Production");
    expect(container.textContent).toContain("50,000 deliveries");
    expect(container.textContent).toContain("push");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookDestinationRegistryCard destinations={[]} activeCount={0} appName="App" />);
    expect(container.textContent).toContain("No destinations");
  });
});
