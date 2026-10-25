import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformKeystone } from "@/components/platform-keystone";
describe("PlatformKeystone", () => { it("renders", () => {
    const { container } = render(<PlatformKeystone />);
    expect(container.textContent).toContain("KEYSTONE");
    expect(container.textContent).toContain("UNLIMITED");
}); });
