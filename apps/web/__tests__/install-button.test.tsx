import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallButton } from "@/components/install-button";

describe("InstallButton", () => {
  it("renders install", () => {
    const { container } = render(
      <InstallButton label="Install Free" icon="📥" variant="install" disabled={false}
        onPrimary={vi.fn()} permissionsCount={3} />
    );
    expect(container.textContent).toContain("Install Free");
    expect(container.textContent).toContain("📥");
    expect(container.textContent).toContain("Requires 3 permissions");
  });
  it("renders installed", () => {
    const { container } = render(
      <InstallButton label="Installed ✓" icon="✅" variant="installed" disabled={false}
        secondaryLabel="Uninstall" onPrimary={vi.fn()} onSecondary={vi.fn()} />
    );
    expect(container.textContent).toContain("Installed ✓");
    expect(container.textContent).toContain("Uninstall");
  });
  it("click install", () => {
    const fn = vi.fn();
    const { container } = render(
      <InstallButton label="Install" icon="📥" variant="install" disabled={false} onPrimary={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
