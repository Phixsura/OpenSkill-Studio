import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppQuickActions } from "@/components/app-quick-actions";

const ACTIONS = [
  { label: "Create App", icon: "➕", href: "/new", description: "Start building" },
  { label: "Docs", icon: "📖", href: "/docs", description: "Read guides" },
];

describe("AppQuickActions", () => {
  it("renders actions", () => {
    const { container } = render(<AppQuickActions actions={ACTIONS} />);
    expect(container.textContent).toContain("Create App");
    expect(container.textContent).toContain("Docs");
  });

  it("shows icons", () => {
    const { container } = render(<AppQuickActions actions={ACTIONS} />);
    expect(container.textContent).toContain("➕");
  });

  it("returns null for empty", () => {
    const { container } = render(<AppQuickActions actions={[]} />);
    expect(container.innerHTML).toBe("");
  });

  it("has links", () => {
    const { container } = render(<AppQuickActions actions={ACTIONS} />);
    expect(container.querySelectorAll("a").length).toBe(2);
  });
});
