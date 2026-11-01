import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SnapshotManagerPanel } from "@/components/snapshot-manager-panel";

const mockSnapshots = [
  { snapshotId: "s1", label: "Before deploy", sizeBytes: 25600, fileCount: 12,
    createdAt: "2024-01-15", createdBy: "admin" },
  { snapshotId: "s2", label: "After deploy", sizeBytes: 28000, fileCount: 14,
    createdAt: "2024-01-16", createdBy: "admin" },
];
const mockDiff = { added: ["/new.js"], removed: ["/old.js"], modified: ["/app.js"], hasChanges: true };

describe("SnapshotManagerPanel", () => {
  it("renders snapshots", () => {
    const { container } = render(
      <SnapshotManagerPanel snapshots={mockSnapshots} diff={null} />
    );
    expect(container.textContent).toContain("Before deploy");
    expect(container.textContent).toContain("12 files");
    expect(container.textContent).toContain("2 saved");
  });

  it("calls onCapture", () => {
    const onCapture = vi.fn();
    const { getByText, getByPlaceholderText } = render(
      <SnapshotManagerPanel snapshots={[]} diff={null} onCapture={onCapture} />
    );
    fireEvent.change(getByPlaceholderText("Snapshot label..."), { target: { value: "test" } });
    fireEvent.click(getByText("Capture"));
    expect(onCapture).toHaveBeenCalledWith("test");
  });

  it("calls onRestore", () => {
    const onRestore = vi.fn();
    const { getAllByText } = render(
      <SnapshotManagerPanel snapshots={mockSnapshots} diff={null} onRestore={onRestore} />
    );
    fireEvent.click(getAllByText("Restore")[0]);
    expect(onRestore).toHaveBeenCalledWith("s1");
  });

  it("shows diff on compare", () => {
    const onCompare = vi.fn();
    const { getByText, container } = render(
      <SnapshotManagerPanel snapshots={mockSnapshots} diff={mockDiff} onCompare={onCompare} />
    );
    fireEvent.click(getByText("Diff"));
    expect(container.textContent).toContain("/new.js");
    expect(container.textContent).toContain("/old.js");
  });
});
