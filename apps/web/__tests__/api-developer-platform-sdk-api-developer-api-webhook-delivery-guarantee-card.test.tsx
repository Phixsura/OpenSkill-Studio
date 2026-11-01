import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuaranteeCard from "../src/components/api-developer-platform-sdk-api-developer-api-webhook-delivery-guarantee-card";

const guarantees = [
  { destination: "https://api.example.com", guarantee_type: "at_least_once", first_try_rate: 95, overall_delivery_rate: 99.95, guarantee_met: true, permanently_failed: 5 },
  { destination: "https://slow.example.com", guarantee_type: "exactly_once", first_try_rate: 80, overall_delivery_rate: 98, guarantee_met: false, permanently_failed: 200 },
];

describe("Card", () => {
  it("shows guarantees", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuaranteeCard guarantees={guarantees} unmetCount={1} appName="App" />);
    expect(container.textContent).toContain("Delivery Guarantees");
    expect(container.textContent).toContain("1 unmet");
    expect(container.textContent).toContain("at least once");
    expect(container.textContent).toContain("MET");
    expect(container.textContent).toContain("UNMET");
    expect(container.textContent).toContain("200 failed");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuaranteeCard guarantees={[]} unmetCount={0} appName="App" />);
    expect(container.textContent).toContain("No delivery guarantees");
  });
});
