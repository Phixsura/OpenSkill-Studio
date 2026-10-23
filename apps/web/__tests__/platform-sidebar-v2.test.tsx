import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUsidebarUv2 } from "@/components/platform-sidebar-v2";

describe("UplatformUsidebarUv2", () => {
  it("renders", () => {
    const { container } = render(<UplatformUsidebarUv2 label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
