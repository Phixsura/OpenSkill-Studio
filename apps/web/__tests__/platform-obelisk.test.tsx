import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformObelisk } from "@/components/platform-obelisk";
describe("PlatformObelisk", () => { it("renders", () => {
    const { container } = render(<PlatformObelisk />);
    expect(container.textContent).toContain("OBELISK");
    expect(container.textContent).toContain("DORA Elite");
}); });
