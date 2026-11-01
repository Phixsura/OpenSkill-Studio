import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUbreadcrumbUv2 } from "@/components/platform-breadcrumb-v2";

describe("UplatformUbreadcrumbUv2", () => {
  it("renders", () => {
    const { container } = render(<UplatformUbreadcrumbUv2 label="OpenSkill" />);
    expect(container.textContent).toContain("OpenSkill");
  });
});
