import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CopyPreview } from "@/components/copy-preview";

describe("CopyPreview", () => {
  const copies = {
    hero: "SuperApp — Build faster. Ship today.",
    cta: "Get started with SuperApp today. Sign up free.",
  };
  it("renders copy variants", () => {
    const { container } = render(<CopyPreview copies={copies} appName="SuperApp" />);
    expect(container.textContent).toContain("SuperApp");
    expect(container.textContent).toContain("Build faster");
    expect(container.textContent).toContain("Sign up free");
    expect(container.textContent).toContain("Hero");
    expect(container.textContent).toContain("CTA");
  });
});
