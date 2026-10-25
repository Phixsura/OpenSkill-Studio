import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOmega } from "@/components/platform-omega";
describe("PlatformOmega", () => { it("renders", () => {
    const { container } = render(<PlatformOmega />);
    expect(container.textContent).toContain("OMEGA");
    expect(container.textContent).toContain("INFINITE POSSIBILITIES");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
