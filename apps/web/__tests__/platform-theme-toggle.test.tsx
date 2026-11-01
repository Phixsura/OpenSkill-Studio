import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUthemeUtoggle } from "@/components/platform-theme-toggle";

describe("UplatformUthemeUtoggle", () => {
  it("renders", () => {
    const { container } = render(<UplatformUthemeUtoggle label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
