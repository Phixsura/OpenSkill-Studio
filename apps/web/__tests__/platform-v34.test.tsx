import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV34 } from "@/components/platform-v34";
describe("PlatformV34", () => { it("renders", () => {
    const { container } = render(<PlatformV34 />);
    expect(container.textContent).toContain("v34");
}); });
