# 03. Supabase Database Setup

## Purpose

Supabase PostgreSQL stores production Partner Folder submissions.

## Create Project

Go to:

```text
https://supabase.com
```

Create:

```text
Project Name: zenov
Region: nearest available region
Database Password: strong password
```

## Get Connection String

Find:

```text
Project Settings
Database
Connection string
URI
```

Render needs a URL similar to:

```text
postgresql://USER:PASSWORD@HOST:PORT/postgres
```

If Render uses psycopg, this form is also acceptable:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/postgres?sslmode=require
```

The API normalizes both formats.

## Where To Put It

Put the value only in Render environment variables:

```text
DATABASE_URL
```

Never put the database URL in:

```text
HTML
JavaScript
GitHub public files
Vercel frontend variables
```

