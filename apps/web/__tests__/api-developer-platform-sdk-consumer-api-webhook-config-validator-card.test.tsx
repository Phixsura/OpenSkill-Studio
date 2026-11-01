import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-webhook-config-validator-card";

describe("WebhookConfigValidatorCard", () => {
  it("shows valid config", () => {
    const { container } = render(<Card webhookId="w1" valid={true} score={100} issues={[]} appName="App" />);
    expect(container.textContent).toContain("Config Validator");
    expect(container.textContent).toContain("100/100");
    expect(container.textContent).toContain("All checks passed");
  });
  it("shows issues", () => {
    const issues = [{ field: "url", severity: "error", message: "URL must use HTTPS" }, { field: "secret", severity: "warning", message: "No signing secret" }];
    const { container } = render(<Card webhookId="w1" valid={false} score={50} issues={issues} appName="App" />);
    expect(container.textContent).toContain("Invalid");
    expect(container.textContent).toContain("HTTPS");
    expect(container.textContent).toContain("signing secret");
  });
});
