import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformStargate } from "@/components/platform-stargate";
describe("PlatformStargate", () => { it("renders", () => {
    const { container } = render(<PlatformStargate />);
    expect(container.textContent).toContain("STARGATE");
    expect(container.textContent).toContain("SDK");
    expect(container.textContent).toContain("Security");
}); });
