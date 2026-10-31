import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOasis } from "@/components/platform-oasis";
describe("PlatformOasis", () => { it("renders", () => {
    const { container } = render(<PlatformOasis />);
    expect(container.textContent).toContain("OASIS");
    expect(container.textContent).toContain("INFINITE");
}); });
