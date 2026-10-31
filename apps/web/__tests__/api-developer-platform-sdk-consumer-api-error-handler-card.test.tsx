import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ErrorHandlerCard from "../src/components/api-developer-platform-sdk-consumer-api-error-handler-card";

describe("ErrorHandlerCard", () => {
  it("renders title and error codes", () => {
    const { container } = render(<ErrorHandlerCard />);
    expect(container.textContent).toContain("Error Handler");
    expect(container.textContent).toContain("RATE_LIMIT");
    expect(container.textContent).toContain("TIMEOUT");
  });

  it("shows retry badges and alert count", () => {
    const { container } = render(<ErrorHandlerCard />);
    expect(container.textContent).toContain("retry");
    expect(container.textContent).toContain("4 error codes");
    expect(container.textContent).toContain("3 alerts triggered");
  });
});
