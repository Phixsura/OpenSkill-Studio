import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOrchestra } from "@/components/platform-orchestra";
describe("PlatformOrchestra", () => { it("renders", () => {
    const { container } = render(<PlatformOrchestra />);
    expect(container.textContent).toContain("ORCHESTRA");
    expect(container.textContent).toContain("Strings");
    expect(container.textContent).toContain("Percussion");
}); });
