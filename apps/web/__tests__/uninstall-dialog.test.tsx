import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UninstallDialog } from "@/components/uninstall-dialog";

describe("UninstallDialog", () => {
  const data = [{ type: "configuration", label: "Configuration", sizeKb: 10 }];
  it("renders dialog", () => {
    const { container } = render(
      <UninstallDialog appName="SuperApp" dataToRemove={data} totalSizeDisplay="10KB"
        warning="All data will be deleted" onConfirm={vi.fn()} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Uninstall SuperApp");
    expect(container.textContent).toContain("Configuration");
    expect(container.textContent).toContain("10KB");
    expect(container.textContent).toContain("Uninstall");
    expect(container.textContent).toContain("Keep App");
  });
  it("confirm click", () => {
    const fn = vi.fn();
    const { container } = render(
      <UninstallDialog appName="X" dataToRemove={[]} totalSizeDisplay="0KB"
        warning="w" onConfirm={fn} onCancel={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Uninstall")!);
    expect(fn).toHaveBeenCalled();
  });
});
