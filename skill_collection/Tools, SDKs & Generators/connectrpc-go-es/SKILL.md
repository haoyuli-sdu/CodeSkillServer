---
name: "connectrpc-go-es"
description: "Build proto-first RPC with a connect-go server and a Connect-ES (TypeScript) client. Use when working with connectrpc, connect-go, connect-es, @connectrpc/connect, @connectrpc/connect-web, protoc-gen-connect-go, protoc-gen-es, buf generate / buf lint / buf breaking, protovalidate, Connect protocol vs gRPC vs gRPC-Web, h2c, RPC CORS, Connect error codes, or TanStack Query via connect-query. Covers the current simple-mode Go codegen and Connect-ES v2 APIs."
---

# ConnectRPC: Go server + Connect-ES client

Schema-first RPC. One `.proto` set is the contract; `buf` generates a Go handler
interface and a TypeScript client. Assume **Go server + ES client** unless the
user says otherwise.

## Non-negotiable defaults

| Decision | Default | Reason |
|---|---|---|
| Protocol | **Connect** | Works over HTTP/1.1, JSON-readable in devtools, no proxy needed. |
| Schema tooling | **Buf v2** (`buf.yaml` + `buf.gen.yaml`, both `version: v2`) | `buf.work.yaml` is dead. |
| Go codegen | `protoc-gen-connect-go` with the **`simple`** option | Handlers take `*Req` and return `*Res` — no `connect.Request`/`connect.Response` wrappers. |
| Go plugin pinning | `go get -tool` + `local: [go, tool, protoc-gen-go]` | Plugin versions live in `go.mod`, so codegen is reproducible. |
| Go h2c | `http.Protocols` + `SetUnencryptedHTTP2(true)` (Go 1.24+) | Replaces `golang.org/x/net/http2/h2c`. |
| Validation | **protovalidate** — rules in the schema + `validate.NewInterceptor()` | One source of truth; no hand-written validation. |
| TS codegen | **`protoc-gen-es` only** | Connect-ES v2 needs no Connect-specific plugin. Services come from `*_pb.ts`. |
| TS client | `createClient(Service, transport)` from `@connectrpc/connect` | `createPromiseClient` is v1 and gone. |
| TS wire format | JSON (`useBinaryFormat: false`, the default) | Readable in the network inspector. Switch to binary only for measured payload wins. |
| Streaming | Unary first. Server streaming if you must. | Streaming binds you to proxy/HTTP2 behaviour and kills curl-based debugging. |

Reach for **gRPC-Web** (`createGrpcWebTransport`) only to talk to a backend that
does not speak Connect. Reach for **gRPC** (`connect.WithGRPC()` on Go clients)
only for interop with an existing gRPC service.

## Load the reference you need

Read one file, not all of them:

- **Schema layout, `buf.yaml`/`buf.gen.yaml`, lint, breaking-change CI** → `references/buf-and-codegen.md`
- **Go handlers, headers, errors, interceptors, streaming, h2c, CORS, compression, gRPC interop, testing** → `references/go-server.md`
- **ES transport, protocol choice, client, errors, cancellation, interceptors, runtime limits, TanStack Query, SSR, mocking** → `references/es-client.md`
- **A symptom you are debugging** → `references/troubleshooting.md`

Copyable starting configs live in `templates/`.

## Workflow for a new service

1. Write `proto/<pkg>/v1/<name>.proto`. Package is `<pkg>.v1`; the version suffix
   is mandatory for `buf lint`'s STANDARD rules.
2. Add protovalidate rules to request messages while writing them, not later.
3. `buf lint`, then `buf generate`.
4. Implement the Go handler interface (`<Service>Handler`); mount on `http.ServeMux`.
5. Create one ES transport for the app, derive clients from it.
6. `buf breaking --against '.git#branch=main'` in CI from the first commit.

## Gotchas that bite

- **Two Go codegen modes exist.** `simple` gives `func (s *S) M(ctx, *Req) (*Res, error)`;
  without it you get `*connect.Request[Req]` / `*connect.Response[Res]`. Read the
  generated `*_connect.go` before writing handlers — do not guess. Mixing the two
  shapes is the single most common failure here.
- **In simple mode, headers move to the context.** Server:
  `connect.CallInfoForHandlerContext(ctx)`. Client: `connect.NewClientContext(ctx)`.
  There is no `req.Header()` to reach for.
- **Routing is Protobuf-derived**: `POST /<pkg>.<Service>/<Method>`, case-sensitive,
  unrelated to Go import paths. Prefixing routes (`/api/`) breaks `grpc-go` clients.
- **CORS is HTTP middleware, not an interceptor.** Browser clients need
  `connectrpc.com/cors` helpers plus your own app headers explicitly allowed
  (`Authorization` is *not* included by default).
- **Unary Connect trailers arrive as `Trailer-`-prefixed headers** and must be
  exposed under that prefix for browsers to read them.
- **`http.Server.ReadTimeout`/`WriteTimeout` apply to the whole stream**, so they
  will kill long-lived streaming RPCs.
- **Browsers cannot do client or bidi streaming.** Server streaming only.
- **Protobuf-ES messages are plain objects** in v2 — no classes, no `new`. Build
  them with `create(SchemaRef, {...})` when you need an explicit instance.
- **`err instanceof ConnectError` is not guaranteed** for errors from fetch or
  wrappers. Normalise with `ConnectError.from(err)`.
- **`include_imports: true` is mandatory on `protoc-gen-es`** as soon as a proto
  imports protovalidate: the generated `*_pb.ts` hard-imports `validate_pb`, so
  without it `tsc` fails with `TS2307`.
- **Generated TS imports are extensionless.** Fine for bundlers, fatal under
  native Node ESM — add `import_extension=js` if the code runs in Node.
- **Go 1.24+ is required** (`http.Protocols`, `go get -tool`), but you don't have
  to install it: `go mod edit -go=1.25.0` makes `GOTOOLCHAIN=auto` fetch it.
