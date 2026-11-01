import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV41 } from "@/components/platform-v41";
describe("PlatformV41", () => { it("renders", () => {
    const { container } = render(<PlatformV41 />);
    expect(container.textContent).toContain("v41");
    expect(container.textContent).toContain("318K");
}); });
