import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUnotificationUbadge } from "@/components/platform-notification-badge";

describe("UplatformUnotificationUbadge", () => {
  it("renders", () => {
    const { container } = render(<UplatformUnotificationUbadge label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
