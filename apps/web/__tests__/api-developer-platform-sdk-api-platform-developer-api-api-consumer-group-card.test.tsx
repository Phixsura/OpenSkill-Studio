import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-group-card";

describe("ConsumerGroupCard", () => {
  it("shows groups", () => {
    const groups = [{ group_id: "g1", name: "Premium", member_count: 15, max_members: 100, policy_count: 3 }];
    const { container } = render(<Card groups={groups} appName="App" />);
    expect(container.textContent).toContain("Consumer Groups");
    expect(container.textContent).toContain("Premium");
    expect(container.textContent).toContain("15/100 members");
    expect(container.textContent).toContain("3 policies");
  });
  it("shows empty", () => {
    const { container } = render(<Card groups={[]} appName="App" />);
    expect(container.textContent).toContain("No consumer groups");
  });
});
