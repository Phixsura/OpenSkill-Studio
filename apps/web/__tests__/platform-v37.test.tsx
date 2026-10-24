import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV37 } from "@/components/platform-v37";
describe("PlatformV37", () => { it("renders", () => {
    const { container } = render(<PlatformV37 />);
    expect(container.textContent).toContain("v37");
}); });
