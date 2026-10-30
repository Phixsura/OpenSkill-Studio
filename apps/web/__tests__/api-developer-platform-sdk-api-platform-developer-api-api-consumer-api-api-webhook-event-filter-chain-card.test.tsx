import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-webhook-event-filter-chain-card";

describe("WebhookEventFilterChainCard", () => {
  it("shows chains", () => {
    const chains = [{ chain_id: "c1", mode: "all", steps: [{ step_id: "s1", filter_type: "event_type", inverted: false }] }];
    const { container } = render(<Card chains={chains} appName="App" />);
    expect(container.textContent).toContain("Filter Chains");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("all");
    expect(container.textContent).toContain("event_type");
  });
  it("shows empty", () => {
    const { container } = render(<Card chains={[]} appName="App" />);
    expect(container.textContent).toContain("No filter chains");
  });
});
