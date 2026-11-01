import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzerCard from "../src/components/api-developer-api-api-developer-api-api-webhook-payload-size-analyzer-card";

const stats = [{ destination: "https://api.example.com", total_payloads: 5000, avg_bytes: 2048, max_bytes: 524288, oversized_count: 3 }];

describe("Card", () => {
  it("shows payload sizes", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzerCard stats={stats} totalBandwidth={10485760} appName="App" />);
    expect(container.textContent).toContain("Payload Sizes");
    expect(container.textContent).toContain("10.0MB total");
    expect(container.textContent).toContain("3 oversized");
    expect(container.textContent).toContain("2.0KB");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzerCard stats={[]} totalBandwidth={0} appName="App" />);
    expect(container.textContent).toContain("No payload data");
  });
});
