import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformObsidian } from "@/components/platform-obsidian";
describe("PlatformObsidian", () => { it("renders", () => {
    const { container } = render(<PlatformObsidian />);
    expect(container.textContent).toContain("OBSIDIAN");
    expect(container.textContent).toContain("Precision");
}); });
