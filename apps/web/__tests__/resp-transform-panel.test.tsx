import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { RespTransformPanel } from "@/components/resp-transform-panel";
describe("RespTransformPanel", () => {
  it("renders", () => {
    const { container } = render(
      <RespTransformPanel format="standard" page={2} totalPages={3}
        total={50} perPage={20} hasNext={true} />
    );
    expect(container.textContent).toContain("Response Transform");
    expect(container.textContent).toContain("standard");
    expect(container.textContent).toContain("50 items");
    expect(container.textContent).toContain("Page 2/3");
    expect(container.textContent).toContain("Next");
  });
});
