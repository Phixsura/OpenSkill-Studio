import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformMjolnir } from "@/components/platform-mjolnir";
describe("PlatformMjolnir", () => { it("renders", () => {
    const { container } = render(<PlatformMjolnir />);
    expect(container.textContent).toContain("MJOLNIR");
    expect(container.textContent).toContain("Worthy");
}); });
