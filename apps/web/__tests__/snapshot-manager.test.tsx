import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SnapshotManager } from "@/components/snapshot-manager";

describe("SnapshotManager", () => {
  it("renders snapshots", () => {
    const snaps = [{ snapshot_id: "snap_1", name: "before-deploy", created_at: "2026-06-01T00:00:00Z", filesystem_files: 5 }];
    const { container } = render(<SnapshotManager snapshots={snaps} onRestore={vi.fn()} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("before-deploy");
    expect(container.textContent).toContain("5 files");
  });
  it("empty state", () => {
    const { container } = render(<SnapshotManager snapshots={[]} onRestore={vi.fn()} onDelete={vi.fn()} />);
    expect(container.textContent).toContain("No snapshots");
  });
  it("calls onRestore", () => {
    const fn = vi.fn();
    const snaps = [{ snapshot_id: "snap_1", name: "x", created_at: "", filesystem_files: 0 }];
    const { container } = render(<SnapshotManager snapshots={snaps} onRestore={fn} onDelete={vi.fn()} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Restore")!;
    fireEvent.click(btn);
    expect(fn).toHaveBeenCalledWith("snap_1");
  });
});
