import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUheaderUv2 } from "@/components/platform-header-v2";

describe("UplatformUheaderUv2", () => {
  it("renders", () => {
    const { container } = render(<UplatformUheaderUv2 label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
