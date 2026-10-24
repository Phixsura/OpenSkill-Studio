import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperProfileEditor } from "@/components/developer-profile-editor";

describe("DeveloperProfileEditor", () => {
  const profile = { display_name: "DevCo", slug: "devco", bio: "Tools", support_email: "help@dev.co", website: "https://dev.co" };
  it("renders form", () => {
    const { container } = render(<DeveloperProfileEditor profile={profile} completeness={75} onSave={vi.fn()} />);
    expect(container.textContent).toContain("Developer Profile");
    expect(container.textContent).toContain("75% complete");
    expect(container.querySelectorAll("input").length).toBe(4);
    expect(container.querySelector("textarea")).toBeTruthy();
  });
  it("saves", () => {
    const fn = vi.fn();
    const { container } = render(<DeveloperProfileEditor profile={profile} completeness={100} onSave={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalledWith(profile);
  });
});
