import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV45 } from "@/components/platform-v45";
describe("PlatformV45", () => { it("renders", () => {
    const { container } = render(<PlatformV45 />);
    expect(container.textContent).toContain("v45");
    expect(container.textContent).toContain("319K");
}); });
