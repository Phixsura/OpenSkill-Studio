import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PublishChecklistPanel } from "@/components/publish-checklist-panel";

describe("PublishChecklistPanel", () => {
  const items = [
    { id: "manifest", label: "Valid manifest", category: "required", passed: true, auto_check: true },
    { id: "icon", label: "App icon", category: "required", passed: false, auto_check: true },
    { id: "tests", label: "Tests passing", category: "quality", passed: true, auto_check: true },
  ];
  it("renders", () => {
    const { container } = render(
      <PublishChecklistPanel items={items} canPublish={false} readinessPct={67}
        blocking={["App icon"]} onPublish={vi.fn()} onRunChecks={vi.fn()} />
    );
    expect(container.textContent).toContain("Publish Checklist");
    expect(container.textContent).toContain("67%");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⬜");
    expect(container.textContent).toContain("Fix 1 issues");
  });
});
