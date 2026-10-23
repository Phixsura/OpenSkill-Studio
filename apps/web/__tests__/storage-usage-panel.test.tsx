import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StorageUsagePanel } from "@/components/storage-usage-panel";

describe("StorageUsagePanel", () => {
  const buckets = [
    { name: "uploads", size_gb: 1.0, objects: 500 },
    { name: "backups", size_gb: 0.5, objects: 50 },
  ];
  it("renders", () => {
    const { container } = render(
      <StorageUsagePanel buckets={buckets} totalSizeGb={1.5} totalObjects={550} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Storage");
    expect(container.textContent).toContain("1.5 GB");
    expect(container.textContent).toContain("550");
    expect(container.textContent).toContain("uploads");
    expect(container.textContent).toContain("backups");
  });
});
