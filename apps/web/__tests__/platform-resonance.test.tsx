import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformResonance } from "@/components/platform-resonance";
describe("PlatformResonance", () => { it("renders", () => {
    const { container } = render(<PlatformResonance />);
    expect(container.textContent).toContain("RESONANCE");
    expect(container.textContent).toContain("INFINITE");
}); });
