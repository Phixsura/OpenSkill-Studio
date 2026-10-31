import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUfooterUv2 } from "@/components/platform-footer-v2";

describe("UplatformUfooterUv2", () => {
  it("renders", () => {
    const { container } = render(<UplatformUfooterUv2 label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
