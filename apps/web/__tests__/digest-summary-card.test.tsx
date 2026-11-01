import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DigestSummaryCard from "../src/components/digest-summary-card";

const digest = {
  digest_id: "d1",
  period: "daily" as const,
  total_events: 150,
  by_category: { users: 80, orders: 50, system: 20 },
  top_event_types: [
    ["user.signup", 60],
    ["order.created", 40],
    ["user.login", 20],
  ] as [string, number][],
};

const emptyDigest = {
  digest_id: "d2",
  period: "hourly" as const,
  total_events: 0,
  by_category: {},
  top_event_types: [] as [string, number][],
};

describe("DigestSummaryCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<DigestSummaryCard digest={digest} appName="My App" />);
    expect(container.textContent).toContain("Digest");
    expect(container.textContent).toContain("My App");
  });

  it("shows period and event count", () => {
    const { container } = render(<DigestSummaryCard digest={digest} appName="App" />);
    expect(container.textContent).toContain("Daily");
    expect(container.textContent).toContain("150 events");
  });

  it("renders categories with counts", () => {
    const { container } = render(<DigestSummaryCard digest={digest} appName="App" />);
    expect(container.textContent).toContain("users");
    expect(container.textContent).toContain("80");
    expect(container.textContent).toContain("orders");
  });

  it("renders top event types", () => {
    const { container } = render(<DigestSummaryCard digest={digest} appName="App" />);
    expect(container.textContent).toContain("user.signup");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("order.created");
  });

  it("shows empty state", () => {
    const { container } = render(<DigestSummaryCard digest={emptyDigest} appName="App" />);
    expect(container.textContent).toContain("No events in this period");
  });
});
