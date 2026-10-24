import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV56 } from "@/components/platform-v56";
describe("PlatformV56", () => { it("renders", () => {
    const { container } = render(<PlatformV56 />);
    expect(container.textContent).toContain("v56");
}); });
