import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppInstallWizard } from "@/components/app-install-wizard";

describe("AppInstallWizard", () => {
  const steps = [
    { id: "review_permissions", label: "Review", status: "current" },
    { id: "configure", label: "Configure", status: "pending" },
  ];
  it("renders", () => {
    const { container } = render(
      <AppInstallWizard appName="Auth SDK" steps={steps}
        permissions={["read:profile"]} onAcceptPermissions={vi.fn()} onComplete={vi.fn()} />
    );
    expect(container.textContent).toContain("Install Auth SDK");
    expect(container.textContent).toContain("Permissions Requested");
    expect(container.textContent).toContain("read:profile");
    expect(container.textContent).toContain("Accept & Continue");
  });
  it("accept", () => {
    const fn = vi.fn();
    const { container } = render(
      <AppInstallWizard appName="X" steps={steps} permissions={["read"]}
        onAcceptPermissions={fn} onComplete={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Accept & Continue")!);
    expect(fn).toHaveBeenCalled();
  });
});
