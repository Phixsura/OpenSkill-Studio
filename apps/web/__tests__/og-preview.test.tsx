import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OgPreview } from "@/components/og-preview";

describe("OgPreview", () => {
  it("renders social preview", () => {
    const { container } = render(
      <OgPreview title="SuperApp" description="A great productivity app"
        url="https://marketplace.openskill.dev/apps/superapp"
        image={null} siteName="OpenSkill Marketplace" />
    );
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("A great productivity app");
    expect(container.textContent).toContain("OpenSkill Marketplace");
    expect(container.textContent).toContain("Social Preview");
  });
});
