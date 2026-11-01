import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-access-log-retention-card";

describe("ConsumerApiAccessLogRetentionCard", () => {
  it("shows stats", () => {
    const stats = { totalEntries: 5000, oldestAgeDays: 45, storageMb: 2.5, dueForDeletion: 100 };
    const { container } = render(<Card stats={stats} retentionDays={90} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Access Log Retention");
    expect(container.textContent).toContain("90d");
    expect(container.textContent).toContain("2.5 MB");
    expect(container.textContent).toContain("100");
  });
  it("shows clean state", () => {
    const stats = { totalEntries: 0, oldestAgeDays: 0, storageMb: 0, dueForDeletion: 0 };
    const { container } = render(<Card stats={stats} retentionDays={30} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("0");
  });
});
