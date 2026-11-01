import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ResponseFormatterCard from "../src/components/api-developer-platform-sdk-consumer-api-response-formatter-card";

describe("ResponseFormatterCard", () => {
  it("renders title and formats", () => {
    const { container } = render(<ResponseFormatterCard />);
    expect(container.textContent).toContain("Response Formatter");
    expect(container.textContent).toContain("json");
    expect(container.textContent).toContain("csv");
    expect(container.textContent).toContain("xml");
  });

  it("shows default and total", () => {
    const { container } = render(<ResponseFormatterCard />);
    expect(container.textContent).toContain("Default: json");
    expect(container.textContent).toContain("13,555 total formatted");
  });
});
