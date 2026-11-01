import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiationCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-api-webhook-content-negotiation-card";

const negotiations = [{ consumer_id: "acme", preferred_format: "application/json", negotiations: 5000 }];

describe("Card", () => {
  it("shows negotiations", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiationCard negotiations={negotiations} formatDistribution={{ "application/json": 8, "application/xml": 2 }} appName="App" />);
    expect(container.textContent).toContain("Content Negotiation");
    expect(container.textContent).toContain("json: 8");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("5000 negs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiationCard negotiations={[]} formatDistribution={{}} appName="App" />);
    expect(container.textContent).toContain("No negotiations configured");
  });
});
