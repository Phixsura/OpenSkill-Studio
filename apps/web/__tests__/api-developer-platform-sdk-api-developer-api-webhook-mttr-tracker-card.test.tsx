import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTrackerCard from "../src/components/api-developer-platform-sdk-api-developer-api-webhook-mttr-tracker-card";

describe("Card", () => {
  it("shows MTTR", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiWebhookMTTRTrackerCard mttrSeconds={300} openIncidents={2} totalIncidents={15} appName="App" />);
    expect(container.textContent).toContain("Webhook MTTR");
    expect(container.textContent).toContain("5m");
    expect(container.textContent).toContain("2 open");
    expect(container.textContent).toContain("15");
  });
});
