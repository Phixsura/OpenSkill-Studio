import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import DataRetentionCard from "../src/components/data-retention-card";

const policies = [
  {
    policy_id: "p1",
    data_type: "logs",
    retention_days: 30,
    action: "delete" as const,
    enabled: true,
  },
  {
    policy_id: "p2",
    data_type: "sessions",
    retention_days: 90,
    action: "anonymize" as const,
    enabled: true,
  },
  {
    policy_id: "p3",
    data_type: "backups",
    retention_days: 365,
    action: "archive" as const,
    enabled: false,
  },
];

describe("DataRetentionCard", () => {
  it("renders header and counts", () => {
    const { container } = render(
      <DataRetentionCard policies={policies} pendingPurge={5} appName="App" />,
    );
    expect(container.textContent).toContain("Data Retention");
    expect(container.textContent).toContain("3 policies");
    expect(container.textContent).toContain("5 pending purge");
  });

  it("shows data types and actions", () => {
    const { container } = render(
      <DataRetentionCard policies={policies} pendingPurge={0} appName="App" />,
    );
    expect(container.textContent).toContain("logs");
    expect(container.textContent).toContain("delete");
    expect(container.textContent).toContain("anonymize");
    expect(container.textContent).toContain("archive");
  });

  it("shows retention days", () => {
    const { container } = render(
      <DataRetentionCard policies={policies} pendingPurge={0} appName="App" />,
    );
    expect(container.textContent).toContain("30d");
    expect(container.textContent).toContain("365d");
  });

  it("shows empty state", () => {
    const { container } = render(
      <DataRetentionCard policies={[]} pendingPurge={0} appName="App" />,
    );
    expect(container.textContent).toContain("No retention policies");
  });
});
