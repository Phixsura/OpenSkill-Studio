import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIConsumerGroupCard from "../src/components/api-consumer-group-card";

const groups = [
  { group_id: "g1", name: "VIP Clients", member_count: 5, rate_limit: 5000 },
  { group_id: "g2", name: "Beta Testers", member_count: 12, rate_limit: 0 },
];

describe("APIConsumerGroupCard", () => {
  it("renders header and totals", () => {
    const { container } = render(<APIConsumerGroupCard groups={groups} appName="App" />);
    expect(container.textContent).toContain("Consumer Groups");
    expect(container.textContent).toContain("2 groups");
    expect(container.textContent).toContain("17 members");
  });

  it("shows names and members", () => {
    const { container } = render(<APIConsumerGroupCard groups={groups} appName="App" />);
    expect(container.textContent).toContain("VIP Clients");
    expect(container.textContent).toContain("5 members");
    expect(container.textContent).toContain("5000/min");
  });

  it("shows empty state", () => {
    const { container } = render(<APIConsumerGroupCard groups={[]} appName="App" />);
    expect(container.textContent).toContain("No consumer groups");
  });
});
