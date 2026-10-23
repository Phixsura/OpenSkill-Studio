import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUversionUbadge } from "@/components/platform-version-badge";

describe("UplatformUversionUbadge", () => {
  it("renders", () => {
    const { container } = render(<UplatformUversionUbadge status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});
