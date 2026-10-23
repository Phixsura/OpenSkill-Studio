import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionsPage } from "@/components/versions-page";

describe("VersionsPage", () => {
  const versions = [
    { version: "2.0.0", publishedAt: "2026-03-01", author: "Bob", downloads: 2000, changeCount: 15, isCurrent: true, isPrerelease: false, canRollback: false },
    { version: "1.0.0", publishedAt: "2026-01-01", author: "Alice", downloads: 5000, changeCount: 10, isCurrent: false, isPrerelease: false, canRollback: true },
  ];
  it("renders versions", () => {
    const { container } = render(
      <VersionsPage appName="SuperApp" versions={versions} current="2.0.0"
        totalDownloads={7000} onRollback={vi.fn()} onPublish={vi.fn()} />
    );
    expect(container.textContent).toContain("SuperApp Versions");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Current");
    expect(container.textContent).toContain("Rollback");
    expect(container.textContent).toContain("7,000");
    expect(container.textContent).toContain("+ New Version");
  });
});
