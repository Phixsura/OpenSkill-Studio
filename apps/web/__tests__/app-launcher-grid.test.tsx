import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppLauncherGrid } from "@/components/app-launcher-grid";

describe("AppLauncherGrid", () => {
  const apps = [
    { id: "a1", name: "Slack", icon: "💬", url: "#", pinned: true },
    { id: "a2", name: "GitHub", icon: "🐙", url: "#", pinned: false },
  ];
  it("renders pinned and recent", () => {
    const { container } = render(<AppLauncherGrid apps={apps} onLaunch={vi.fn()} onPin={vi.fn()} />);
    expect(container.textContent).toContain("Pinned");
    expect(container.textContent).toContain("Slack");
    expect(container.textContent).toContain("Recent");
    expect(container.textContent).toContain("GitHub");
  });
  it("launch click", () => {
    const fn = vi.fn();
    const { container } = render(<AppLauncherGrid apps={apps} onLaunch={fn} onPin={vi.fn()} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("a1");
  });
});
