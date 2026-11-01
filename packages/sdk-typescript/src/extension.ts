/**
 * OpenSkill Extension SDK — runs inside sandboxed iframe UI extensions.
 *
 * Provides postMessage-based communication with the host platform:
 * - API calls (scoped to granted permissions)
 * - UI controls (resize, navigate, toast)
 * - Context events (org, user, surface, entity)
 *
 * @example
 * ```ts
 * import { OpenSkillExtension } from '@openskill/sdk/extension';
 *
 * const ext = new OpenSkillExtension();
 *
 * ext.on('context_changed', (ctx) => {
 *   console.log('Org:', ctx.orgId, 'Surface:', ctx.surface);
 * });
 *
 * const cohorts = await ext.api.get('/cohorts', { limit: 10 });
 * ext.ui.toast({ message: 'Loaded!', type: 'success' });
 * ```
 */

// ── Types ───────────────────────────────────────────────

export interface ExtensionContext {
  orgId: string;
  userId: string;
  surface: string;
  entityId?: string;
  entityType?: string;
  installationId: string;
  permissions: string[];
}

export interface ToastOptions {
  message: string;
  type?: "success" | "error" | "info" | "warning";
  duration?: number;
}

interface MessagePayload {
  type: string;
  id: string;
  [key: string]: unknown;
}

interface PendingRequest {
  resolve: (value: unknown) => void;
  reject: (reason: unknown) => void;
  timer: ReturnType<typeof setTimeout>;
}

// ── Extension class ─────────────────────────────────────

export class OpenSkillExtension {
  private readonly _origin: string;
  private readonly _listeners: Map<string, Array<(data: unknown) => void>> = new Map();
  private readonly _pending: Map<string, PendingRequest> = new Map();
  private readonly _boundHandler: (event: MessageEvent) => void;
  private _context: ExtensionContext | null = null;
  private _requestId = 0;
  private _ready = false;

  /** API proxy — make scoped platform API calls */
  readonly api: ExtensionApi;
  /** UI controls — resize, navigate, toast */
  readonly ui: ExtensionUi;

  constructor(options: { origin: string; timeout?: number }) {
    if (!options.origin || options.origin === "*") {
      throw new Error("origin is required and must not be '*'");
    }
    this._origin = options.origin;
    const timeout = options.timeout ?? 10_000;

    this.api = new ExtensionApi(this, timeout);
    this.ui = new ExtensionUi(this);

    // Bind handler for proper cleanup in destroy()
    this._boundHandler = this._handleMessage.bind(this);

    // Listen for messages from host
    if (typeof window !== "undefined") {
      window.addEventListener("message", this._boundHandler);
      // Signal ready
      this._postToHost({ type: "extension:ready" });
    }
  }

  /** Current context (populated after host sends context_changed) */
  get context(): ExtensionContext | null {
    return this._context;
  }

  /** Whether the extension has received its initial context */
  get isReady(): boolean {
    return this._ready;
  }

  /** Register an event listener */
  on(event: string, handler: (data: unknown) => void): () => void {
    const handlers = this._listeners.get(event) ?? [];
    handlers.push(handler);
    this._listeners.set(event, handlers);
    // Return unsubscribe function
    return () => {
      const list = this._listeners.get(event);
      if (list) {
        const idx = list.indexOf(handler);
        if (idx !== -1) list.splice(idx, 1);
      }
    };
  }

  /** Send a request to the host and wait for response */
  _sendRequest(type: string, payload: Record<string, unknown> = {}, timeoutMs = 10_000): Promise<unknown> {
    return new Promise((resolve, reject) => {
      const id = `req_${++this._requestId}`;
      const timer = setTimeout(() => {
        this._pending.delete(id);
        reject(new Error(`Request ${type} timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      this._pending.set(id, { resolve, reject, timer });
      this._postToHost({ type, id, ...payload });
    });
  }

  /** Post a message to the host window */
  _postToHost(data: Record<string, unknown>): void {
    if (typeof window !== "undefined" && window.parent !== window) {
      window.parent.postMessage(
        { source: "openskill-extension", ...data },
        this._origin,
      );
    }
  }

  private _handleMessage(event: MessageEvent): void {
    // Validate origin and source
    if (event.origin !== this._origin || event.source !== window.parent) return;

    const data = event.data as MessagePayload;
    if (!data || typeof data !== "object") return;

    // Handle response to a pending request
    if (data.id && this._pending.has(data.id)) {
      const pending = this._pending.get(data.id)!;
      this._pending.delete(data.id);
      clearTimeout(pending.timer);

      if (data.type === "error") {
        pending.reject(new Error(String(data.message ?? "Unknown error")));
      } else {
        pending.resolve(data.result ?? data);
      }
      return;
    }

    // Handle host events
    if (data.type === "context_changed") {
      this._context = data.context as ExtensionContext;
      this._ready = true;
      this._emit("context_changed", this._context);
    } else if (data.type === "event") {
      this._emit(String(data.eventType ?? "unknown"), data.payload);
    }
  }

  private _emit(event: string, data: unknown): void {
    const handlers = this._listeners.get(event);
    if (handlers) {
      for (const h of handlers) {
        try {
          h(data);
        } catch {
          // Don't let listener errors break the event loop
        }
      }
    }
  }

  /** Clean up listeners */
  destroy(): void {
    if (typeof window !== "undefined") {
      window.removeEventListener("message", this._boundHandler);
    }
    for (const [, pending] of this._pending) {
      clearTimeout(pending.timer);
      pending.reject(new Error("Extension destroyed"));
    }
    this._pending.clear();
    this._listeners.clear();
  }
}

// ── API proxy ───────────────────────────────────────────

class ExtensionApi {
  constructor(
    private ext: OpenSkillExtension,
    private timeout: number,
  ) {}

  /** GET request via host API proxy */
  async get<T = unknown>(path: string, query?: Record<string, unknown>): Promise<T> {
    return (await this.ext._sendRequest(
      "api_call",
      { method: "GET", path, query },
      this.timeout,
    )) as T;
  }

  /** POST request via host API proxy */
  async post<T = unknown>(path: string, body?: unknown): Promise<T> {
    return (await this.ext._sendRequest(
      "api_call",
      { method: "POST", path, body },
      this.timeout,
    )) as T;
  }

  /** PATCH request via host API proxy */
  async patch<T = unknown>(path: string, body?: unknown): Promise<T> {
    return (await this.ext._sendRequest(
      "api_call",
      { method: "PATCH", path, body },
      this.timeout,
    )) as T;
  }

  /** DELETE request via host API proxy */
  async delete<T = unknown>(path: string): Promise<T> {
    return (await this.ext._sendRequest(
      "api_call",
      { method: "DELETE", path },
      this.timeout,
    )) as T;
  }
}

// ── UI controls ─────────────────────────────────────────

class ExtensionUi {
  constructor(private ext: OpenSkillExtension) {}

  /** Resize the extension iframe */
  resize(dimensions: { width?: number; height?: number }): void {
    this.ext._postToHost({ type: "ui:resize", ...dimensions });
  }

  /** Navigate the host to a platform page */
  navigate(path: string): void {
    this.ext._postToHost({ type: "ui:navigate", path });
  }

  /** Show a toast notification in the host */
  toast(options: ToastOptions): void {
    this.ext._postToHost({ type: "ui:toast", ...options });
  }

  /** Open a modal in the host */
  openModal(options: { title: string; url: string; width?: number; height?: number }): void {
    this.ext._postToHost({ type: "ui:open_modal", ...options });
  }

  /** Close the current extension panel */
  close(): void {
    this.ext._postToHost({ type: "ui:close" });
  }
}
