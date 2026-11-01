import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookPayloadSizeCard from "../src/components/api-webhook-payload-size-card";

const stats = [{ destination: "https://a.com", avg_bytes: 5120, max_bytes: 10240, over_limit_count: 1, delivery_count: 10 }];

describe("APIWebhookPayloadSizeCard", () => {
  it("renders with stats", () => {
    const { container } = render(<APIWebhookPayloadSizeCard stats={stats} maxLimit={1048576} appName="App" />);
    expect(container.textContent).toContain("Payload Size");
    expect(container.textContent).toContain("1 over limit");
    expect(container.textContent).toContain("5.0KB");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookPayloadSizeCard stats={[]} maxLimit={1048576} appName="App" />);
    expect(container.textContent).toContain("No payload data");
  });
});
