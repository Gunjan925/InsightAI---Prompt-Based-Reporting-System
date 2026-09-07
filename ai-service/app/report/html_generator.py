# # Generates HTML reports for preview or conversion.
# import json
# from datetime import datetime, timezone, timedelta
# from jinja2 import Template

# # HTML Report Template: graphs in 2-column grid at top, then full-width AI analysis below
# HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>{{ title }}</title>
#     <!-- Import Google Typography Fonts -->
#     <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
#     <!-- Tailwind CSS Engine for style compilation -->
#     <script src="https://cdn.tailwindcss.com"></script>
#     <!-- Interactive Plotly JS engine -->
#     <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
#     <script>
#         tailwind.config = {
#             theme: {
#                 extend: {
#                     fontFamily: {
#                         sans: ['Inter', 'sans-serif'],
#                         title: ['Outfit', 'sans-serif'],
#                     }
#                 }
#             }
#         }
#     </script>
#     <style>
#         body {
#             font-family: 'Inter', sans-serif;
#             background-color: #f8fafc;
#             color: #1e293b;
#         }
#         h1, h2, h3, h4, h5, h6 {
#             font-family: 'Outfit', sans-serif;
#         }
#         /* User-Friendly Pointer Bullet Cards */
#         ul.pointer-list, ul.space-y-1, .prose ul {
#             list-style: none !important;
#             padding-left: 0 !important;
#             margin-top: 1rem;
#             margin-bottom: 1rem;
#         }
#         ul.pointer-list li, ul.space-y-1 li, .prose ul li {
#             position: relative;
#             padding: 10px 14px 10px 34px !important;
#             margin-bottom: 8px !important;
#             background-color: #ffffff;
#             border: 1px solid #e2e8f0;
#             border-left: 4px solid #4f46e5;
#             border-radius: 10px;
#             font-size: 0.875rem;
#             line-height: 1.6;
#             color: #334155;
#             box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
#         }
#         ul.pointer-list li::before, ul.space-y-1 li::before, .prose ul li::before {
#             content: "•";
#             position: absolute;
#             left: 14px;
#             top: 8px;
#             color: #4f46e5;
#             font-weight: 900;
#             font-size: 1.25rem;
#         }
#         .prose p {
#             margin-bottom: 0.75rem;
#             line-height: 1.6;
#             color: #334155;
#             font-size: 0.9rem;
#         }
#         /* Print layout optimizations */
#         @media print {
#             .no-print { display: none !important; }
#             body { background: white; color: black; }
#             main { padding: 0; max-width: 100%; }
#             .print-page-break { page-break-after: always; }
#         }
#     </style>
# </head>
# <body class="text-slate-900 bg-slate-50/50 min-h-screen selection:bg-indigo-100 selection:text-indigo-900">
#     <!-- Header Banner -->
#     <header class="bg-gradient-to-r from-indigo-800 via-indigo-900 to-slate-900 text-white shadow-md relative overflow-hidden">
#         <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.2),transparent_50%)]"></div>
#         <div class="max-w-7xl mx-auto px-6 py-8 relative z-10">
#             <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
#                 <div>
#                     <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 backdrop-blur-sm mb-3">
#                         <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
#                         InsightAI Analytical Report
#                     </span>
#                     <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight leading-tight">{{ title }}</h1>
#                 </div>
#                 <div class="flex flex-col items-end gap-2">
#                     <div class="flex items-center gap-3">
#                         <span class="text-xs text-indigo-200 uppercase font-semibold tracking-wider">Dataset File</span>
#                         <span class="text-xs font-mono font-bold bg-indigo-950/80 border border-indigo-700/50 px-3 py-1.5 rounded-lg text-white">
#                             {{ dataset_id }}
#                         </span>
#                     </div>
#                     <span class="text-xs text-indigo-300">Generated: <strong class="text-white">{{ generated_at }}</strong></span>
#                 </div>
#             </div>
#         </div>
#     </header>

#     <!-- Main Container: top-to-bottom flow -->
#     <main class="max-w-7xl mx-auto px-6 py-10 space-y-8">

#         <!-- SECTION 1: Dataset Stats Overview (full-width) -->
#         <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 no-print">
#             <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider border-b border-slate-100 pb-3 mb-4 flex items-center justify-between">
#                 <span>Dataset Overview</span>
#                 <span class="text-[11px] font-normal text-slate-500 font-mono">{{ row_count }} rows × {{ col_count }} cols</span>
#             </h3>
#             <div class="flex flex-wrap gap-6 items-center">
#                 <div class="bg-slate-50 px-6 py-4 rounded-xl border border-slate-100 text-center">
#                     <span class="text-xs text-slate-500 font-semibold block mb-1">Total Rows</span>
#                     <span class="text-2xl font-extrabold text-indigo-600 tracking-tight">{{ row_count }}</span>
#                 </div>
#                 <div class="bg-slate-50 px-6 py-4 rounded-xl border border-slate-100 text-center">
#                     <span class="text-xs text-slate-500 font-semibold block mb-1">Total Columns</span>
#                     <span class="text-2xl font-extrabold text-indigo-600 tracking-tight">{{ col_count }}</span>
#                 </div>
#                 <div class="flex-1 min-w-0">
#                     <span class="text-xs font-semibold text-slate-600 block mb-2">Column Attributes</span>
#                     <div class="flex flex-wrap gap-1.5">
#                         {% for col, info in columns.items() %}
#                         <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-mono border border-slate-200/60">
#                             <span>{{ col }}</span>
#                             <span class="text-[10px] uppercase text-indigo-600 font-semibold bg-indigo-50 px-1 rounded">{{ info.type }}</span>
#                         </span>
#                         {% endfor %}
#                     </div>
#                 </div>
#             </div>
#         </div>

#         <!-- SECTION 2: Visualizations — 2-Column Chart Grid (full width) -->
#         {% if charts %}
#         <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6">
#             <div class="border-b border-slate-100 pb-3 mb-6 flex items-center justify-between">
#                 <h2 class="text-lg font-bold text-slate-900">Visual Interpretations</h2>
#                 <span class="text-xs bg-indigo-50 text-indigo-700 font-semibold px-2.5 py-1 rounded-full border border-indigo-100">
#                     {{ charts|length }} Graphs
#                 </span>
#             </div>
#             <!-- 2-Column Chart Grid -->
#             <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
#                 {% for chart in charts %}
#                 <div class="border border-slate-200/80 rounded-xl p-4 bg-slate-50/40 shadow-xs flex flex-col">
#                     <div class="mb-2">
#                         <h4 class="text-sm font-bold text-slate-800 leading-snug" title="{{ chart.title }}">{{ chart.title }}</h4>
#                         {% if chart.description %}
#                         <p class="text-[11px] text-slate-500 mt-1">{{ chart.description }}</p>
#                         {% endif %}
#                     </div>
#                     <div id="plotly_container_{{ loop.index }}" class="w-full bg-white rounded-lg border border-slate-200/60 overflow-hidden flex-1" style="height: 380px;"></div>
#                 </div>
#                 {% endfor %}
#             </div>
#         </div>
#         {% endif %}

#         <!-- SECTION 3: Full-Width AI Analysis Text (single column, below charts) -->
#         <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 lg:p-8">
#             <div class="border-b border-slate-100 pb-3 mb-6">
#                 <h2 class="text-lg font-bold text-slate-900">AI-Generated Analysis</h2>
#             </div>
#             <div class="prose max-w-none text-slate-800">
#                 {{ ai_analysis_html }}
#             </div>
#         </div>

#     </main>

#     <!-- Footer -->
#     <footer class="bg-slate-900 border-t border-slate-800 text-slate-400 py-8 mt-12 text-center text-xs no-print">
#         <div class="max-w-7xl mx-auto px-6">
#             <p class="font-medium text-slate-300">Generated dynamically via the InsightAI microservice framework.</p>
#             <p class="text-slate-500 mt-1">&copy; 2026 InsightAI Report Engine. All rights reserved.</p>
#         </div>
#     </footer>

#     <!-- Plotly rendering scripts -->
#     <script>
#         function renderCharts() {
#             {% if charts %}
#                 {% for chart in charts %}
#                 try {
#                     var rawData = {{ chart.plotly_json }};
#                     rawData.layout = rawData.layout || {};
#                     rawData.layout.autosize = true;
#                     rawData.layout.width = null;
#                     rawData.layout.height = null;
#                     rawData.layout.margin = rawData.layout.margin || { l: 55, r: 25, t: 55, b: 65 };
#                     Plotly.newPlot(
#                         "plotly_container_{{ loop.index }}",
#                         rawData.data,
#                         rawData.layout,
#                         {
#                             responsive: true,
#                             displayModeBar: true,
#                             modeBarButtonsToRemove: ['lasso2d','select2d','autoScale2d'],
#                             displaylogo: false,
#                             scrollZoom: false
#                         }
#                     );
#                 } catch(e) {
#                     console.error("Failed to render Plotly chart {{ loop.index }}:", e);
#                     var el = document.getElementById("plotly_container_{{ loop.index }}");
#                     if (el) el.innerHTML =
#                         "<div style='height:100%;display:flex;align-items:center;justify-content:center;color:#e11d48;font-size:0.8rem;background:#fff1f2;border-radius:10px;padding:16px;text-align:center;'>Chart error: " + e.message + "</div>";
#                 }
#                 {% endfor %}
#             {% endif %}
#         }
#         // Run after DOM and Plotly are both ready
#         if (document.readyState === 'loading') {
#             document.addEventListener('DOMContentLoaded', renderCharts);
#         } else {
#             renderCharts();
#         }
#     </script>
# </body>
# </html>
# """

# def generate_report_html(title: str, dataset_id: str, row_count: int, col_count: int, columns: dict, charts: list[dict], ai_analysis_html: str) -> str:
#     """
#     Assembles dataset properties, visual components, and LLM text analysis
#     into a beautiful single-page interactive HTML dashboard report.
#     """
#     # Generate IST timestamp for the report header
#     IST = timezone(timedelta(hours=5, minutes=30))
#     generated_at = datetime.now(IST).strftime('%d %b %Y, %I:%M %p IST')

#     html_template = Template(HTML_REPORT_TEMPLATE)
#     return html_template.render(
#         title=title,
#         dataset_id=dataset_id,
#         row_count=row_count,
#         col_count=col_count,
#         columns=columns,
#         charts=charts,
#         ai_analysis_html=ai_analysis_html,
#         generated_at=generated_at
#     )

# Generates HTML reports for preview or conversion.
import json
from datetime import datetime, timezone, timedelta
from jinja2 import Template

# HTML Report Template: graphs in 2-column grid at top, then full-width AI analysis below
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
            color: #1e293b;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
        }
        /* User-Friendly Pointer Bullet Cards */
        ul.pointer-list, ul.space-y-1, .prose ul {
            list-style: none !important;
            padding-left: 0 !important;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        ul.pointer-list li, ul.space-y-1 li, .prose ul li {
            position: relative;
            padding: 10px 14px 10px 34px !important;
            margin-bottom: 8px !important;
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #4f46e5;
            border-radius: 10px;
            font-size: 0.875rem;
            line-height: 1.6;
            color: #334155;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }
        ul.pointer-list li::before, ul.space-y-1 li::before, .prose ul li::before {
            content: "•";
            position: absolute;
            left: 14px;
            top: 8px;
            color: #4f46e5;
            font-weight: 900;
            font-size: 1.25rem;
        }
        .prose p {
            margin-bottom: 0.75rem;
            line-height: 1.6;
            color: #334155;
            font-size: 0.9rem;
        }
        /* Print layout optimizations */
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
    <header class="bg-gradient-to-r from-indigo-800 via-indigo-900 to-slate-900 text-white shadow-md relative overflow-hidden">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.2),transparent_50%)]"></div>
        <div class="max-w-7xl mx-auto px-6 py-8 relative z-10">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-200 border border-indigo-500/30 backdrop-blur-sm mb-3">
                        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                        InsightAI Analytical Report
                    </span>
                    <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight leading-tight">{{ title }}</h1>
                </div>
                <div class="flex flex-col items-end gap-2">
                    <div class="flex items-center gap-3">
                        <span class="text-xs text-indigo-200 uppercase font-semibold tracking-wider">Dataset File</span>
                        <span class="text-xs font-mono font-bold bg-indigo-950/80 border border-indigo-700/50 px-3 py-1.5 rounded-lg text-white">
                            {{ dataset_id }}
                        </span>
                    </div>
                    <span class="text-xs text-indigo-300">Generated: <strong class="text-white">{{ generated_at }}</strong></span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container: top-to-bottom flow -->
    <main class="max-w-7xl mx-auto px-6 py-10 space-y-8">

        <!-- SECTION 1: Dataset Stats Overview (full-width) -->
        <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 no-print">
            <h3 class="text-xs font-bold text-slate-700 uppercase tracking-wider border-b border-slate-100 pb-3 mb-4 flex items-center justify-between">
                <span>Dataset Overview</span>
                <span class="text-[11px] font-normal text-slate-500 font-mono">{{ row_count }} rows × {{ col_count }} cols</span>
            </h3>
            <div class="flex flex-wrap gap-6 items-center">
                <div class="bg-slate-50 px-6 py-4 rounded-xl border border-slate-100 text-center">
                    <span class="text-xs text-slate-500 font-semibold block mb-1">Total Rows</span>
                    <span class="text-2xl font-extrabold text-indigo-600 tracking-tight">{{ row_count }}</span>
                </div>
                <div class="bg-slate-50 px-6 py-4 rounded-xl border border-slate-100 text-center">
                    <span class="text-xs text-slate-500 font-semibold block mb-1">Total Columns</span>
                    <span class="text-2xl font-extrabold text-indigo-600 tracking-tight">{{ col_count }}</span>
                </div>
                <div class="flex-1 min-w-0">
                    <span class="text-xs font-semibold text-slate-600 block mb-2">Column Attributes</span>
                    <div class="flex flex-wrap gap-1.5">
                        {% for col, info in columns.items() %}
                        <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs font-mono border border-slate-200/60">
                            <span>{{ col }}</span>
                            <span class="text-[10px] uppercase text-indigo-600 font-semibold bg-indigo-50 px-1 rounded">{{ info.type }}</span>
                        </span>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <!-- SECTION 2: Visualizations — 2-Column Chart Grid (Fixed layout issue) -->
        {% if charts %}
        <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6">
            <div class="border-b border-slate-100 pb-3 mb-6 flex items-center justify-between">
                <h2 class="text-lg font-bold text-slate-900">Visual Interpretations</h2>
                <span class="text-xs bg-indigo-50 text-indigo-700 font-semibold px-2.5 py-1 rounded-full border border-indigo-100">
                    {{ charts|length }} Graphs
                </span>
            </div>
            <!-- 2-Column Chart Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {% for chart in charts %}
                <div class="border border-slate-200/80 rounded-xl p-4 bg-slate-50/40 shadow-xs flex flex-col h-[420px]">
                    <div class="mb-2 shrink-0">
                        <h4 class="text-sm font-bold text-slate-800 leading-snug truncate" title="{{ chart.title }}">{{ chart.title }}</h4>
                        {% if chart.description %}
                        <p class="text-[11px] text-slate-500 mt-1 line-clamp-2">{{ chart.description }}</p>
                        {% endif %}
                    </div>
                    <div id="plotly_container_{{ loop.index }}" class="w-full flex-1 min-h-0 bg-white rounded-lg border border-slate-200/60 overflow-hidden"></div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- SECTION 3: Full-Width AI Analysis Text (single column, below charts) -->
        <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 lg:p-8">
            <div class="border-b border-slate-100 pb-3 mb-6">
                <h2 class="text-lg font-bold text-slate-900">AI-Generated Analysis</h2>
            </div>
            <div class="prose max-w-none text-slate-800">
                {{ ai_analysis_html }}
            </div>
        </div>

    </main>

    <!-- Footer -->
    <footer class="bg-slate-900 border-t border-slate-800 text-slate-400 py-8 mt-12 text-center text-xs no-print">
        <div class="max-w-7xl mx-auto px-6">
            <p class="font-medium text-slate-300">Generated dynamically via the InsightAI microservice framework.</p>
            <p class="text-slate-500 mt-1">&copy; 2026 InsightAI Report Engine. All rights reserved.</p>
        </div>
    </footer>

    <!-- Plotly rendering scripts (Fixed auto-sizing bug) -->
    <script>
        function renderCharts() {
            {% if charts %}
                {% for chart in charts %}
                try {
                    var rawData = {{ chart.plotly_json }};
                    rawData.layout = rawData.layout || {};
                    rawData.layout.autosize = true;
                    delete rawData.layout.height;
                    delete rawData.layout.width;
                    rawData.layout.margin = rawData.layout.margin || { l: 45, r: 25, t: 45, b: 45 };
                    
                    Plotly.newPlot(
                        "plotly_container_{{ loop.index }}",
                        rawData.data,
                        rawData.layout,
                        {
                            responsive: true,
                            displayModeBar: true,
                            modeBarButtonsToRemove: ['lasso2d','select2d','autoScale2d'],
                            displaylogo: false,
                            scrollZoom: false
                        }
                    );
                } catch(e) {
                    console.error("Failed to render Plotly chart {{ loop.index }}:", e);
                    var el = document.getElementById("plotly_container_{{ loop.index }}");
                    if (el) el.innerHTML =
                        "<div style='height:100%;display:flex;align-items:center;justify-content:center;color:#e11d48;font-size:0.8rem;background:#fff1f2;border-radius:10px;padding:16px;text-align:center;'>Chart error: " + e.message + "</div>";
                }
                {% endfor %}

                setTimeout(function() {
                    window.dispatchEvent(new Event('resize'));
                }, 100);
            {% endif %}
        }
        
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            renderCharts();
        } else {
            document.addEventListener('DOMContentLoaded', renderCharts);
        }
    </script>
</body>
</html>
"""

def generate_report_html(title: str, dataset_id: str, row_count: int, col_count: int, columns: dict, charts: list[dict], ai_analysis_html: str) -> str:
    """
    Assembles dataset properties, visual components, and LLM text analysis
    into a beautiful single-page interactive HTML dashboard report.
    """
    # Generate IST timestamp for the report header
    IST = timezone(timedelta(hours=5, minutes=30))
    generated_at = datetime.now(IST).strftime('%d %b %Y, %I:%M %p IST')

    html_template = Template(HTML_REPORT_TEMPLATE)
    return html_template.render(
        title=title,
        dataset_id=dataset_id,
        row_count=row_count,
        col_count=col_count,
        columns=columns,
        charts=charts,
        ai_analysis_html=ai_analysis_html,
        generated_at=generated_at
    )