import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-backoff-card";

describe("WebhookBackoffCard", () => {
  it("shows backoff states", () => {
    const states = [{ consumer_id: "c1", endpoint: "/hook", attempt: 3, current_delay_s: 8, max_delay_s: 3600 }];
    const { container } = render(<Card states={states} backedOffCount={1} appName="App" />);
    expect(container.textContent).toContain("Webhook Backoff");
    expect(container.textContent).toContain("1 backing off");
    expect(container.textContent).toContain("8s");
    expect(container.textContent).toContain("attempt 3");
  });
  it("shows empty", () => {
    const { container } = render(<Card states={[]} backedOffCount={0} appName="App" />);
    expect(container.textContent).toContain("No backoff states");
  });
});
