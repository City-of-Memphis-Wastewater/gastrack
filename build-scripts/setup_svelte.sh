#!/bin/bash
# build-scripts/setup_svelte.sh

echo "Setting up Svelte frontend..."

# 1. Initialize Node project in frontend/
cd frontend
npm init -y

# 2. Install Svelte/Vite via a template (minimal setup)
npm create vite@latest . -- --template svelte-ts

# 3. Install dependencies
npm install

# 4. Create a basic Svelte file that calls the Starlette API
echo "Creating basic Svelte component..."
mkdir -p src/lib
cat << 'EOF' > src/App.svelte
<script lang="ts">
    import { onMount } from 'svelte';

    let message = 'Loading...';
    let apiStatus = 'Waiting for API';

    onMount(async () => {
        try {
            const response = await fetch('/?format=json');
            const data = await response.json();
            apiStatus = 'Connected!';
            message = data.message;
        } catch (error) {
            apiStatus = 'Error connecting to Python API!';
            message = 'Is the Uvicorn server running?';
            console.error(error);
        }
    });
</script>

<main>
    <h1>GasTrack Biogas Data Entry</h1>
    <p>API Status: <strong>{apiStatus}</strong></p>
    <p>API Message: {message}</p>

    <section>
        <h2>Daily Input Form (Pre-Treatment)</h2>
        <form>
            <label for="date">Date:</label>
            <input type="date" id="date" />
            <button type="submit">Submit Data</button>
        </form>
    </section>
</main>

<style>
    main {
        font-family: sans-serif;
        padding: 2em;
    }
</style>
EOF

# 5. Add build script to package.json
# Note: You'll need to customize the build command if not using Vite defaults
sed -i '' 's/"build": "vite build"/"build": "vite build --outDir dist"/' package.json

echo "Svelte setup complete in 'frontend/'. Run 'npm install' and then 'npm run build' to create the 'dist' directory."

cd ..
