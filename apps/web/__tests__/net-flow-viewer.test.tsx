import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetFlowViewer } from "@/components/net-flow-viewer";

describe("NetFlowViewer", () => {
  it("renders", () => {
    const { container } = render(
      <NetFlowViewer totalFlows={100} uniquePairs={5} totalBytes={50000}
        topFlows={[
          { src: "web", dst: "api", bytes: 20000, packets: 200 },
          { src: "api", dst: "db", bytes: 15000, packets: 150 },
        ]} />
    );
    expect(container.textContent).toContain("Network Flows");
    expect(container.textContent).toContain("5 pairs");
    expect(container.textContent).toContain("web → api");
    expect(container.textContent).toContain("20,000 B");
  });
});
