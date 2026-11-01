import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GoldenPathPanel } from "@/components/golden-path-panel";
describe("GoldenPathPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GoldenPathPanel goldenPath={["gateway", "api", "db"]}
        actualPath={["gateway", "cache", "api", "db"]}
        followsGolden={false} deviations={1} />
    );
    expect(container.textContent).toContain("Golden Path");
    expect(container.textContent).toContain("1 deviations");
    expect(container.textContent).toContain("gateway → api → db");
    expect(container.textContent).toContain("gateway → cache → api → db");
  });
});
