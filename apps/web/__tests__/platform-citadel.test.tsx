import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformCitadel } from "@/components/platform-citadel";
describe("PlatformCitadel", () => { it("renders", () => {
    const { container } = render(<PlatformCitadel />);
    expect(container.textContent).toContain("CITADEL");
    expect(container.textContent).toContain("Walls");
    expect(container.textContent).toContain("0 breaches");
}); });
