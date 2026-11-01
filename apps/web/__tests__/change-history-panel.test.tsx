import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangeHistoryPanel } from "@/components/change-history-panel";

const changes = [
  { changeId: "c1", changeType: "deploy", description: "Deployed v2.0", actor: "admin", timestamp: "5m ago", hasDiff: true },
  { changeId: "c2", changeType: "config", description: "Changed theme", actor: "alice", timestamp: "1h ago", hasDiff: false },
];

describe("ChangeHistoryPanel", () => {
  it("renders changes", () => {
    const { container } = render(<ChangeHistoryPanel changes={changes} changeTypes={["deploy", "config"]} actors={["admin", "alice"]} />);
    expect(container.textContent).toContain("Deployed v2.0");
    expect(container.textContent).toContain("Changed theme");
  });
  it("filters by type", () => {
    const fn = vi.fn();
    const { getByText } = render(<ChangeHistoryPanel changes={changes} changeTypes={["deploy", "config"]} actors={[]} onFilter={fn} />);
    fireEvent.click(getByText("🚀 deploy"));
    expect(fn).toHaveBeenCalledWith("deploy", null);
  });
});
