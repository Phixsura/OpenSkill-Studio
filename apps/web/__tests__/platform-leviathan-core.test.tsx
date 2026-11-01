import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformLeviathanCore } from "@/components/platform-leviathan-core";
describe("PlatformLeviathanCore", () => { it("renders", () => {
    const { container } = render(<PlatformLeviathanCore />);
    expect(container.textContent).toContain("LEVIATHAN CORE");
    expect(container.textContent).toContain("ZERO");
}); });
