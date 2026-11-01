import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvatarStack } from "@/components/avatar-stack";

describe("AvatarStack", () => {
  const avatars = [
    { name: "Alice", initials: "A", avatar_url: "https://example.com/a.png" },
    { name: "Bob", initials: "B", avatar_url: "https://example.com/b.png" },
  ];
  it("renders avatars", () => {
    const { container } = render(<AvatarStack avatars={avatars} overflowText={null} />);
    const imgs = container.querySelectorAll("img");
    expect(imgs.length).toBe(2);
    expect(imgs[0].getAttribute("alt")).toBe("Alice");
  });
  it("shows overflow", () => {
    const { container } = render(<AvatarStack avatars={avatars} overflowText="+3" />);
    expect(container.textContent).toContain("+3");
  });
});
