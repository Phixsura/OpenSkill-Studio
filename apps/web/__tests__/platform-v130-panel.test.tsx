import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV130Panel } from "@/components/platform-v130-panel";
describe("PlatformV130Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV130Panel />);
    expect(container.textContent).toContain("v130");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
