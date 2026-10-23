import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvatarGroup } from "@/components/avatar-group";

describe("AvatarGroup", () => {
  it("renders avatars", () => {
    const { container } = render(
      <AvatarGroup remaining={2} remainingDisplay="+2" avatars={[
        { initials: "AC", bgColor: "#3B82F6" },
        { initials: "BJ", bgColor: "#10B981" },
        { initials: "CK", bgColor: "#F59E0B" },
      ]} />
    );
    expect(container.textContent).toContain("AC");
    expect(container.textContent).toContain("BJ");
    expect(container.textContent).toContain("CK");
    expect(container.textContent).toContain("+2");
  });
});
