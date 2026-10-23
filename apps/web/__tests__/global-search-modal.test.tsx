import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GlobalSearchModal } from "@/components/global-search-modal";

describe("GlobalSearchModal", () => {
  it("renders results", () => {
    const onSelect = vi.fn();
    const { container, getAllByRole } = render(
      <GlobalSearchModal total={2} onSearch={vi.fn()} onSelect={onSelect}
        results={[
          { title: "User Management", description: "Manage users", type: "page", url: "/users", icon: "👥" },
          { title: "API Keys", description: "Manage keys", type: "settings", url: "/keys", icon: "🔑" },
        ]} />
    );
    expect(container.textContent).toContain("User Management");
    expect(container.textContent).toContain("API Keys");
    const buttons = getAllByRole("button");
    fireEvent.click(buttons[0]);
    expect(onSelect).toHaveBeenCalledWith("/users");
  });
});
