import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AccessLogCard from "../src/components/api-developer-platform-sdk-consumer-api-access-log-card";

describe("AccessLogCard", () => {
  it("renders title and summary", () => {
    const { container } = render(<AccessLogCard />);
    expect(container.textContent).toContain("Access Log");
    expect(container.textContent).toContain("96%");
    expect(container.textContent).toContain("85ms");
  });

  it("shows error breakdown", () => {
    const { container } = render(<AccessLogCard />);
    expect(container.textContent).toContain("520 client err");
    expect(container.textContent).toContain("100 server err");
  });
});
