import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV60Big60 } from "@/components/platform-v60-big60";
describe("PlatformV60Big60", () => { it("renders", () => {
    const { container } = render(<PlatformV60Big60 />);
    expect(container.textContent).toContain("v60");
    expect(container.textContent).toContain("BIG 60");
    expect(container.textContent).toContain("322K+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
