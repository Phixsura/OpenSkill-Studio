import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV28 } from "@/components/platform-v28";
describe("PlatformV28", () => { it("renders", () => {
    const { container } = render(<PlatformV28 />);
    expect(container.textContent).toContain("v28");
}); });
