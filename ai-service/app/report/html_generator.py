# Generates HTML reports for preview or conversion.
import json
from jinja2 import Template

# Premium styled Single Page HTML Template
HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <!-- Import Google Typography Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Tailwind CSS Engine for style compilation -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Interactive Plotly JS engine -->
    <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        title: ['Outfit', 'sans-serif'],
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
        }
        /* Custom print formatting to save report as PDF */
        @media print {
            .no-print { display: none !important; }
            body { background: white; color: black; }
            main { padding: 0; max-width: 100%; }
            .print-page-break { page-break-after: always; }
        }
    </style>
</head>
<body class="text-slate-900 bg-slate-50/50 min-h-screen selection:bg-indigo-100 selection:text-indigo-900">
    <!-- Header Banner -->
    <header class="bg-gradient-to-r from-indigo-700 via-indigo-800 to-indigo-950 text-white shadow-md relative overflow-hidden print-page-break">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.25),transparent_45%)]"></div>
        <div class="max-w-7xl mx-auto px-6 py-10 relative z-10">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                <div>
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 backdrop-blur-sm mb-4">
                        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                        InsightAI Auto-Generated Report
                    </span>
                    <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight leading-tight">{{ title }}</h1>
                </div>
                <div class="flex items-center gap-3">
                    <span class="text-xs text-indigo-200 uppercase font-semibold tracking-wider">Dataset Source</span>
                    <span class="text-sm font-mono font-bold bg-indigo-900/60 border border-indigo-700/60 px-3 py-1.5 rounded-lg shadow-inner text-white">
                        {{ dataset_id }}
                    </span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="max-w-7xl mx-auto px-6 py-12">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            
            <!-- Side Panel (Data Profile & Metric Widgets) -->
            <div class="space-y-6 lg:col-span-1 no-print">
                <!-- Size profile card -->
                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 transition-all hover:shadow-md">
                    <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider border-b border-slate-100 pb-3 mb-4">Dataset Profile</h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                            <span class="text-xs text-slate-500 font-semibold block mb-1">Rows</span>
                            <span class="text-3xl font-extrabold text-indigo-600 tracking-tight">{{ row_count }}</span>
                        </div>
                        <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                            <span class="text-xs text-slate-500 font-semibold block mb-1">Columns</span>
                            <span class="text-3xl font-extrabold text-indigo-600 tracking-tight">{{ col_count }}</span>
                        </div>
                    </div>
                </div>

                <!-- Fields listing card -->
                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 transition-all hover:shadow-md">
                    <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wider border-b border-slate-100 pb-3 mb-4">Attributes Schema</h3>
                    <div class="space-y-2 max-h-80 overflow-y-auto pr-1">
                        {% for col, info in columns.items() %}
                        <div class="flex items-center justify-between p-2 hover:bg-indigo-50/30 rounded-lg transition-colors border border-transparent">
                            <span class="text-xs font-mono text-slate-700 truncate max-w-[170px]" title="{{ col }}">{{ col }}</span>
                            <span class="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100/50">
                                {{ info.type }}
                            </span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Content Area (Visualizations and AI Analysis) -->
            <div class="lg:col-span-2 space-y-8">
                
                <!-- Plotly Visualizations Section -->
                {% if charts %}
                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 lg:p-8 transition-all hover:shadow-md">
                    <h2 class="text-xl lg:text-2xl font-bold text-indigo-950 border-b border-slate-100 pb-4 mb-6">Visual Interpretations</h2>
                    <div class="space-y-8">
                        {% for chart in charts %}
                        <div class="border border-slate-100/80 rounded-2xl p-5 bg-slate-50/50 shadow-inner">
                            <h4 class="text-sm lg:text-base font-bold text-slate-800 mb-1">{{ chart.title }}</h4>
                            <p class="text-xs text-slate-500 mb-4">{{ chart.description }}</p>
                            <!-- Target Div for JS rendering -->
                            <div id="plotly_container_{{ loop.index }}" class="w-full bg-white rounded-xl border border-slate-200/60 shadow-sm overflow-hidden" style="height: 400px;"></div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}

                <!-- Detailed AI Analysis Section -->
                <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 lg:p-10 transition-all hover:shadow-md">
                    <div class="prose max-w-none text-slate-800">
                        {{ ai_analysis_html }}
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer Banner -->
    <footer class="bg-slate-900 border-t border-slate-800 text-slate-400 py-10 mt-16 text-center text-sm no-print">
        <div class="max-w-7xl mx-auto px-6">
            <p class="font-medium text-slate-300">Generated dynamically via the InsightAI microservice framework.</p>
            <p class="text-xs text-slate-600 mt-2">&copy; 2026 InsightAI Report Engine. All rights reserved.</p>
        </div>
    </footer>

    <!-- Plotly rendering scripts mapping backend config values -->
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            {% if charts %}
                {% for chart in charts %}
                try {
                    var layoutData = {{ chart.plotly_json }};
                    // Ensure full width responsiveness of components
                    layoutData.layout = layoutData.layout || {};
                    layoutData.layout.autosize = true;
                    layoutData.layout.width = null;
                    layoutData.layout.paper_bgcolor = "rgba(0,0,0,0)";
                    layoutData.layout.plot_bgcolor = "rgba(0,0,0,0)";
                    Plotly.newPlot("plotly_container_{{ loop.index }}", layoutData.data, layoutData.layout, {responsive: true, displayModeBar: false});
                } catch(e) {
                    console.error("Failed to render Plotly chart {{ loop.index }}:", e);
                    document.getElementById("plotly_container_{{ loop.index }}").innerHTML = 
                        "<div class='h-full flex items-center justify-center text-rose-500 font-semibold text-xs bg-rose-50 border border-rose-100 rounded-xl'>Visualization rendering error: " + e.message + "</div>";
                }
                {% endfor %}
            {% endif %}
        });
    </script>
</body>
</html>
"""

def generate_report_html(title: str, dataset_id: str, row_count: int, col_count: int, columns: dict, charts: list[dict], ai_analysis_html: str) -> str:
    """
    Assembles dataset properties, visual components, and LLM text analysis
    into a beautiful single-page interactive HTML dashboard report.
    """
    html_template = Template(HTML_REPORT_TEMPLATE)
    return html_template.render(
        title=title,
        dataset_id=dataset_id,
        row_count=row_count,
        col_count=col_count,
        columns=columns,
        charts=charts,
        ai_analysis_html=ai_analysis_html
    )