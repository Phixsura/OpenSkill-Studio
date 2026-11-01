import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformInfinityGauntlet } from "@/components/platform-infinity-gauntlet";
describe("PlatformInfinityGauntlet", () => { it("renders", () => {
    const { container } = render(<PlatformInfinityGauntlet />);
    expect(container.textContent).toContain("INFINITY GAUNTLET");
    expect(container.textContent).toContain("Power");
}); });
