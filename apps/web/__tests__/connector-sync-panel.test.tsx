import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ConnectorSyncPanel } from "@/components/connector-sync-panel";

const mockJobs = [
  { id: "s1", sourceConnector: "Slack", targetConnector: "Jira",
    direction: "source_to_target" as const, status: "completed" as const,
    recordsSynced: 500, recordsFailed: 2, conflicts: 0, lastSyncAt: "2h ago" },
  { id: "s2", sourceConnector: "GitHub", targetConnector: "Linear",
    direction: "bidirectional" as const, status: "conflict" as const,
    recordsSynced: 120, recordsFailed: 0, conflicts: 3 },
];

describe("ConnectorSyncPanel", () => {
  it("renders sync jobs", () => {
    const { container } = render(<ConnectorSyncPanel jobs={mockJobs} />);
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("Jira");
    expect(container.textContent).toContain("620 synced");
  });

  it("shows conflicts", () => {
    const { container } = render(<ConnectorSyncPanel jobs={mockJobs} />);
    expect(container.textContent).toContain("3 conflicts");
  });

  it("calls onSync", () => {
    const onSync = vi.fn();
    const { getByText } = render(<ConnectorSyncPanel jobs={mockJobs} onSync={onSync} />);
    fireEvent.click(getByText("Sync"));
    expect(onSync).toHaveBeenCalledWith("s1");
  });

  it("calls onResolve for conflicts", () => {
    const onResolve = vi.fn();
    const { getByText } = render(<ConnectorSyncPanel jobs={mockJobs} onResolve={onResolve} />);
    fireEvent.click(getByText("Resolve"));
    expect(onResolve).toHaveBeenCalledWith("s2");
  });
});
