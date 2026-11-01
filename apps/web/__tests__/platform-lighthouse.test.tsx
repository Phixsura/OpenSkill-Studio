import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformLighthouse } from "@/components/platform-lighthouse";
describe("PlatformLighthouse", () => { it("renders", () => {
    const { container } = render(<PlatformLighthouse />);
    expect(container.textContent).toContain("LIGHTHOUSE");
    expect(container.textContent).toContain("0 groundings");
}); });
