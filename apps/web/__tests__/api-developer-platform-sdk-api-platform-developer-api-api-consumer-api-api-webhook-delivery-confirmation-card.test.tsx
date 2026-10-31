import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-delivery-confirmation-card";

describe("DeliveryConfirmationCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card confirmationRate={95} pendingCount={5} confirmedCount={950} timeoutCount={50} appName="App" />);
    expect(container.textContent).toContain("Delivery Confirmation");
    expect(container.textContent).toContain("95%");
    expect(container.textContent).toContain("950");
    expect(container.textContent).toContain("50");
  });
  it("shows low rate", () => {
    const { container } = render(<Card confirmationRate={50} pendingCount={0} confirmedCount={50} timeoutCount={50} appName="App" />);
    expect(container.textContent).toContain("50%");
  });
});
