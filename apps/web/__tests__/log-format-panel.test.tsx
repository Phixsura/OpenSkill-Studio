import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogFormatPanel } from "@/components/log-format-panel";
describe("LogFormatPanel", () => {
  it("renders", () => {
    const { container } = render(
      <LogFormatPanel total={1000} byLevel={{ INFO: 800, ERROR: 200 }} byService={{ api: 600, worker: 400 }} />
    );
    expect(container.textContent).toContain("Log Analytics");
    expect(container.textContent).toContain("1,000 logs");
    expect(container.textContent).toContain("INFO");
    expect(container.textContent).toContain("800");
    expect(container.textContent).toContain("api");
    expect(container.textContent).toContain("600");
  });
});
