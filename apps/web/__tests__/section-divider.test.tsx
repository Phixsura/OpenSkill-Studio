import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SectionDivider } from "@/components/section-divider";

describe("SectionDivider", () => {
  it("renders plain", () => {
    const { container } = render(
      <SectionDivider label={null} variantClass="border-t" spacingClass="my-4" />
    );
    expect(container.querySelector("div")).toBeTruthy();
    expect(container.textContent).toBe("");
  });
  it("renders with label", () => {
    const { container } = render(
      <SectionDivider label="Or continue with" variantClass="border-t" spacingClass="my-4" />
    );
    expect(container.textContent).toContain("Or continue with");
  });
});
