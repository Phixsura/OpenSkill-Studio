import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV52 } from "@/components/platform-v52";
describe("PlatformV52", () => { it("renders", () => {
    const { container } = render(<PlatformV52 />);
    expect(container.textContent).toContain("v52");
}); });
