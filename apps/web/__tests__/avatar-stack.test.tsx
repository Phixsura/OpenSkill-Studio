import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvatarStack } from "@/components/avatar-stack";

describe("AvatarStack", () => {
  const avatars = [
    { name: "Alice", initials: "A", color: "#3b82f6", image: null },
    { name: "Bob Smith", initials: "BS", color: "#ef4444", image: null },
  ];
  it("renders avatars", () => {
    const { container } = render(
      <AvatarStack avatars={avatars} remaining={3} showRemaining={true} remainingLabel="+3" />
    );
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("BS");
    expect(container.textContent).toContain("+3");
  });
  it("no remaining", () => {
    const { container } = render(
      <AvatarStack avatars={avatars} remaining={0} showRemaining={false} remainingLabel="" />
    );
    expect(container.textContent).not.toContain("+");
  });
});
