import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BillingMeterCard from "../src/components/api-developer-platform-sdk-consumer-api-billing-meter-card";

describe("BillingMeterCard", () => {
  it("renders title and consumers", () => {
    const { container } = render(<BillingMeterCard />);
    expect(container.textContent).toContain("Billing Meter");
    expect(container.textContent).toContain("c-acme");
    expect(container.textContent).toContain("c-beta");
  });

  it("shows pricing and units", () => {
    const { container } = render(<BillingMeterCard />);
    expect(container.textContent).toContain("$89.99");
    expect(container.textContent).toContain("$29.99");
    expect(container.textContent).toContain("2 consumers billed");
  });
});
