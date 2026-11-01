import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformArcanum } from "@/components/platform-arcanum";
describe("PlatformArcanum", () => { it("renders", () => {
    const { container } = render(<PlatformArcanum />);
    expect(container.textContent).toContain("ARCANUM");
    expect(container.textContent).toContain("Never stop");
}); });
