import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV49 } from "@/components/platform-v49";
describe("PlatformV49", () => { it("renders", () => {
    const { container } = render(<PlatformV49 />);
    expect(container.textContent).toContain("v49");
}); });
