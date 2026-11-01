import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-abort-controller-card";

describe("RequestAbortControllerCard", () => {
  it("shows stats", () => {
    const { container } = render(<Card inFlightCount={5} abortRate={3.5} totalAborted={35} totalCompleted={965} appName="App" />);
    expect(container.textContent).toContain("Abort Controller");
    expect(container.textContent).toContain("3.5% abort rate");
    expect(container.textContent).toContain("35");
    expect(container.textContent).toContain("965");
  });
  it("shows zero", () => {
    const { container } = render(<Card inFlightCount={0} abortRate={0} totalAborted={0} totalCompleted={0} appName="App" />);
    expect(container.textContent).toContain("0% abort rate");
  });
});
