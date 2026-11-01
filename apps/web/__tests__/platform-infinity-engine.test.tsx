import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformInfinityEngine } from "@/components/platform-infinity-engine";
describe("PlatformInfinityEngine", () => { it("renders", () => {
    const { container } = render(<PlatformInfinityEngine />);
    expect(container.textContent).toContain("INFINITY ENGINE");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
