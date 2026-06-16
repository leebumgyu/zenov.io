# 01. Frontend Vercel Deployment

## Purpose

Deploy the Zenov public web platform:

```text
Partner Folder
Executive Dashboard
Education Center
```

## Upload Folder

Upload the contents of:

```text
01_frontend_vercel
```

to the Vercel frontend GitHub repository root.

## Correct GitHub Root Structure

```text
index.html
app.css
app.js
partner/
education/
locales/
vercel.json
```

Do not upload the `01_frontend_vercel` folder itself.

## Why This Folder Is Production Ready

This frontend has already been corrected for Vercel root deployment.

It does not require:

```text
/demo-web/app.css
/demo-web/app.js
```

The production frontend uses relative paths:

```text
./app.css
./app.js
../app.css
```

## Vercel Setting

If Vercel asks for a framework preset:

```text
Framework Preset: Other
Build Command: blank
Output Directory: blank or .
Install Command: blank
```

## API Proxy

The included `vercel.json` sends:

```text
/api/*
```

to:

```text
https://api.zenov.io/api/*
```

## Test URLs

After deployment:

```text
https://zenov.io/
https://zenov.io/partner/
https://zenov.io/education.html
```

The CSS must load immediately. If the page is unstyled, the wrong folder level was uploaded.

