import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SidebarLayout } from "@/components/sidebar-layout";

describe("SidebarLayout", () => {
  const sections = [{ title: "Main", items: [
    { id: "home", label: "Home", icon: "🏠" },
    { id: "apps", label: "My Apps", icon: "📦" },
  ]}];
  it("renders", () => {
    const { container } = render(
      <SidebarLayout sections={sections} collapsed={false} activeItem="home"
        onItemClick={vi.fn()} onToggle={vi.fn()}>
        <p>Content</p>
      </SidebarLayout>
    );
    expect(container.textContent).toContain("Menu");
    expect(container.textContent).toContain("Home");
    expect(container.textContent).toContain("My Apps");
    expect(container.textContent).toContain("Content");
  });
  it("click item", () => {
    const fn = vi.fn();
    const { container } = render(
      <SidebarLayout sections={sections} collapsed={false} activeItem="home"
        onItemClick={fn} onToggle={vi.fn()}>
        <p>X</p>
      </SidebarLayout>
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("My Apps"))!);
    expect(fn).toHaveBeenCalledWith("apps");
  });
});
