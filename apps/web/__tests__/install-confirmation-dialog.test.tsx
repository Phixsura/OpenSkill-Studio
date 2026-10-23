import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallConfirmationDialog } from "@/components/install-confirmation-dialog";

describe("InstallConfirmationDialog", () => {
  const perms = [{ name: "read:profile", risk: "low" }, { name: "admin:all", risk: "critical" }];
  it("renders", () => {
    const { container } = render(
      <InstallConfirmationDialog appName="Auth SDK" permissions={perms} priceLabel="Free"
        maxRisk="critical" requiresReview={true} confirmMessage="⚠️ Review carefully"
        onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Install Auth SDK");
    expect(container.textContent).toContain("⚠️ Review carefully");
    expect(container.textContent).toContain("read:profile");
    expect(container.textContent).toContain("admin:all");
    expect(container.textContent).toContain("Permissions (2)");
  });
  it("confirm", () => {
    const fn = vi.fn();
    const { container } = render(
      <InstallConfirmationDialog appName="X" permissions={[]} priceLabel="Free"
        maxRisk="low" requiresReview={false} confirmMessage="Install?"
        onConfirm={fn} onCancel={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Install")!);
    expect(fn).toHaveBeenCalled();
  });
});
