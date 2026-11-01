import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { UserPrefsForm } from "@/components/user-prefs-form";

describe("UserPrefsForm", () => {
  it("renders prefs", () => {
    const { container } = render(
      <UserPrefsForm customized={1} onSet={vi.fn()} onReset={vi.fn()}
        preferences={{ theme: "dark", language: "en", show_tips: true, compact_view: false }} />
    );
    expect(container.textContent).toContain("Preferences");
    expect(container.textContent).toContain("1 customized");
    expect(container.textContent).toContain("theme");
    expect(container.textContent).toContain("dark");
    expect(container.textContent).toContain("show tips");
    expect(container.textContent).toContain("Reset");
  });
});
