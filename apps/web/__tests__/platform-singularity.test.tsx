import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSingularity } from "@/components/platform-singularity";
describe("PlatformSingularity", () => { it("renders", () => {
    const { container } = render(<PlatformSingularity />);
    expect(container.textContent).toContain("SINGULARITY");
    expect(container.textContent).toContain("TRANSCENDENT");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
