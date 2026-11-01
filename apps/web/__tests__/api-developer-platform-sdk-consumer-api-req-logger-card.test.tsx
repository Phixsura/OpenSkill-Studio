import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ReqLoggerCard from "../src/components/api-developer-platform-sdk-consumer-api-req-logger-card";

describe("ReqLoggerCard", () => {
  it("renders title and levels", () => {
    const { container } = render(<ReqLoggerCard />);
    expect(container.textContent).toContain("Request Logger");
    expect(container.textContent).toContain("info");
    expect(container.textContent).toContain("warn");
    expect(container.textContent).toContain("error");
  });

  it("shows stats", () => {
    const { container } = render(<ReqLoggerCard />);
    expect(container.textContent).toContain("45,200 total");
    expect(container.textContent).toContain("1.33% errors");
  });
});
