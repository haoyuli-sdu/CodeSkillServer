---
name: "project-scaffold"
description: "Scaffold a new full-stack project with Next.js (client), Express (server), shared types/validation, and full VPS deployment setup. Use when starting a new project from scratch. Creates complete folder structure, configs, base files, deployment scripts, and runs npm install."
---

# Project Scaffold

Scaffold a complete production-ready full-stack project: Next.js + Express + MongoDB + VPS deployment.

## Project name

If `$ARGUMENTS` is provided, use it as the project name (kebab-case). Otherwise ask the user for a project name before proceeding.

## What to build

```
{project-name}/
  client/               ← Next.js app
  server/               ← Express API
  shared/               ← Zod schemas + TypeScript types
  deploy/               ← GitHub webhook server
  nginx/
    app.conf            ← Nginx config template
  ecosystem.config.js   ← PM2 process definitions
  setup.sh              ← one-time VPS setup script
  .env.example          ← documents ALL vars across all services
  .gitignore
  README.md
```

---

## Step 1 — Root

```bash
mkdir {project-name}
cd {project-name}
git init
```

### `.gitignore`
```
node_modules/
.env
dist/
.next/
*.log
logs/
uploads/
```

### `.env.example`
```bash
# ---- SERVER ----
NODE_ENV=development
PORT=5000
MONGODB_URL=mongodb://localhost:27017/{project-name}
SESSION_SECRET=change-me-in-production
LOG_LEVEL=info
CLIENT_URL=http://localhost:3000

# ---- CLIENT ----
NEXT_PUBLIC_API_URL=http://localhost:5000/api

# ---- DEPLOY ----
WEBHOOK_SECRET=your-webhook-secret
PROJECT_NAME={project-name}
PROJECT_DIR=/var/www/{project-name}
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=your-app-password
RECIPIENT_EMAIL=your@gmail.com
```

### `README.md`
```md
# {project-name}

Full-stack app: Next.js + Express + MongoDB.

## Structure
- `/client` — Next.js frontend (port 3000)
- `/server` — Express API (port 5000)
- `/shared` — Zod schemas and TypeScript types
- `/deploy` — GitHub webhook server (port 3001)

## Local development
1. Copy `.env.example` values into `server/.env` and `client/.env`
2. `cd server && npm run dev`
3. `cd client && npm run dev`

## Production deployment
1. SSH into VPS
2. `git clone <repo>`
3. Fill in all `.env` files
4. `chmod +x setup.sh && ./setup.sh`
```

---

## Step 2 — Shared

### `shared/package.json`
```json
{
  "name": "@shared",
  "version": "1.0.0",
  "private": true
}
```

### `shared/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "./dist",
    "rootDir": "./"
  },
  "include": ["./**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### `shared/schemas/common.ts`
```typescript
import { z } from "zod";

// Pagination
export const paginationSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(10),
  search: z.string().optional(),
});
export type PaginationQuery = z.infer<typeof paginationSchema>;

// Params
export const idParamSchema = z.object({
  id: z.string().min(1),
});
export type IdParam = z.infer<typeof idParamSchema>;

export const slugParamSchema = z.object({
  slug: z.string().min(1),
});
export type SlugParam = z.infer<typeof slugParamSchema>;

// Pagination result
export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}
```

---

## Step 3 — Server

### `server/package.json`
```json
{
  "name": "server",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "tsx watch src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  },
  "dependencies": {
    "bcryptjs": "^2.4.3",
    "compression": "^1.7.4",
    "connect-mongo": "^5.1.0",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "express-rate-limit": "^7.1.5",
    "express-session": "^1.17.3",
    "mongoose": "^8.0.0",
    "morgan": "^1.10.0",
    "multer": "^1.4.5-lts.1",
    "slugify": "^1.6.6",
    "winston": "^3.11.0",
    "winston-daily-rotate-file": "^4.7.1",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/bcryptjs": "^2.4.6",
    "@types/compression": "^1.7.5",
    "@types/cors": "^2.8.17",
    "@types/express": "^4.17.21",
    "@types/express-session": "^1.17.10",
    "@types/morgan": "^1.9.9",
    "@types/multer": "^1.4.11",
    "@types/node": "^20.10.0",
    "tsx": "^4.6.2",
    "typescript": "^5.3.2"
  }
}
```

### `server/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "paths": {
      "@shared/*": ["../shared/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

### `server/.env.example`
```
NODE_ENV=development
PORT=5000
MONGODB_URL=mongodb://localhost:27017/{project-name}
SESSION_SECRET=change-me-in-production
LOG_LEVEL=info
CLIENT_URL=http://localhost:3000
```

### `server/src/config/env.config.ts`
```typescript
import { z } from "zod";

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  PORT: z.string().default("5000"),
  MONGODB_URL: z.string().min(1, "MONGODB_URL is required"),
  SESSION_SECRET: z.string().min(1, "SESSION_SECRET is required"),
  LOG_LEVEL: z.string().default("info"),
  CLIENT_URL: z.string().default("http://localhost:3000"),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error("❌ Invalid environment variables:");
  console.error(parsed.error.format());
  process.exit(1);
}

export const env = parsed.data;
```

### `server/src/config/db.config.ts`
```typescript
import mongoose from "mongoose";
import { env } from "./env.config";
import { logger } from "./logger.config";

export const connectDB = async (): Promise<void> => {
  try {
    await mongoose.connect(env.MONGODB_URL);
    logger.info("MongoDB connected");
  } catch (error) {
    logger.error("MongoDB connection failed", { error });
    process.exit(1);
  }
};
```

### `server/src/config/logger.config.ts`
```typescript
import winston from "winston";
import DailyRotateFile from "winston-daily-rotate-file";
import { env } from "./env.config";

const devFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: "HH:mm:ss" }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    const metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : "";
    return `${timestamp} [${level}]: ${message} ${metaStr}`;
  })
);

const prodFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

const transports: winston.transport[] = [
  new winston.transports.Console({
    format: env.NODE_ENV === "production" ? prodFormat : devFormat,
    level: env.LOG_LEVEL,
  }),
];

if (env.NODE_ENV === "production") {
  transports.push(
    new DailyRotateFile({
      filename: "logs/error-%DATE%.log",
      datePattern: "YYYY-MM-DD",
      level: "error",
      format: prodFormat,
      maxFiles: "30d",
      maxSize: "20m",
    }),
    new DailyRotateFile({
      filename: "logs/combined-%DATE%.log",
      datePattern: "YYYY-MM-DD",
      format: prodFormat,
      maxFiles: "30d",
      maxSize: "20m",
    })
  );
}

export const logger = winston.createLogger({
  level: env.LOG_LEVEL,
  transports,
  exitOnError: false,
});
```

### `server/src/config/session.config.ts`
```typescript
import session from "express-session";
import MongoStore from "connect-mongo";
import { env } from "./env.config";

export const sessionMiddleware = session({
  secret: env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({
    mongoUrl: env.MONGODB_URL,
    collectionName: "sessions",
    ttl: 60 * 60 * 24 * 7,
  }),
  cookie: {
    secure: env.NODE_ENV === "production",
    httpOnly: true,
    maxAge: 1000 * 60 * 60 * 24 * 7,
    sameSite: env.NODE_ENV === "production" ? "strict" : "lax",
  },
});
```

### `server/src/config/rateLimit.config.ts`
```typescript
import rateLimit from "express-rate-limit";

export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { success: false, error: { message: "Too many requests" } },
});

export const uploadLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: { success: false, error: { message: "Too many upload requests" } },
});

export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  message: { success: false, error: { message: "Too many auth attempts" } },
});
```

### `server/src/middleware/error.middleware.ts`
```typescript
import { Request, Response, NextFunction } from "express";
import { logger } from "../config/logger.config";
import { env } from "../config/env.config";

export const errorHandler = (
  err: any,
  req: Request,
  res: Response,
  _next: NextFunction
) => {
  logger.error("Unhandled error:", {
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method,
  });

  if (err.name === "ValidationError") {
    const errors = Object.values(err.errors).map((e: any) => ({
      field: e.path,
      message: e.message,
    }));
    return res.status(400).json({
      success: false,
      error: { message: "Validation failed", details: errors },
    });
  }

  if (err.name === "CastError") {
    return res.status(400).json({
      success: false,
      error: { message: `Invalid ${err.path}: ${err.value}` },
    });
  }

  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    return res.status(409).json({
      success: false,
      error: { message: `${field} already exists` },
    });
  }

  if (err.type === "entity.too.large") {
    return res.status(413).json({
      success: false,
      error: { message: "Request body too large" },
    });
  }

  const status = err.status || err.statusCode || 500;
  res.status(status).json({
    success: false,
    error: {
      message: err.message || "Internal server error",
      ...(env.NODE_ENV !== "production" && { stack: err.stack }),
    },
  });
};
```

### `server/src/middleware/validate.middleware.ts`
```typescript
import { Request, Response, NextFunction } from "express";
import { ZodSchema } from "zod";

interface ValidateSchemas {
  body?: ZodSchema;
  params?: ZodSchema;
  query?: ZodSchema;
}

export const validate = (schemas: ValidateSchemas) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (schemas.params) {
      const result = schemas.params.safeParse(req.params);
      if (!result.success) {
        return res.status(400).json({
          success: false,
          error: { message: "Invalid params", details: result.error.flatten().fieldErrors },
        });
      }
      req.params = result.data;
    }

    if (schemas.query) {
      const result = schemas.query.safeParse(req.query);
      if (!result.success) {
        return res.status(400).json({
          success: false,
          error: { message: "Invalid query", details: result.error.flatten().fieldErrors },
        });
      }
      req.query = result.data;
    }

    if (schemas.body) {
      const result = schemas.body.safeParse(req.body);
      if (!result.success) {
        return res.status(400).json({
          success: false,
          error: { message: "Invalid body", details: result.error.flatten().fieldErrors },
        });
      }
      req.body = result.data;
    }

    next();
  };
};
```

### `server/src/middleware/auth.middleware.ts`
```typescript
import { Request, Response, NextFunction } from "express";

export const auth = (req: Request, res: Response, next: NextFunction) => {
  if (!req.session || !(req.session as any).userId) {
    return res.status(401).json({
      success: false,
      error: { message: "Unauthorized" },
    });
  }
  next();
};
```

### `server/src/middleware/upload.middleware.ts`
```typescript
import multer from "multer";
import path from "path";
import fs from "fs";
import { Request } from "express";

const UPLOADS_DIR = path.join(process.cwd(), "uploads");
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, UPLOADS_DIR),
  filename: (_req, file, cb) => {
    const unique = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
    cb(null, `${unique}${path.extname(file.originalname)}`);
  },
});

const fileFilter = (
  _req: Request,
  file: Express.Multer.File,
  cb: multer.FileFilterCallback
) => {
  const allowed = /jpeg|jpg|png|gif|webp|pdf|doc|docx/;
  const ext = allowed.test(path.extname(file.originalname).toLowerCase());
  const mime = allowed.test(file.mimetype);
  if (ext && mime) return cb(null, true);
  cb(new Error("File type not allowed"));
};

export const uploadSingle = (fieldName: string) =>
  multer({ storage, fileFilter, limits: { fileSize: 10 * 1024 * 1024 } }).single(fieldName);

export const uploadMultiple = (fieldName: string, maxCount = 10) =>
  multer({ storage, fileFilter, limits: { fileSize: 10 * 1024 * 1024 } }).array(fieldName, maxCount);

export const handleUploadError = (err: any, _req: Request, res: any, next: any) => {
  if (err instanceof multer.MulterError || err.message === "File type not allowed") {
    return res.status(400).json({ success: false, error: { message: err.message } });
  }
  next(err);
};

export const getFileUrl = (file: Express.Multer.File): string =>
  `/uploads/${file.filename}`;

export const getFileUrls = (files: Express.Multer.File[]): string[] =>
  files.map(getFileUrl);

export const deleteFile = (url: string): void => {
  const filePath = path.join(process.cwd(), url);
  if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
};

export const deleteFiles = (urls: string[]): void =>
  urls.forEach(deleteFile);
```

### `server/src/services/base.service.ts`
```typescript
import { Model, Document } from "mongoose";
import { PaginationQuery, PaginatedResult } from "@shared/schemas/common";

export class BaseService<T extends Document> {
  constructor(
    protected model: Model<T>,
    protected defaultSort: Record<string, 1 | -1> = { createdAt: -1 }
  ) {}

  async getAll(
    query: PaginationQuery,
    filter: Record<string, any> = {}
  ): Promise<PaginatedResult<T>> {
    const { page, limit, search } = query;
    const baseFilter: any = { ...filter };

    if (search) {
      baseFilter.$text = { $search: search };
    }

    const [data, total] = await Promise.all([
      this.model
        .find(baseFilter)
        .sort(this.defaultSort)
        .skip((page - 1) * limit)
        .limit(limit)
        .lean(),
      this.model.countDocuments(baseFilter),
    ]);

    return {
      data: data as T[],
      pagination: { page, limit, total, pages: Math.ceil(total / limit) },
    };
  }

  async getById(id: string): Promise<T | null> {
    return this.model.findById(id).lean() as Promise<T | null>;
  }

  async getBySlug(slug: string): Promise<T | null> {
    return (this.model as any).findOne({ slug }).lean() as Promise<T | null>;
  }

  async create(data: Partial<T>): Promise<T> {
    return this.model.create(data) as Promise<T>;
  }

  async update(id: string, data: Partial<T>): Promise<T | null> {
    return this.model
      .findByIdAndUpdate(id, data, { new: true, runValidators: true })
      .lean() as Promise<T | null>;
  }

  async delete(id: string): Promise<T | null> {
    return this.model.findByIdAndDelete(id).lean() as Promise<T | null>;
  }
}
```

### `server/src/routes/index.ts`
```typescript
import { Router } from "express";

const router = Router();

// Register resource routes here
// Example: router.use("/news", newsRouter);

export default router;
```

### `server/src/app.ts`
```typescript
import express from "express";
import compression from "compression";
import cors from "cors";
import morgan from "morgan";
import path from "path";
import { sessionMiddleware } from "./config/session.config";
import { errorHandler } from "./middleware/error.middleware";
import { apiLimiter } from "./config/rateLimit.config";
import { env } from "./config/env.config";
import router from "./routes/index";

const app = express();

// Trust proxy — required when running behind Nginx on VPS
app.set("trust proxy", 1);

// Compression
app.use(compression());

// CORS
app.use(cors({ origin: env.CLIENT_URL, credentials: true }));

// Rate limiting
app.use("/api", apiLimiter);

// Body parsing
app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true, limit: "10mb" }));

// Session
app.use(sessionMiddleware);

// Static uploads
app.use("/uploads", express.static(path.join(process.cwd(), "uploads")));

// Request logging
app.use(morgan("dev"));

// Health check
app.get("/health", (_req, res) => {
  res.status(200).json({
    success: true,
    message: "Server is running",
    timestamp: new Date().toISOString(),
    environment: env.NODE_ENV,
  });
});

// API routes
app.use("/api", router);

// 404 handler
app.use("*", (req, res) => {
  res.status(404).json({
    success: false,
    error: { message: "Route not found", path: req.originalUrl, method: req.method },
  });
});

// Global error handler — must be last
app.use(errorHandler);

export default app;
```

### `server/src/server.ts`
```typescript
import "dotenv/config";
import fs from "fs";
import path from "path";
import app from "./app";
import { connectDB } from "./config/db.config";
import { env } from "./config/env.config";
import { logger } from "./config/logger.config";

process.on("unhandledRejection", (err: Error) => {
  logger.error("Unhandled Promise Rejection:", err);
  process.exit(1);
});

process.on("uncaughtException", (err: Error) => {
  logger.error("Uncaught Exception:", err);
  process.exit(1);
});

process.on("SIGTERM", () => {
  logger.info("SIGTERM received, shutting down gracefully");
  process.exit(0);
});

process.on("SIGINT", () => {
  logger.info("SIGINT received, shutting down gracefully");
  process.exit(0);
});

const start = async () => {
  try {
    const uploadDir = path.join(process.cwd(), "uploads");
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    await connectDB();

    app.listen(env.PORT, () => {
      logger.info(`Server running on port ${env.PORT} in ${env.NODE_ENV} mode`);
    });
  } catch (error) {
    logger.error("Failed to start server:", error);
    process.exit(1);
  }
};

start();
```

---

## Step 4 — Client

Run:
```bash
cd client
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir no --import-alias "@/*"
```

### Update `client/tsconfig.json` — add shared alias
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"],
      "@shared/*": ["../shared/*"]
    }
  }
}
```

### `client/.env.example`
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api
```

### `client/lib/api/axios.ts`
```typescript
import axios from "axios";

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api",
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        window.location.href = "/admin/login";
      }
    }
    return Promise.reject(error);
  }
);
```

### `client/lib/api/auth.ts`
```typescript
import { api } from "./axios";

export const getMe = () => api.get("/auth/me");
export const login = (data: { email: string; password: string }) =>
  api.post("/auth/login", data);
export const logout = () => api.post("/auth/logout");
```

### `client/lib/api/index.ts`
```typescript
export * from "./auth";
```

### `client/middleware.ts`
```typescript
import { NextRequest, NextResponse } from "next/server";

// Add public protected routes here if needed
const protectedRoutes: string[] = [];

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/admin")) {
    if (pathname === "/admin/login") return NextResponse.next();
    const session = request.cookies.get("connect.sid");
    if (!session) {
      return NextResponse.redirect(new URL("/admin/login", request.url));
    }
    return NextResponse.next();
  }

  if (protectedRoutes.some((route) => pathname.startsWith(route))) {
    const session = request.cookies.get("connect.sid");
    if (!session) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
```

### `client/app/admin/login/page.tsx`
```tsx
export default function LoginPage() {
  return <div>Login — add /auth-session or /auth-google skill</div>;
}
```

### `client/app/admin/(dashboard)/layout.tsx`
```tsx
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>;
}
```

### Create empty folders
```bash
mkdir -p client/components/ui
mkdir -p client/components/common
mkdir -p client/hooks
mkdir -p client/types
mkdir -p client/styles
```

---

## Step 5 — Deploy

### `deploy/package.json`
```json
{
  "name": "deploy",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "start": "node webhook.js",
    "dev": "node --watch webhook.js"
  },
  "dependencies": {
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "nodemailer": "^6.9.7"
  }
}
```

### `deploy/.env.example`
```
WEBHOOK_SECRET=your-webhook-secret
PROJECT_NAME={project-name}
PROJECT_DIR=/var/www/{project-name}
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=your-app-password
RECIPIENT_EMAIL=your@gmail.com
```

### `deploy/webhook.js`
```javascript
require("dotenv").config();
const express = require("express");
const crypto = require("crypto");
const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
const nodemailer = require("nodemailer");

const app = express();
const PORT = 3001;

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const PROJECT_DIR = process.env.PROJECT_DIR;
const PROJECT_NAME = process.env.PROJECT_NAME || "app";
const LOG_FILE = path.join(__dirname, "deployment.log");

if (!WEBHOOK_SECRET) {
  console.error("❌ WEBHOOK_SECRET is required");
  process.exit(1);
}

if (!PROJECT_DIR) {
  console.error("❌ PROJECT_DIR is required");
  process.exit(1);
}

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(logMessage.trim());
  fs.appendFileSync(LOG_FILE, logMessage);
}

async function sendEmail(message, isError = false) {
  try {
    const { GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL } = process.env;
    if (!GMAIL_USER || !GMAIL_APP_PASSWORD || !RECIPIENT_EMAIL) return;

    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: { user: GMAIL_USER, pass: GMAIL_APP_PASSWORD },
    });

    await transporter.sendMail({
      from: GMAIL_USER,
      to: RECIPIENT_EMAIL,
      subject: `${isError ? "❌ Failed" : "✅ Success"} — ${PROJECT_NAME} Deployment`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px;">
          <div style="background: ${isError ? "#f8d7da" : "#d4edda"}; padding: 20px; border-radius: 5px;">
            <h2 style="color: ${isError ? "#721c24" : "#155724"}; margin: 0;">
              ${isError ? "❌ Deployment Failed" : "✅ Deployment Successful"}
            </h2>
          </div>
          <div style="padding: 20px; background: #f8f9fa; border-radius: 5px; margin-top: 10px;">
            <pre style="color: #333; white-space: pre-wrap;">${message}</pre>
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">
              ${PROJECT_NAME} · ${new Date().toISOString()}
            </p>
          </div>
        </div>
      `,
    });

    log("Email notification sent");
  } catch (error) {
    log(`Failed to send email: ${error.message}`);
  }
}

app.use(express.json({
  verify: (req, _res, buf) => { req.rawBody = buf; },
}));

app.post(["/webhook", "/webhook/github"], (req, res) => {
  try {
    const signature = req.headers["x-hub-signature-256"];
    if (!signature) {
      log("No signature provided");
      return res.status(401).send("No signature provided");
    }

    const digest = "sha256=" + crypto
      .createHmac("sha256", WEBHOOK_SECRET)
      .update(req.rawBody)
      .digest("hex");

    const isValid = crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(digest)
    );

    if (!isValid) {
      log("Invalid signature");
      return res.status(401).send("Invalid signature");
    }

    const isMain =
      req.body.ref === "refs/heads/main" ||
      req.body.ref === "refs/heads/master";

    if (!isMain) {
      log(`Push ignored: ${req.body.ref}`);
      return res.status(200).send("Ignored");
    }

    log("Push to main detected — starting deployment");
    setImmediate(deploy);
    return res.status(200).send("Deployment started");

  } catch (error) {
    log(`Webhook error: ${error.message}`);
    return res.status(500).send("Webhook error");
  }
});

app.get("/health", (_req, res) => res.status(200).send("OK"));

async function deploy() {
  try {
    log("=== Deployment Started ===");
    process.chdir(PROJECT_DIR);

    log("Pulling latest changes...");
    execSync("git pull origin main", { stdio: "inherit", timeout: 60000 });

    log("Installing server dependencies...");
    execSync("cd server && npm install", { stdio: "inherit", timeout: 120000 });

    log("Building server...");
    execSync("cd server && npm run build", { stdio: "inherit", timeout: 120000 });

    log("Installing client dependencies...");
    execSync("cd client && npm install", { stdio: "inherit", timeout: 120000 });

    log("Building client...");
    execSync("cd client && npm run build", { stdio: "inherit", timeout: 300000 });

    log("Restarting services...");

    try {
      execSync("pm2 restart server", { stdio: "inherit" });
    } catch {
      execSync("pm2 start server/dist/server.js --name server", { stdio: "inherit" });
    }

    try {
      execSync("pm2 restart client", { stdio: "inherit" });
    } catch {
      execSync("pm2 start npm --name client -- start", {
        stdio: "inherit",
        cwd: path.join(PROJECT_DIR, "client"),
      });
    }

    execSync("pm2 save", { stdio: "inherit" });

    log("=== Deployment Completed ===");
    await sendEmail("Deployment completed successfully!");

  } catch (error) {
    log(`Deployment failed: ${error.message}`);
    await sendEmail(`Deployment failed!\n\nError: ${error.message}`, true);
  }
}

process.on("SIGINT", () => { log("Shutting down..."); process.exit(0); });
process.on("SIGTERM", () => { log("Shutting down..."); process.exit(0); });

app.listen(PORT, () => log(`Webhook server running on port ${PORT}`));
```

---

## Step 6 — Nginx config

### `nginx/app.conf`
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN www.YOUR_DOMAIN;

    # Next.js client
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Express API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Uploads
    location /uploads {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
}
```

---

## Step 7 — PM2 ecosystem

### `ecosystem.config.js`
```javascript
module.exports = {
  apps: [
    {
      name: "server",
      script: "server/dist/server.js",
      cwd: "/var/www/{project-name}",
      env: { NODE_ENV: "production" },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      error_file: "logs/server-error.log",
      out_file: "logs/server-out.log",
    },
    {
      name: "client",
      script: "npm",
      args: "start",
      cwd: "/var/www/{project-name}/client",
      env: { NODE_ENV: "production", PORT: 3000 },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      error_file: "logs/client-error.log",
      out_file: "logs/client-out.log",
    },
    {
      name: "deploy",
      script: "deploy/webhook.js",
      cwd: "/var/www/{project-name}",
      env: { NODE_ENV: "production" },
      instances: 1,
      autorestart: true,
      watch: false,
      error_file: "logs/deploy-error.log",
      out_file: "logs/deploy-out.log",
    },
  ],
};
```

---

## Step 8 — Setup script

### `setup.sh`
```bash
#!/bin/bash
set -e

echo ""
echo "========================================="
echo "  {project-name} — VPS Setup"
echo "========================================="
echo ""

# Ask for domain
read -p "Enter your domain name (e.g. myproject.com): " DOMAIN
if [ -z "$DOMAIN" ]; then
  echo "❌ Domain name is required"
  exit 1
fi

PROJECT_DIR=$(pwd)
echo "📁 Project directory: $PROJECT_DIR"
echo "🌐 Domain: $DOMAIN"
echo ""

# Update system
echo "📦 Updating system..."
apt-get update -y && apt-get upgrade -y
apt-get install -y curl git ufw

# Install Node.js via nvm
echo "📦 Installing Node.js..."
if ! command -v node &> /dev/null; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
  nvm install 20
  nvm use 20
  nvm alias default 20
  echo "✅ Node.js $(node -v) installed"
else
  echo "✅ Node.js already installed: $(node -v)"
fi

# Install PM2
echo "📦 Installing PM2..."
npm install -g pm2
echo "✅ PM2 installed"

# Install MongoDB
echo "📦 Installing MongoDB..."
if ! command -v mongod &> /dev/null; then
  curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
  echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
  apt-get update -y
  apt-get install -y mongodb-org
  systemctl start mongod
  systemctl enable mongod
  echo "✅ MongoDB installed and started"
else
  echo "✅ MongoDB already installed"
fi

# Install Nginx
echo "📦 Installing Nginx..."
if ! command -v nginx &> /dev/null; then
  apt-get install -y nginx
  systemctl start nginx
  systemctl enable nginx
  echo "✅ Nginx installed"
else
  echo "✅ Nginx already installed"
fi

# Install Certbot
echo "📦 Installing Certbot..."
apt-get install -y certbot python3-certbot-nginx
echo "✅ Certbot installed"

# Configure UFW firewall
echo "🔒 Configuring firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3001/tcp
ufw deny 3000/tcp
ufw deny 5000/tcp
ufw --force enable
echo "✅ Firewall configured"

# Check .env files
echo ""
echo "🔍 Checking .env files..."
if [ ! -f "server/.env" ]; then
  cp server/.env.example server/.env
  echo "⚠️  server/.env created from example — fill in your values"
fi
if [ ! -f "client/.env" ]; then
  cp client/.env.example client/.env
  echo "⚠️  client/.env created from example — fill in your values"
fi
if [ ! -f "deploy/.env" ]; then
  cp deploy/.env.example deploy/.env
  echo "⚠️  deploy/.env created from example — fill in your values"
fi

# Update ecosystem.config.js with actual path
sed -i "s|/var/www/{project-name}|$PROJECT_DIR|g" ecosystem.config.js

# Create logs directory
mkdir -p logs

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
cd shared && npm install && cd ..
cd server && npm install && cd ..
cd client && npm install && cd ..
cd deploy && npm install && cd ..

# Build
echo ""
echo "🔨 Building server..."
cd server && npm run build && cd ..

echo "🔨 Building client..."
cd client && npm run build && cd ..

# Configure Nginx
echo ""
echo "🌐 Configuring Nginx for $DOMAIN..."
sed "s/YOUR_DOMAIN/$DOMAIN/g" nginx/app.conf > /etc/nginx/sites-available/{project-name}
ln -sf /etc/nginx/sites-available/{project-name} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
echo "✅ Nginx configured"

# SSL
echo ""
echo "🔒 Setting up SSL..."
GMAIL=$(grep GMAIL_USER deploy/.env | cut -d '=' -f2)
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $GMAIL || {
  echo "⚠️  Certbot failed — run manually: certbot --nginx -d $DOMAIN -d www.$DOMAIN"
}

# Start PM2
echo ""
echo "🚀 Starting services..."
pm2 start ecosystem.config.js
pm2 save

# PM2 startup on reboot
echo ""
echo "⚙️  Configuring PM2 startup on reboot..."
pm2 startup systemd -u root --hp /root
pm2 save

echo ""
echo "========================================="
echo "  ✅ Setup Complete!"
echo "========================================="
echo ""
echo "  🌐 App: https://$DOMAIN"
echo ""
echo "  Useful commands:"
echo "    pm2 status          — all processes"
echo "    pm2 logs server     — server logs"
echo "    pm2 logs client     — client logs"
echo "    pm2 logs deploy     — webhook logs"
echo ""
echo "  Next steps:"
echo "    1. GitHub → Settings → Webhooks"
echo "    2. URL: https://$DOMAIN:3001/webhook"
echo "    3. Secret: match WEBHOOK_SECRET in deploy/.env"
echo "    4. Run: /auth-session or /auth-google skill"
echo "    5. Run: /crud-resource skill for each resource"
echo ""
```

---

## Step 9 — Install dependencies locally

```bash
cd shared && npm install zod && cd ..
cd server && npm install && cd ..
cd client && npm install axios @tanstack/react-query && cd ..
cd client && npx shadcn@latest init && cd ..
# Choose: Default style, Zinc color, yes to CSS variables
cd deploy && npm install && cd ..
```

## Step 10 — Copy .env files locally

```bash
cp server/.env.example server/.env
cp client/.env.example client/.env
cp deploy/.env.example deploy/.env
```

Tell the user to fill in `server/.env` with their MongoDB URL and session secret.

---

## Step 11 — Final summary

After scaffolding complete, print this:

```
✅ Project scaffolded: {project-name}

Local development:
  Server:  cd server && npm run dev    → http://localhost:5000
  Client:  cd client && npm run dev    → http://localhost:3000
  Webhook: cd deploy && npm run dev    → http://localhost:3001

Fill in your .env files:
  server/.env  → MONGODB_URL, SESSION_SECRET
  client/.env  → NEXT_PUBLIC_API_URL
  deploy/.env  → WEBHOOK_SECRET, PROJECT_DIR, GMAIL credentials

Deploy to production:
  1. git push to GitHub
  2. SSH into VPS, git clone your repo
  3. Fill in all .env files on VPS
  4. chmod +x setup.sh && ./setup.sh
  5. Add GitHub webhook: https://yourdomain.com:3001/webhook

Add features:
  Auth:     /auth-session  or  /auth-google
  Resource: /crud-resource
```

---

## Rules — always follow these

- Every controller accepts `next: NextFunction` and calls `next(error)` in catch — never handle errors inline
- All env vars via `env` from `config/env.config.ts` — never `process.env` directly
- All validation via Zod schemas from `/shared/schemas/`
- One file per resource in `client/lib/api/`
- Admin routes always protected by session cookie in `middleware.ts`
- Public pages → server components, admin pages → TanStack Query
- Never expose port 3000 or 5000 directly — always through Nginx in production
