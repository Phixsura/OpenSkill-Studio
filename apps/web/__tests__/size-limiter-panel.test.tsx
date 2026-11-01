import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SizeLimiterPanel } from "@/components/size-limiter-panel";
describe("SizeLimiterPanel", () => {
  it("renders", () => {
    const { container } = render(
      <SizeLimiterPanel maxBytes={1048576} humanLimit="1.0MB" accepted={95} rejected={5} total={100} />
    );
    expect(container.textContent).toContain("Size Limiter");
    expect(container.textContent).toContain("max 1.0MB");
    expect(container.textContent).toContain("100 checked");
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("5");
  });
});
