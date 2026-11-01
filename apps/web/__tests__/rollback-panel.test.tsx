import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RollbackPanel } from "@/components/rollback-panel";

const mockHistory = [
  { id: "rb1", fromVersion: "2.0.0", toVersion: "1.0.0", reason: "Critical bug",
    status: "completed" as const, initiatedBy: "admin", startedAt: "2024-01-15" },
];

describe("RollbackPanel", () => {
  it("renders current version and targets", () => {
    const { container } = render(
      <RollbackPanel currentVersion="2.0.0" availableVersions={["1.0.0", "1.5.0", "2.0.0"]}
        history={[]} />
    );
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("v1.0.0");
    expect(container.textContent).toContain("v1.5.0");
  });

  it("calls onRollback", () => {
    const onRollback = vi.fn();
    const { getByText } = render(
      <RollbackPanel currentVersion="2.0.0" availableVersions={["1.0.0", "2.0.0"]}
        history={[]} onRollback={onRollback} />
    );
    fireEvent.click(getByText("v1.0.0"));
    expect(onRollback).toHaveBeenCalledWith("1.0.0");
  });

  it("shows history with rollforward", () => {
    const onRollforward = vi.fn();
    const { getByText, container } = render(
      <RollbackPanel currentVersion="1.0.0" availableVersions={["1.0.0"]}
        history={mockHistory} onRollforward={onRollforward} />
    );
    expect(container.textContent).toContain("v2.0.0 → v1.0.0");
    expect(container.textContent).toContain("Critical bug");
    fireEvent.click(getByText("Rollforward"));
    expect(onRollforward).toHaveBeenCalledWith("rb1");
  });
});
