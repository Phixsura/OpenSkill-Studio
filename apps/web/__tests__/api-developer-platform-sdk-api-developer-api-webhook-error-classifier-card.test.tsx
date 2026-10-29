import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifierCard from "../src/components/api-developer-platform-sdk-api-developer-api-webhook-error-classifier-card";

const errors = [
  { error_class: "timeout", count: 150, destinations_count: 5 },
  { error_class: "http_5xx", count: 50, destinations_count: 3 },
];

describe("Card", () => {
  it("shows classified errors", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifierCard errors={errors} totalErrors={200} appName="App" />);
    expect(container.textContent).toContain("Error Classifier");
    expect(container.textContent).toContain("200");
    expect(container.textContent).toContain("timeout");
    expect(container.textContent).toContain("150×");
    expect(container.textContent).toContain("5 dest");
  });
  it("shows clean", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifierCard errors={[]} totalErrors={0} appName="App" />);
    expect(container.textContent).toContain("No webhook errors");
  });
});
