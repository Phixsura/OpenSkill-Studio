import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformLegacyMonument } from "@/components/platform-legacy-monument";
describe("PlatformLegacyMonument", () => { it("renders", () => {
    const { container } = render(<PlatformLegacyMonument />);
    expect(container.textContent).toContain("LEGACY MONUMENT");
    expect(container.textContent).toContain("FOREVER LEGENDARY");
}); });
