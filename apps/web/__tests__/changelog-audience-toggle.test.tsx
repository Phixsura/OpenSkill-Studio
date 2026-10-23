import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChangelogAudienceToggle } from "@/components/changelog-audience-toggle";

describe("ChangelogAudienceToggle", () => {
  it("renders", () => {
    const { container } = render(
      <ChangelogAudienceToggle audience="end_user" onSwitch={vi.fn()} entries={["Dark mode is here!"]} prefix="What's new:" />
    );
    expect(container.textContent).toContain("Dark mode is here!");
    expect(container.textContent).toContain("Users");
  });
  it("switches audience", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChangelogAudienceToggle audience="end_user" onSwitch={fn} entries={[]} prefix="" />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent?.includes("Developers"))!);
    expect(fn).toHaveBeenCalledWith("developer");
  });
});
