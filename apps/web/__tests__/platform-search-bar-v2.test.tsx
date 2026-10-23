import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUsearchUbarUv2 } from "@/components/platform-search-bar-v2";

describe("UplatformUsearchUbarUv2", () => {
  it("renders", () => {
    const { container } = render(<UplatformUsearchUbarUv2 label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
