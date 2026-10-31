import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookStatusCard from "../src/components/api-webhook-status-card";

const dests = [
  { destination: "https://a.com", status: "healthy", consecutive_failures: 0 },
  { destination: "https://b.com", status: "down", consecutive_failures: 5 },
];

describe("APIWebhookStatusCard", () => {
  it("renders header and unhealthy count", () => {
    const { container } = render(<APIWebhookStatusCard destinations={dests} appName="App" />);
    expect(container.textContent).toContain("Webhook Status");
    expect(container.textContent).toContain("1 unhealthy");
  });
  it("shows statuses", () => {
    const { container } = render(<APIWebhookStatusCard destinations={dests} appName="App" />);
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("down");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookStatusCard destinations={[]} appName="App" />);
    expect(container.textContent).toContain("No destinations tracked");
  });
});
