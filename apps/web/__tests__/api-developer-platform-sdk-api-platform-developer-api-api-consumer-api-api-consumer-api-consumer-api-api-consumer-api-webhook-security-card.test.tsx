import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-webhook-security-card";

describe("ConsumerApiWebhookSecurityCard", () => {
  it("shows audits", () => {
    const audits = [{ webhookId: "w1", score: 80, issues: ["No IP whitelist"], compliant: false }];
    const { container } = render(<Card audits={audits} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Webhook Security");
    expect(container.textContent).toContain("w1");
    expect(container.textContent).toContain("80/100");
    expect(container.textContent).toContain("No IP whitelist");
  });
  it("shows empty", () => {
    const { container } = render(<Card audits={[]} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No security audits");
  });
});
