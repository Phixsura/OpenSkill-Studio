import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookTimeoutCard from "../src/components/api-webhook-timeout-card";

const configs = [
  { destination: "https://fast.com", connect_timeout_ms: 3000, read_timeout_ms: 10000, timeout_count: 0 },
  { destination: "https://slow.com", connect_timeout_ms: 5000, read_timeout_ms: 30000, timeout_count: 10 },
];

describe("APIWebhookTimeoutCard", () => {
  it("renders header and frequent count", () => {
    const { container } = render(<APIWebhookTimeoutCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("Webhook Timeouts");
    expect(container.textContent).toContain("1 frequent");
  });

  it("shows timeouts and counts", () => {
    const { container } = render(<APIWebhookTimeoutCard configs={configs} appName="App" />);
    expect(container.textContent).toContain("3000ms");
    expect(container.textContent).toContain("10x");
  });

  it("shows empty state", () => {
    const { container } = render(<APIWebhookTimeoutCard configs={[]} appName="App" />);
    expect(container.textContent).toContain("No timeout configs");
  });
});
