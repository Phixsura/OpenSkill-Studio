import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUuserUmenu } from "@/components/platform-user-menu";

describe("UplatformUuserUmenu", () => {
  it("renders", () => {
    const { container } = render(<UplatformUuserUmenu label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
