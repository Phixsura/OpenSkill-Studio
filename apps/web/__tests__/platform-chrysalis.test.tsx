import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformChrysalis } from "@/components/platform-chrysalis";
describe("PlatformChrysalis", () => { it("renders", () => {
    const { container } = render(<PlatformChrysalis />);
    expect(container.textContent).toContain("CHRYSALIS");
    expect(container.textContent).toContain("BUTTERFLY");
}); });
