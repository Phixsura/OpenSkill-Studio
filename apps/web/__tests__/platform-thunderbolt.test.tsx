import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformThunderbolt } from "@/components/platform-thunderbolt";
describe("PlatformThunderbolt", () => { it("renders", () => {
    const { container } = render(<PlatformThunderbolt />);
    expect(container.textContent).toContain("THUNDERBOLT");
    expect(container.textContent).toContain("100% accuracy");
}); });
