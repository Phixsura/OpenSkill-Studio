import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookDeadLetterQueueCard from "../src/components/api-developer-api-webhook-dead-letter-queue-card";

const letters = [
  { letter_id: "dl1", event_type: "push", destination: "https://a.com/hook", failure_reason: "timeout", retry_count: 3, requeued: false },
  { letter_id: "dl2", event_type: "issue", destination: "https://b.com/hook", failure_reason: "500", retry_count: 5, requeued: true },
];

describe("APIDeveloperAPIWebhookDeadLetterQueueCard", () => {
  it("shows dead letters", () => {
    const { container } = render(<APIDeveloperAPIWebhookDeadLetterQueueCard letters={letters} totalCount={10} byDestination={{ "https://a.com/hook": 5, "https://b.com/hook": 5 }} appName="App" />);
    expect(container.textContent).toContain("Dead Letter Queue");
    expect(container.textContent).toContain("10");
    expect(container.textContent).toContain("push");
    expect(container.textContent).toContain("timeout");
    expect(container.textContent).toContain("requeued");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookDeadLetterQueueCard letters={[]} totalCount={0} byDestination={{}} appName="App" />);
    expect(container.textContent).toContain("Queue empty");
  });
});
