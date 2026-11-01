import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployHistoryTimeline } from "@/components/deploy-history-timeline";

describe("DeployHistoryTimeline", () => {
  it("renders and rollback", () => {
    const onRollback = vi.fn();
    const { container, getByText } = render(
      <DeployHistoryTimeline current="1.2.0" onRollback={onRollback} entries={[
        { version: "1.2.0", commit: "ghi789aa", deployer: "alice", status: "active", index: 2 },
        { version: "1.1.0", commit: "def456bb", deployer: "bob", status: "superseded", index: 1 },
      ]} />
    );
    expect(container.textContent).toContain("Deploy History");
    expect(container.textContent).toContain("v1.2.0");
    expect(container.textContent).toContain("Current: 1.2.0");
    fireEvent.click(getByText("Rollback"));
    expect(onRollback).toHaveBeenCalledWith(1);
  });
});
