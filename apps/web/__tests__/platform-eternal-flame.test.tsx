import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformEternalFlame } from "@/components/platform-eternal-flame";
describe("PlatformEternalFlame", () => { it("renders", () => {
    const { container } = render(<PlatformEternalFlame />);
    expect(container.textContent).toContain("ETERNAL FLAME");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
