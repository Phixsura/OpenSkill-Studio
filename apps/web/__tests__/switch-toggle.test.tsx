import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SwitchToggle } from "@/components/switch-toggle";

describe("SwitchToggle", () => {
  it("renders", () => {
    const { container } = render(
      <SwitchToggle label="Dark Mode" description="Toggle theme" enabled={true}
        disabled={false} ariaLabel="Toggle Dark Mode" onToggle={vi.fn()} />
    );
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("Toggle theme");
  });
  it("toggles", () => {
    const fn = vi.fn();
    const { container } = render(
      <SwitchToggle label="X" description={null} enabled={false} disabled={false}
        ariaLabel="Toggle X" onToggle={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
  it("disabled", () => {
    const fn = vi.fn();
    const { container } = render(
      <SwitchToggle label="X" description={null} enabled={false} disabled={true}
        ariaLabel="X" onToggle={fn} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(fn).not.toHaveBeenCalled();
  });
});
