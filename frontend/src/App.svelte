<script lang="ts">
    import { onMount } from 'svelte';

    // 1. TypeScript Interfaces matching Python models
    interface Factor {
        key: string;
        value: number;
        description: string | null;
    }

    interface AnalyzerReading {
        timestamp: Date;
        sample_point: string;
        ch4_pct: number | null;
        co2_pct: number | null;
        h2s_ppm: number | null;
        t_sensor_f: number | null;
    }

    // --- State Management ---
    let factors: Factor[] = [];
    let isLoading: boolean = true;
    let error: string | null = null;
    
    // Mock latest reading data for immediate visualization
    let latestReading: AnalyzerReading = {
        timestamp: new Date(),
        sample_point: 'Sheet 1',
        ch4_pct: 62.5,
        co2_pct: 35.1,
        h2s_ppm: 250,
        t_sensor_f: 98.6
    };

    // --- API Fetching Logic ---
    onMount(async () => {
        try {
            const response = await fetch('/api/factors');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            factors = await response.json();
            error = null;
        } catch (e) {
            console.error("Failed to fetch factors:", e);
            error = "Failed to load configuration factors from API.";
        } finally {
            isLoading = false;
        }
    });

    // --- Utility Functions for Display ---
    function getFactor(key: string): string {
        const factor = factors.find(f => f.key === key);
        return factor ? factor.value.toFixed(4) : 'N/A';
    }

    function getFactorDescription(key: string): string {
        const factor = factors.find(f => f.key === key);
        return factor?.description || key;
    }

    // --- Helper Component for Status Metrics ---
    // Note: Svelte components are functions in a single file setup
    function MetricTile(props: { title: string, value: string, unit: string, color: string }) {
        return `
            <div class="p-3 bg-white/5 backdrop-blur-sm rounded-lg shadow-xl border border-gray-700/50 flex flex-col items-start space-y-1 ${props.color}">
                <p class="text-xs font-semibold uppercase opacity-70">${props.title}</p>
                <p class="text-2xl font-bold">
                    ${props.value}
                    <span class="text-xs font-normal opacity-80">${props.unit}</span>
                </p>
            </div>
        `;
    }
</script>

<div class="min-h-screen bg-gray-900 text-gray-100 p-6 sm:p-10 font-sans">
    <header class="mb-8">
        <h1 class="text-4xl font-extrabold text-teal-400 tracking-tight">GasTrack Dashboard</h1>
        <p class="text-gray-400">T.E. Maxson WWTP - Biogas Emission & Flow Model Interface</p>
    </header>

    <!-- Factors/Configuration Section -->
    <div class="mb-10 p-6 bg-gray-800 rounded-xl shadow-inner">
        <h2 class="text-2xl font-semibold mb-4 text-gray-200">System Configuration (Factors)</h2>
        
        {#if isLoading}
            <div class="text-teal-400">Loading emission factors...</div>
        {:else if error}
            <div class="text-red-400 p-4 bg-red-900/30 rounded-lg">{error}</div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {#each factors as factor}
                    <div class="p-3 bg-gray-700/50 rounded-lg">
                        <p class="text-sm font-mono text-yellow-300">{factor.key}</p>
                        <p class="text-lg font-bold flex justify-between items-center">
                            <span>{factor.value.toFixed(6)}</span>
                            <span class="text-xs text-gray-400 truncate ml-2" title="{factor.description || ''}">{factor.description || 'No Description'}</span>
                        </p>
                    </div>
                {/each}
            </div>
        {/if}
    </div>

    <!-- Biogas System Schematic (Responding to User Request) -->
    <div class="mb-10 p-6 bg-gray-800 rounded-xl shadow-2xl border-2 border-teal-500/50">
        <h2 class="text-2xl font-semibold mb-6 text-teal-400">Biogas Handling System Overview</h2>
        
        <div class="relative flex flex-col md:flex-row justify-between items-center w-full">
            
            <!-- 1. Covered Lagoon (Source) -->
            <div class="flex flex-col items-center p-4 bg-blue-900/30 border-2 border-blue-400 rounded-full w-48 h-48 justify-center shadow-lg mb-8 md:mb-0">
                <svg class="w-10 h-10 text-blue-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 21.6c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zM12 10.6v5.8M15 13.6h-6"></path>
                </svg>
                <p class="text-lg font-bold text-blue-300">COVERED LAGOON</p>
                <div class="text-xs text-gray-300">Generation Source</div>
            </div>

            <!-- Arrow 1: To Blower/Analyzer -->
            <div class="flex-grow flex items-center justify-center p-4 w-full md:w-auto">
                <svg class="w-full md:w-auto h-2 md:h-10 text-yellow-500 transform md:-rotate-90 rotate-0" fill="currentColor" viewBox="0 0 100 10" preserveAspectRatio="none">
                    <path d="M 0 5 L 90 5 L 85 0 L 100 5 L 85 10 L 90 5 Z" />
                </svg>
                <div class="absolute bg-yellow-900/50 text-xs p-1 rounded-md border border-yellow-500 opacity-80 mt-10 md:mt-0 md:-ml-8">RAW GAS</div>
            </div>

            <!-- 2. Blower/Compressor -->
            <div class="flex flex-col items-center p-4 bg-green-900/30 border-2 border-green-400 rounded-lg shadow-lg w-40 h-40 justify-center relative mb-8 md:mb-0">
                <svg class="w-10 h-10 text-green-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 018 10.144V4a2 2 0 00-2-2H2a2 2 0 00-2 2v6.144a18.022 18.022 0 01-1.048 5.356m0 0h18"></path>
                </svg>
                <p class="text-lg font-bold text-green-300">BLOWERS</p>
                <div class="text-xs text-gray-300">Flow/Pressure Control</div>

                <!-- Analyzer Sampling Point (Sheet 1) -->
                <div class="absolute top-0 right-0 p-1 bg-gray-600 rounded-bl-lg text-xs font-mono text-white">
                    <span class="text-red-400 font-bold mr-1">T:</span> {latestReading.t_sensor_f?.toFixed(1) || 'N/A'} °F
                </div>
            </div>

            <!-- Arrow 2: To Flare/Engine -->
            <div class="flex-grow flex items-center justify-center p-4 w-full md:w-auto">
                <svg class="w-full md:w-auto h-2 md:h-10 text-yellow-500 transform md:-rotate-90 rotate-0" fill="currentColor" viewBox="0 0 100 10" preserveAspectRatio="none">
                    <path d="M 0 5 L 90 5 L 85 0 L 100 5 L 85 10 L 90 5 Z" />
                </svg>
                <div class="absolute bg-yellow-900/50 text-xs p-1 rounded-md border border-yellow-500 opacity-80 mt-10 md:mt-0 md:-ml-8">CONDITIONED GAS</div>
            </div>

            <!-- 3. Utilization/Destruction (Flare) -->
            <div class="flex flex-col items-center p-4 bg-red-900/30 border-2 border-red-400 rounded-lg shadow-lg w-40 h-40 justify-center">
                <svg class="w-10 h-10 text-red-300 mb-2" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 20.5v-6h4v6a.5.5 0 001 0v-6h3.58a.42.42 0 00.37-.24l1.5-3a.42.42 0 00-.37-.6H16V9a4 4 0 00-8 0v1.66H4.05a.42.42 0 00-.37.6l1.5 3a.42.42 0 00.37.24H10v6a.5.5 0 001 0z"></path>
                </svg>
                <p class="text-lg font-bold text-red-300">FLARE / CHP</p>
                <div class="text-xs text-gray-300">Utilization/Destruction</div>
            </div>

        </div>

    </div>

    <!-- Latest Analyzer Data Display -->
    <div class="p-6 bg-gray-800 rounded-xl shadow-inner">
        <h2 class="text-2xl font-semibold mb-4 text-gray-200">Latest Analyzer Reading (Sheet 1)</h2>
        <p class="text-xs text-gray-500 mb-4">Last updated: {latestReading.timestamp.toLocaleTimeString()}</p>
        
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <!-- Methane (CH4) -->
            {@html MetricTile({ title: 'METHANE', value: latestReading.ch4_pct?.toFixed(2) || 'N/A', unit: '%', color: 'text-green-400' })}
            <!-- Carbon Dioxide (CO2) -->
            {@html MetricTile({ title: 'CO2', value: latestReading.co2_pct?.toFixed(2) || 'N/A', unit: '%', color: 'text-gray-400' })}
            <!-- Hydrogen Sulfide (H2S) -->
            {@html MetricTile({ title: 'H2S', value: latestReading.h2s_ppm?.toFixed(0) || 'N/A', unit: 'ppm', color: 'text-orange-400' })}
            <!-- NOx Emission Factor (from API Factors) -->
            {@html MetricTile({ title: 'NOx Emission Factor', value: getFactor('EMF_NOX_LBS_MMBTU'), unit: 'lbs/MMBTU', color: 'text-yellow-400' })}
        </div>
    </div>
</div>

<style>
    /* Global styles for a dark theme */
    :global(body) {
        background-color: #111827; /* gray-900 */
        font-family: 'Inter', sans-serif;
    }
</style>