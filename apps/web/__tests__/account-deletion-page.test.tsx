import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AccountDeletionPage } from "@/components/account-deletion-page";

describe("AccountDeletionPage", () => {
  const items = [{ category: "profile", count: 1, label: "Profile" }, { category: "apps", count: 5, label: "Apps" }];
  it("renders deletion page", () => {
    const { container } = render(
      <AccountDeletionPage items={items} totalRecords={6} scheduledDeletion="2026-02-01"
        gracePeriodDays={30} canCancel={true} onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Delete Account");
    expect(container.textContent).toContain("6 records");
    expect(container.textContent).toContain("30-day");
    expect(container.textContent).toContain("Keep Account");
    expect(container.textContent).toContain("Delete Everything");
  });
  it("confirm click", () => {
    const fn = vi.fn();
    const { container } = render(
      <AccountDeletionPage items={items} totalRecords={6} scheduledDeletion="2026-02-01"
        gracePeriodDays={30} canCancel={true} onConfirm={fn} onCancel={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Delete Everything")!);
    expect(fn).toHaveBeenCalled();
  });
});
