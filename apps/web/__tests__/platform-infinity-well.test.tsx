import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformInfinityWell } from "@/components/platform-infinity-well";
describe("PlatformInfinityWell", () => { it("renders", () => {
    const { container } = render(<PlatformInfinityWell />);
    expect(container.textContent).toContain("INFINITY WELL");
    expect(container.textContent).toContain("0 denied");
}); });
