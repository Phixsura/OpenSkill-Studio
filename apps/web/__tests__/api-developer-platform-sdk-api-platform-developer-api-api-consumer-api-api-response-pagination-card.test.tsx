import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-response-pagination-card";

describe("ResponsePaginationCard", () => {
  it("shows configs", () => {
    const configs = [{ consumer_id: "c1", default_page_size: 20, max_page_size: 100, style: "offset" }];
    const { container } = render(<Card configs={configs} appName="App" />);
    expect(container.textContent).toContain("Pagination");
    expect(container.textContent).toContain("offset");
    expect(container.textContent).toContain("20/100");
  });
  it("shows empty", () => {
    const { container } = render(<Card configs={[]} appName="App" />);
    expect(container.textContent).toContain("No pagination configs");
  });
});
