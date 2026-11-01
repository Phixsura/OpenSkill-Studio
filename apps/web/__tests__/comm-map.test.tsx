import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CommMap } from "@/components/comm-map";

describe("CommMap", () => {
  it("renders", () => {
    const { container } = render(
      <CommMap nodes={["api", "db", "cache"]} totalRps={1500}
        byProtocol={{ http: 1, tcp: 2 }}
        edges={[
          { source: "api", destination: "db", protocol: "tcp", rps: 500 },
          { source: "api", destination: "cache", protocol: "tcp", rps: 1000 },
        ]} />
    );
    expect(container.textContent).toContain("Communication Map");
    expect(container.textContent).toContain("3 services");
    expect(container.textContent).toContain("1500 RPS");
    expect(container.textContent).toContain("api → db");
    expect(container.textContent).toContain("tcp: 2");
  });
});
