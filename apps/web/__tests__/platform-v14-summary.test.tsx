import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV14Summary } from "@/components/platform-v14-summary";
describe("PlatformV14Summary", () => { it("renders", () => {
    const { container } = render(<PlatformV14Summary />);
    expect(container.textContent).toContain("Platform v14.0");
    expect(container.textContent).toContain("ALL SYSTEMS OPERATIONAL");
}); });
