import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmationCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-webhook-delivery-confirmation-card";

describe("Card", () => {
  it("shows confirmation stats", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiWebhookDeliveryConfirmationCard confirmationRate={98.5} avgLatencyMs={75} unconfirmedCount={15} totalDeliveries={10000} appName="App" />);
    expect(container.textContent).toContain("Delivery Confirmation");
    expect(container.textContent).toContain("98.5%");
    expect(container.textContent).toContain("75ms");
    expect(container.textContent).toContain("15 pending");
    expect(container.textContent).toContain("10000");
  });
});
