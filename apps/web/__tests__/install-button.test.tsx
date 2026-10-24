import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { InstallButton } from "@/components/install-button";

describe("InstallButton", () => {
  it("renders install", () => {
    const { container } = render(
      <InstallButton state="install" label="Install — Free" disabled={false} variant="primary" onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Install — Free");
  });
  it("renders installed", () => {
    const { container } = render(
      <InstallButton state="installed" label="Installed ✓" disabled={true} variant="secondary" onClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Installed");
    expect(container.querySelector("button")?.disabled).toBe(true);
  });
  it("click", () => {
    const fn = vi.fn();
    const { container } = render(
      <InstallButton state="install" label="Install" disabled={false} variant="primary" onClick={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
