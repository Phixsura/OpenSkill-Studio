import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { VersionManagementLayout } from "@/components/version-management-layout";

describe("VersionManagementLayout", () => {
  it("renders", () => {
    const { container } = render(
      <VersionManagementLayout appName="SuperApp" currentVersion="2.0" stats={{ total: 5, published: 3, in_review: 1 }}
        onCreateVersion={vi.fn()}>
        <p>Version list</p>
      </VersionManagementLayout>
    );
    expect(container.textContent).toContain("SuperApp — Versions");
    expect(container.textContent).toContain("Current: 2.0");
    expect(container.textContent).toContain("5 versions");
    expect(container.textContent).toContain("1 in review");
  });
  it("create version", () => {
    const fn = vi.fn();
    const { container } = render(
      <VersionManagementLayout appName="X" currentVersion={null} stats={{ total: 0, published: 0, in_review: 0 }}
        onCreateVersion={fn}><p>C</p></VersionManagementLayout>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("New"))!);
    expect(fn).toHaveBeenCalled();
  });
});
