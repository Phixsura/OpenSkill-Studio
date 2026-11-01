import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-consumer-api-consumer-webhook-content-filter-card";

describe("WebhookContentFilterCard", () => {
  it("shows rules", () => {
    const rules = [{ id: "r1", field: "status", operator: "equals", value: "active" }];
    const { container } = render(<Card webhookId="w1" rules={rules} matchMode="all" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Content Filter");
    expect(container.textContent).toContain("status");
    expect(container.textContent).toContain("equals");
    expect(container.textContent).toContain("ALL");
  });
  it("shows empty", () => {
    const { container } = render(<Card webhookId="w1" rules={[]} matchMode="any" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No filter rules");
  });
});
