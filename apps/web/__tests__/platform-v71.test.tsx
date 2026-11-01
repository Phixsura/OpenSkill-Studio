import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV71 } from "@/components/platform-v71";
describe("PlatformV71", () => { it("renders", () => {
    const { container } = render(<PlatformV71 />);
    expect(container.textContent).toContain("v71");
}); });
