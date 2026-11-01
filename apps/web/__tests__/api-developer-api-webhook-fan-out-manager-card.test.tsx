import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIWebhookFanOutManagerCard from "../src/components/api-developer-api-webhook-fan-out-manager-card";

const targets = [
  { target_id: "t1", destination: "https://a.com/hook", event_types: ["push", "issue"], enabled: true, delivery_count: 500, failure_count: 3 },
  { target_id: "t2", destination: "https://b.com/hook", event_types: ["push"], enabled: false, delivery_count: 100, failure_count: 0 },
];

describe("APIDeveloperAPIWebhookFanOutManagerCard", () => {
  it("shows targets", () => {
    const { container } = render(<APIDeveloperAPIWebhookFanOutManagerCard targets={targets} appName="App" />);
    expect(container.textContent).toContain("Fan-Out Manager");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("https://a.com/hook");
    expect(container.textContent).toContain("500 sent");
    expect(container.textContent).toContain("3 failures");
    expect(container.textContent).toContain("push");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIWebhookFanOutManagerCard targets={[]} appName="App" />);
    expect(container.textContent).toContain("No fan-out targets");
  });
});
