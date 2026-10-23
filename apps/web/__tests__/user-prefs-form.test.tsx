import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UserPrefsForm } from "@/components/user-prefs-form";

describe("UserPrefsForm", () => {
  it("renders prefs", () => {
    const onUpdate = vi.fn();
    const { container, getByText, getAllByRole } = render(
      <UserPrefsForm onUpdate={onUpdate} onReset={vi.fn()}
        prefs={{ theme: "dark", notifications_email: true, code_font_size: 14 }} />
    );
    expect(container.textContent).toContain("Preferences");
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("14");
    const toggles = getAllByRole("button").filter(b => b.className.includes("rounded-full"));
    fireEvent.click(toggles[0]);
    expect(onUpdate).toHaveBeenCalledWith("notifications_email", false);
  });
});
