import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIWebhookDeadLetterCard from "../src/components/api-webhook-dead-letter-card";

const letters = [
  { letter_id: "dl1", destination: "https://a.com", event_type: "push", last_error: "Connection refused", attempts: 5, retried: false },
  { letter_id: "dl2", destination: "https://b.com", event_type: "issue", last_error: "Timeout", attempts: 3, retried: true },
];

describe("APIWebhookDeadLetterCard", () => {
  it("renders header and pending count", () => {
    const { container } = render(<APIWebhookDeadLetterCard letters={letters} appName="App" />);
    expect(container.textContent).toContain("Dead Letters");
    expect(container.textContent).toContain("1 pending");
  });

  it("shows event type and error", () => {
    const { container } = render(<APIWebhookDeadLetterCard letters={letters} appName="App" />);
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("Connection refused");
    expect(container.textContent).toContain("5 attempts");
  });

  it("shows clean state", () => {
    const { container } = render(<APIWebhookDeadLetterCard letters={[]} appName="App" />);
    expect(container.textContent).toContain("No dead letters");
  });
});
