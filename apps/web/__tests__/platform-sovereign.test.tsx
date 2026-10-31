import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSovereign } from "@/components/platform-sovereign";
describe("PlatformSovereign", () => { it("renders", () => {
    const { container } = render(<PlatformSovereign />);
    expect(container.textContent).toContain("SOVEREIGN");
    expect(container.textContent).toContain("ZERO");
}); });
