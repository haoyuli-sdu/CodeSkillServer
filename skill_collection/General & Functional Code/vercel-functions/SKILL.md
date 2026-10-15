---
name: "vercel-functions"
description: "Generate Vercel Serverless and Edge Functions with middleware, ISR, streaming, and proper runtime configuration. Use when the user wants to create API routes, middleware, or server-side logic on Vercel."
---

## Instructions

You are a Vercel Functions expert. Generate production-ready Serverless Functions, Edge Functions, Middleware, and streaming implementations.

### Step 1: Gather requirements

Determine from user input or `$ARGUMENTS`:
- **Function type**: Serverless (Node.js), Edge (V8), Middleware, ISR, Streaming
- **Framework**: Next.js App Router, Next.js Pages Router, standalone `/api` directory
- **Purpose**: API endpoint, authentication, data fetching, real-time streaming, caching
- **Runtime constraints**: cold start tolerance, execution time, memory, region

### Step 2: Choose the right runtime

**Runtime comparison:**
| Feature | Serverless (Node.js) | Edge (V8) |
|---------|---------------------|-----------|
| Cold start | ~250ms | ~0ms (no cold start) |
| Max duration | 60s (Hobby) / 300s (Pro) / 900s (Enterprise) | 30s |
| Memory | 1024 MB (default, up to 3008 MB) | 128 MB |
| Node.js APIs | Full support | Limited (no `fs`, `net`, `child_process`) |
| npm packages | All | Must be Edge-compatible |
| Regions | Single (configurable) | All edge locations |
| Streaming | Yes | Yes |
| Use case | Heavy computation, DB access | Auth, redirects, A/B testing |

**Decision guide:**
- Use **Serverless** for: database queries, file processing, heavy computation, full Node.js API access
- Use **Edge** for: authentication checks, geolocation routing, A/B testing, header manipulation, lightweight transforms
- Use **Middleware** for: request interception before routing, auth guards, redirects, rewrites

### Step 3: Generate Serverless Functions

**Next.js App Router - Route Handlers (recommended):**
```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs'; // default
export const maxDuration = 30;
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const page = parseInt(searchParams.get('page') || '1');

  try {
    const users = await db.user.findMany({
      skip: (page - 1) * 20,
      take: 20,
    });

    return NextResponse.json({ users, page }, {
      status: 200,
      headers: {
        'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300',
      },
    });
  } catch (error) {
    console.error('Failed to fetch users:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  try {
    const user = await db.user.create({ data: body });
    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 400 }
    );
  }
}
```

**Next.js App Router - Dynamic route:**
```typescript
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  const user = await db.user.findUnique({ where: { id } });
  if (!user) {
    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  }

  return NextResponse.json(user);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const body = await request.json();

  const user = await db.user.update({
    where: { id },
    data: body,
  });

  return NextResponse.json(user);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  await db.user.delete({ where: { id } });
  return new NextResponse(null, { status: 204 });
}
```

**Next.js Pages Router - API Routes:**
```typescript
// pages/api/users.ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'GET') {
    const users = await db.user.findMany();
    return res.status(200).json(users);
  }

  if (req.method === 'POST') {
    const user = await db.user.create({ data: req.body });
    return res.status(201).json(user);
  }

  res.setHeader('Allow', ['GET', 'POST']);
  return res.status(405).json({ error: `Method ${req.method} not allowed` });
}
```

**Standalone Serverless Function (/api directory, non-Next.js):**
```typescript
// api/hello.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default function handler(req: VercelRequest, res: VercelResponse) {
  const { name = 'World' } = req.query;
  return res.json({ message: `Hello ${name}!` });
}
```

### Step 4: Generate Edge Functions

**Edge Route Handler (App Router):**
```typescript
// app/api/location/route.ts
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const country = request.geo?.country || 'US';
  const city = request.geo?.city || 'Unknown';
  const region = request.geo?.region || 'Unknown';

  return NextResponse.json({
    country,
    city,
    region,
    timestamp: Date.now(),
  });
}
```

**Edge Function with external API call:**
```typescript
// app/api/proxy/route.ts
export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const response = await fetch('https://api.example.com/data', {
    headers: {
      'Authorization': `Bearer ${process.env.API_KEY}`,
    },
  });

  const data = await response.json();

  return NextResponse.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400',
    },
  });
}
```

### Step 5: Generate Edge Middleware

**Authentication middleware:**
```typescript
// middleware.ts (project root)
import { NextRequest, NextResponse } from 'next/server';

export const config = {
  matcher: [
    // Match all paths except static files and api routes that don't need auth
    '/((?!_next/static|_next/image|favicon.ico|api/public).*)',
  ],
};

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session-token')?.value;

  // Redirect to login if no session token
  if (!token && !request.nextUrl.pathname.startsWith('/login')) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('callbackUrl', request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Add custom headers
  const response = NextResponse.next();
  response.headers.set('x-request-id', crypto.randomUUID());
  return response;
}
```

**Geolocation-based routing:**
```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

export const config = {
  matcher: ['/'],
};

export function middleware(request: NextRequest) {
  const country = request.geo?.country || 'US';

  // Rewrite to country-specific page
  if (country === 'DE' || country === 'AT' || country === 'CH') {
    return NextResponse.rewrite(new URL('/de', request.url));
  }

  if (country === 'FR' || country === 'BE') {
    return NextResponse.rewrite(new URL('/fr', request.url));
  }

  return NextResponse.next();
}
```

**A/B testing middleware:**
```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';

export const config = {
  matcher: ['/landing'],
};

export function middleware(request: NextRequest) {
  const bucket = request.cookies.get('ab-bucket')?.value;

  if (bucket) {
    return NextResponse.rewrite(new URL(`/landing/${bucket}`, request.url));
  }

  // Assign bucket: 50/50 split
  const newBucket = Math.random() < 0.5 ? 'control' : 'variant';
  const response = NextResponse.rewrite(
    new URL(`/landing/${newBucket}`, request.url)
  );
  response.cookies.set('ab-bucket', newBucket, {
    maxAge: 60 * 60 * 24 * 30, // 30 days
    httpOnly: true,
  });

  return response;
}
```

**Rate limiting middleware:**
```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
  analytics: true,
});

export const config = {
  matcher: ['/api/:path*'],
};

export async function middleware(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1';
  const { success, limit, remaining, reset } = await ratelimit.limit(ip);

  if (!success) {
    return NextResponse.json(
      { error: 'Too many requests' },
      {
        status: 429,
        headers: {
          'X-RateLimit-Limit': limit.toString(),
          'X-RateLimit-Remaining': remaining.toString(),
          'X-RateLimit-Reset': reset.toString(),
        },
      }
    );
  }

  return NextResponse.next();
}
```

### Step 6: Generate ISR (Incremental Static Regeneration)

**Time-based revalidation:**
```typescript
// app/posts/[slug]/page.tsx
export const revalidate = 3600; // Revalidate every hour

export async function generateStaticParams() {
  const posts = await db.post.findMany({ select: { slug: true } });
  return posts.map((post) => ({ slug: post.slug }));
}

export default async function PostPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await db.post.findUnique({ where: { slug } });
  return <article>{/* render post */}</article>;
}
```

**On-demand revalidation:**
```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const secret = request.headers.get('x-revalidation-secret');
  if (secret !== process.env.REVALIDATION_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { path, tag } = await request.json();

  if (tag) {
    revalidateTag(tag);
    return NextResponse.json({ revalidated: true, tag });
  }

  if (path) {
    revalidatePath(path);
    return NextResponse.json({ revalidated: true, path });
  }

  return NextResponse.json({ error: 'Missing path or tag' }, { status: 400 });
}
```

### Step 7: Generate streaming responses

**Streaming with AI SDK:**
```typescript
// app/api/chat/route.ts
import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';

export const maxDuration = 60;

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    messages,
  });

  return result.toDataStreamResponse();
}
```

**Manual streaming with ReadableStream:**
```typescript
// app/api/stream/route.ts
export const runtime = 'edge';

export async function GET() {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      for (let i = 0; i < 10; i++) {
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ count: i })}\n\n`)
        );
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

### Step 8: Function configuration

**Configure function settings in vercel.json:**
```json
{
  "functions": {
    "app/api/heavy-task/route.ts": {
      "maxDuration": 300,
      "memory": 3008
    },
    "app/api/edge-task/route.ts": {
      "runtime": "edge"
    },
    "app/api/regional/route.ts": {
      "regions": ["iad1"]
    }
  }
}
```

**Or inline with route segment config:**
```typescript
// app/api/heavy/route.ts
export const runtime = 'nodejs';
export const maxDuration = 300;
export const preferredRegion = 'iad1';
export const dynamic = 'force-dynamic';
export const fetchCache = 'default-no-store';
```

### Step 9: CORS handling

**Reusable CORS utility:**
```typescript
// lib/cors.ts
import { NextResponse } from 'next/server';

const allowedOrigins = [
  'https://yourdomain.com',
  'https://app.yourdomain.com',
];

export function cors(request: Request, response: NextResponse) {
  const origin = request.headers.get('origin');

  if (origin && allowedOrigins.includes(origin)) {
    response.headers.set('Access-Control-Allow-Origin', origin);
  }

  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  response.headers.set('Access-Control-Max-Age', '86400');

  return response;
}

// Handle preflight OPTIONS
export function handleOptions(request: Request) {
  const response = new NextResponse(null, { status: 204 });
  return cors(request, response);
}
```

**Apply to route:**
```typescript
// app/api/data/route.ts
import { cors, handleOptions } from '@/lib/cors';

export async function OPTIONS(request: Request) {
  return handleOptions(request);
}

export async function GET(request: Request) {
  const data = { message: 'Hello' };
  const response = NextResponse.json(data);
  return cors(request, response);
}
```

### Step 10: Local development

**Vercel CLI development server:**
```bash
# Install Vercel CLI
npm i -g vercel

# Link project and pull env vars
vercel link
vercel env pull .env.local

# Start local dev server with Vercel runtime
vercel dev

# Or use framework-specific dev (faster, but no Vercel features)
npm run dev
```

### Best practices:
- Use Edge Functions for latency-sensitive, lightweight operations
- Use Serverless Functions when you need full Node.js API access
- Set `maxDuration` explicitly to avoid unexpected timeouts
- Place middleware at the project root (`middleware.ts`)
- Use route segment config (`export const runtime = 'edge'`) over `vercel.json` when possible
- Implement proper error boundaries and structured error responses
- Use `Cache-Control` headers with `s-maxage` and `stale-while-revalidate` for CDN caching
- Add request ID headers in middleware for debugging and tracing
- Use ISR with on-demand revalidation for content that changes via CMS webhooks
- Keep Edge Functions small; avoid importing large packages

### Anti-patterns to avoid:
- Do not use Edge runtime with packages that require Node.js APIs (`fs`, `net`, `crypto` beyond Web Crypto)
- Do not set `maxDuration` higher than needed (increases cost and timeout risk)
- Avoid blocking middleware with heavy computation or slow external calls
- Do not use `force-dynamic` when static generation or ISR would work
- Never store state in function memory (functions are stateless between invocations)
- Do not skip error handling; unhandled errors return 500 with no useful information
- Avoid using `res.end()` patterns in App Router (use `NextResponse` or `Response`)

### Cost optimization:
- Use Edge Functions where possible (cheaper, no cold starts)
- Leverage ISR and caching to minimize function invocations
- Set `maxDuration` to the minimum needed to cap execution costs
- Use `s-maxage` caching headers aggressively for cacheable responses
- Avoid `force-dynamic` on pages that can be statically generated
- Monitor function invocation counts in Vercel Dashboard > Usage
- Consolidate API routes where logical to reduce function count
- Use `stale-while-revalidate` to serve cached content while refreshing in background
