import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformArchon } from "@/components/platform-archon";
describe("PlatformArchon", () => { it("renders", () => {
    const { container } = render(<PlatformArchon />);
    expect(container.textContent).toContain("ARCHON");
    expect(container.textContent).toContain("ZERO");
}); });
