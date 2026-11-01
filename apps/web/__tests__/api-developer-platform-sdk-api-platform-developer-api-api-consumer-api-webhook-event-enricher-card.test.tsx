import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-webhook-event-enricher-card";

describe("EventEnricherCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", rules: [{ rule_id: "r1", field_name: "env", source: "static" }], enabled: true }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Event Enricher");
    expect(container.textContent).toContain("c1");
    expect(container.textContent).toContain("env");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No enrichment configs");
  });
});
