import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV44 } from "@/components/platform-v44";
describe("PlatformV44", () => { it("renders", () => {
    const { container } = render(<PlatformV44 />);
    expect(container.textContent).toContain("v44");
    expect(container.textContent).toContain("319K");
}); });
