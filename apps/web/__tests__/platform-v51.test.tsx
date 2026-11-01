import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV51 } from "@/components/platform-v51";
describe("PlatformV51", () => { it("renders", () => {
    const { container } = render(<PlatformV51 />);
    expect(container.textContent).toContain("v51");
}); });
