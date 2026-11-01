import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV35 } from "@/components/platform-v35";
describe("PlatformV35", () => { it("renders", () => {
    const { container } = render(<PlatformV35 />);
    expect(container.textContent).toContain("v35");
    expect(container.textContent).toContain("316K");
}); });
