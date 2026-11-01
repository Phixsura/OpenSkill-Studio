import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvatarDisplay } from "@/components/avatar-display";

describe("AvatarDisplay", () => {
  it("renders initials", () => {
    const { container } = render(
      <AvatarDisplay initials="AD" bgColor="#3b82f6" textColor="#fff" size={48} fontSize={24} />
    );
    expect(container.textContent).toContain("AD");
  });
  it("renders image", () => {
    const { container } = render(
      <AvatarDisplay initials="X" bgColor="#000" textColor="#fff" size={48} fontSize={24}
        imageUrl="https://example.com/avatar.png" />
    );
    expect(container.querySelector("img")).toBeTruthy();
  });
});
