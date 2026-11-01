import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UltimatePlatform } from "@/components/ultimate-platform";
describe("UltimatePlatform", () => { it("renders", () => {
    const { container } = render(<UltimatePlatform />);
    expect(container.textContent).toContain("ULTIMATE PLATFORM");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
