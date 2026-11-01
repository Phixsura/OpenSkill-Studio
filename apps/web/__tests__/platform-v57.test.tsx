import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV57 } from "@/components/platform-v57";
describe("PlatformV57", () => { it("renders", () => {
    const { container } = render(<PlatformV57 />);
    expect(container.textContent).toContain("v57");
}); });
