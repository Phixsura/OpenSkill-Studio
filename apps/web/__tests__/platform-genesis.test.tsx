import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformGenesis } from "@/components/platform-genesis";
describe("PlatformGenesis", () => { it("renders", () => {
    const { container } = render(<PlatformGenesis />);
    expect(container.textContent).toContain("GENESIS");
    expect(container.textContent).toContain("ETERNAL CREATION");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
