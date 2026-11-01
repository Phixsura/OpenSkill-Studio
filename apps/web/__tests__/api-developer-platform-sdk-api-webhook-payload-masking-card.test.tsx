import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiWebhookPayloadMaskingCard from "../src/components/api-developer-platform-sdk-api-webhook-payload-masking-card";

const configs = [{ destination: "https://api.example.com", rules: [{ field_pattern: "api_key", mask_char: "*", visible_chars: 4 }], masked_count: 5000 }];

describe("Card", () => {
  it("shows masking configs", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookPayloadMaskingCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("Payload Masking");
    expect(container.textContent).toContain("5,000 masked");
    expect(container.textContent).toContain("api_key");
    expect(container.textContent).toContain("1 rules");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiWebhookPayloadMaskingCard configs={[]} appName="App" />);
    expect(container.textContent).toContain("No masking configs");
  });
});
