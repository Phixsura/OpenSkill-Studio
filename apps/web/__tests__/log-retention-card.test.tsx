import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LogRetentionCard from "../src/components/log-retention-card";

const policies = [
  {
    policy_id: "p1",
    log_type: "access",
    retention_days: 30,
    max_size_mb: 500,
    current_size_mb: 450,
    entry_count: 500000,
    needs_cleanup: false,
  },
  {
    policy_id: "p2",
    log_type: "error",
    retention_days: 90,
    max_size_mb: 100,
    current_size_mb: 120,
    entry_count: 25000,
    needs_cleanup: true,
  },
];

describe("LogRetentionCard", () => {
  it("renders header and app name", () => {
    const { container } = render(
      <LogRetentionCard policies={policies} totalSizeMb={570} appName="My App" />,
    );
    expect(container.textContent).toContain("Log Retention");
    expect(container.textContent).toContain("My App");
  });

  it("shows total size", () => {
    const { container } = render(
      <LogRetentionCard policies={policies} totalSizeMb={570} appName="App" />,
    );
    expect(container.textContent).toContain("570 MB total");
  });

  it("shows cleanup badge", () => {
    const { container } = render(
      <LogRetentionCard policies={policies} totalSizeMb={0} appName="App" />,
    );
    expect(container.textContent).toContain("1 need cleanup");
  });

  it("renders log types and retention", () => {
    const { container } = render(
      <LogRetentionCard policies={policies} totalSizeMb={0} appName="App" />,
    );
    expect(container.textContent).toContain("access");
    expect(container.textContent).toContain("30d retention");
  });

  it("shows entry counts", () => {
    const { container } = render(
      <LogRetentionCard policies={policies} totalSizeMb={0} appName="App" />,
    );
    expect(container.textContent).toContain("500.0K entries");
  });

  it("shows empty state", () => {
    const { container } = render(<LogRetentionCard policies={[]} totalSizeMb={0} appName="App" />);
    expect(container.textContent).toContain("No retention policies");
  });
});
