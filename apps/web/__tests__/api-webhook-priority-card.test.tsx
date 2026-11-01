import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookPriorityCard from "../src/components/api-webhook-priority-card";

const priorities = [
  { event_type: "security.alert", priority: 5, delivery_count: 10 },
  { event_type: "user.created", priority: 2, delivery_count: 100 },
];

describe("APIWebhookPriorityCard", () => {
  it("renders events with priorities", () => {
    const { container } = render(<APIWebhookPriorityCard priorities={priorities} appName="App" />);
    expect(container.textContent).toContain("Webhook Priority");
    expect(container.textContent).toContain("security.alert");
    expect(container.textContent).toContain("Critical");
    expect(container.textContent).toContain("Normal");
  });
  it("shows empty", () => {
    const { container } = render(<APIWebhookPriorityCard priorities={[]} appName="App" />);
    expect(container.textContent).toContain("No priorities configured");
  });
});
