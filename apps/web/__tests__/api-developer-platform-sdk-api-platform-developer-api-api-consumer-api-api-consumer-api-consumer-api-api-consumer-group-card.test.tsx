import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-group-card";

describe("ConsumerApiConsumerGroupCard", () => {
  it("shows groups", () => {
    const groups = [{ id: "g1", name: "Enterprise", memberCount: 5, policies: { rate_limit: "rl-ent" } }];
    const { container } = render(<Card groups={groups} appName="App" />);
    expect(container.textContent).toContain("Consumer Groups");
    expect(container.textContent).toContain("Enterprise");
    expect(container.textContent).toContain("5 members");
    expect(container.textContent).toContain("rate_limit: rl-ent");
  });
  it("shows empty", () => {
    const { container } = render(<Card groups={[]} appName="App" />);
    expect(container.textContent).toContain("No consumer groups");
  });
});
