import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ApiChlogPanel } from "@/components/api-chlog-panel";
describe("ApiChlogPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ApiChlogPanel version="v2.0" breaking={true} modifiedCount={1}
        addedPaths={["/products"]} removedPaths={["/orders"]} />
    );
    expect(container.textContent).toContain("API Changelog");
    expect(container.textContent).toContain("v2.0");
    expect(container.textContent).toContain("BREAKING");
    expect(container.textContent).toContain("+ /products");
    expect(container.textContent).toContain("- /orders");
    expect(container.textContent).toContain("1 modified");
  });
});
