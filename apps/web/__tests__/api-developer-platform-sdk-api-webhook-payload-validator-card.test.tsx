import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiWebhookPayloadValidatorCard from "../src/components/api-developer-platform-sdk-api-webhook-payload-validator-card";

const validations = [{ destination: "https://api.example.com", total_validated: 10000, valid_rate: 99.5, invalid_count: 50, last_error: "" }];

describe("Card", () => {
  it("shows validations", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookPayloadValidatorCard validations={validations} appName="App" />);
    expect(container.textContent).toContain("Payload Validator");
    expect(container.textContent).toContain("50 invalid");
    expect(container.textContent).toContain("99.5% valid");
    expect(container.textContent).toContain("10000 checked");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookPayloadValidatorCard validations={[]} appName="App" />);
    expect(container.textContent).toContain("No validations");
  });
});
