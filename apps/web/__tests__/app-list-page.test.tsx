import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppListPage } from "@/components/app-list-page";

describe("AppListPage", () => {
  const apps = [
    { id: "a1", name: "SuperApp", icon: "🚀", version: "2.0.0", status: "active", installs: 5000, rating: 4.5 },
  ];
  it("renders app list", () => {
    const { container } = render(
      <AppListPage apps={apps} total={1} sortBy="newest" hasDraft={false}
        onSort={vi.fn()} onSelect={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("My Apps (1)");
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("+ Create App");
  });
});
