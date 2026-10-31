import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiWebhookCompressionCard from "../src/components/api-developer-api-api-webhook-compression-card";

describe("APIDeveloperAPIApiWebhookCompressionCard", () => {
  it("shows compression stats", () => {
    const { container } = render(<APIDeveloperAPIApiWebhookCompressionCard stats={{ count: 1000, total_original: 5242880, total_compressed: 1048576, avg_savings_pct: 80 }} appName="App" />);
    expect(container.textContent).toContain("Webhook Compression");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("1,000");
    expect(container.textContent).toContain("5.0MB");
    expect(container.textContent).toContain("1.0MB");
  });
});
