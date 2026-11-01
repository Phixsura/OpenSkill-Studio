import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV75 } from "@/components/platform-v75";
describe("PlatformV75", () => { it("renders", () => {
    const { container } = render(<PlatformV75 />);
    expect(container.textContent).toContain("v75");
}); });
