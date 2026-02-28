import markdown
import os
import subprocess
import shutil
from pypdf import PdfReader, PdfWriter

def generate_cv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, 'CV.md')
    html_file = os.path.join(base_dir, 'CV.html')
    pdf_file = os.path.join(base_dir, 'CV.pdf')
    png_file = os.path.join(base_dir, 'CV.png')

    # Modern CSS with Grid - Clean & Professional
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { box-sizing: border-box; }

    body {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        background-color: #fff;
        color: #334155;
        font-size: 12.8px;
        line-height: 1.42;
        width: 210mm;
        height: 296mm;
        overflow: hidden;
    }
    
    .page-container {
        display: grid;
        grid-template-columns: 70mm 1fr;
        height: 296mm;
        width: 210mm;
    }

    .sidebar {
        background-color: #f8fafc;
        color: #334155;
        padding: 12px 14px;
        display: flex;
        flex-direction: column;
        gap: 12px;
        border-right: 1px solid #e2e8f0;
    }

    .profile-pic-container {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        border: 3px solid #fff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        margin: 0 auto;
    }

    .profile-pic {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .contact-section h1 {
        font-size: 24px;
        font-weight: 800;
        color: #1e293b;
        margin: 0 0 6px 0;
        text-align: center;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }

    .subtitle {
        text-align: center;
        color: #2563eb;
        font-weight: 600;
        margin-bottom: 8px;
        display: block;
        font-size: 13px;
        line-height: 1.25;
    }

    .contact-details {
        display: flex;
        flex-direction: column;
        gap: 6px;
        font-size: 11px;
    }

    .contact-details p { margin: 0; display: flex; align-items: center; gap: 8px; }
    .contact-details a { 
        color: #475569; 
        text-decoration: none; 
        font-weight: 500;
        border-bottom: 1px dotted #94a3b8;
    }

    .section-title {
        font-size: 12.5px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        font-weight: 700;
        border-bottom: 2px solid #cbd5e1;
        padding-bottom: 4px;
        margin-bottom: 8px;
    }

    .main-content {
        padding: 28px 28px 8px 28px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .main-section {
        margin-bottom: 6px;
    }
    
    .main-title {
        font-size: 15.5px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 3px;
        display: flex;
        align-items: center;
        gap: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 2px;
    }

    .about-text {
        text-align: left;
        margin-bottom: 2px;
        color: #334155;
        text-align: justify;
    }

    .item-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 1px;
    }

    .item-title {
        font-weight: 700;
        color: #1e293b;
        font-size: 14px;
    }

    .item-date {
        color: #64748b;
        font-size: 10.5px;
        font-weight: 500;
        white-space: nowrap; 
        background: #f1f5f9;
        padding: 1.5px 6px;
        border-radius: 4px;
    }

    .item-desc {
        color: #475569;
        font-size: 12.2px;
        margin: 0 0 1px 0;
        line-height: 1.45;
    }
    
    .link-style {
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
    }

    .skills-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 8px;
    }
    .skill-category {
        font-size: 11.5px;
        line-height: 1.3;
    }
    .skill-category strong { color: #0f172a; font-weight: 600; }

    @media print {
        @page { margin: 0; }
        body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
    """

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Tom de Groot - CV</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="page-container">
            <!-- SIDEBAR -->
            <div class="sidebar">
                <div class="profile-pic-container">
                    <img src="Profile_pic.jpg" class="profile-pic" alt="Profile">
                </div>
                
                <div class="contact-section">
                    <h1>Tom de Groot</h1>
                    <span class="subtitle">Frontier Evaluation &<br>Formal Verification</span>
                    
                    <div class="contact-details">
                        <p>Grijpskerk, NL</p>
                        <p><a href="tel:+31631490416">+31 6 314 90 416</a></p>
                        <p><a href="mailto:tomthegreatest04@gmail.com">tomthegreatest04@gmail.com</a></p>
                        <p><a href="https://github.com/Tomodovodoo">github.com/Tomodovodoo</a></p>
                        <p><a href="https://x.com/Tomodovodoo">x.com/Tomodovodoo</a></p>
                    </div>
                </div>

                <div>
                    <div class="section-title">Technical Stack</div>
                    <div class="skills-grid">
                        <div class="skill-category"><strong>ML/Agents:</strong> TensorFlow, n8n, OpenClaw, Slurm</div>
                        <div class="skill-category"><strong>Formal:</strong> Lean 4, mathlib, Lake, CI/CD for proofs, auto-formalization.</div>
                        <div class="skill-category"><strong>Tools:</strong> Git, GitHub, Linux/HPC, VS Code, Docker, Numba/Njit</div>
                        <div class="skill-category"><strong>Software Languages:</strong> Python, Lean.</div>
                        <div class="skill-category"><strong>Spoken Languages:</strong> Dutch, English.</div>
                    </div>
                </div>

                <div>
                    <div class="section-title">Education</div>
                    <div class="job-item" style="margin-bottom: 8px;">
                        <div class="item-title">BSc Chemistry</div>
                        <div class="item-desc" style="margin-bottom:0;">University of Groningen</div>
                        <div class="item-desc" style="font-size: 10.5px; color:#64748b; margin-bottom:0;">2021 - 2025</div>
                        <div class="item-desc" style="font-style: italic; font-size: 10.5px; margin-bottom: 2px;">Track: Chemistry of Life</div>
                        <div class="item-desc" style="font-size: 10px; line-height: 1.2; color:#334155;">
                            <strong>Thesis:</strong> Evaluating and Optimizing NMR Prediction with Graph Neural Networks<br>(Chem-AI)
                        </div>
                    </div>
                </div>

                <div>
                    <div class="section-title">Awards</div>
                    <div class="job-item" style="margin-bottom: 5px;">
                        <div class="item-title" style="font-size: 11px;"><a href="https://www.chess.com/news/view/2021-chesscom-awards-winners#member" class="link-style">Chess.com Member of the Year 2021</a></div>
                    </div>
                    <div class="job-item">
                        <div class="item-title" style="font-size: 11px;"><a href="https://harmonic.fun/news#blog-post-mathematician-sponsorships" class="link-style">Harmonic Rising Mathematician Grant</a></div>
                        <div class="item-desc" style="font-size: 10px;">(Details on request)</div>
                    </div>
                </div>
            </div>

            <!-- MAIN CONTENT -->
            <div class="main-content">
                <div class="main-section">
                    <div class="main-title">About Me</div>
                    <div class="about-text">
                        Hi, I'm Tom. I'm a BSc Chemistry graduate from the University of Groningen (Life Sciences track). 
                        My thesis in the Pollice Group focused on optimizing NMR prediction with GNNs. 
                        Post-graduation, I pivoted to mathematics and formal methods, becoming an active contributor to the <strong>PNT+</strong> Lean formalization project. 
                        I've built a strong foundation in student mathematics and programming, which I use to design and evaluate AI systems, their output, and create frameworks for them.
                    </div>
                    <div class="about-text" style="margin-top: 4px;">
                        <strong>Goals!</strong> Focusing on frontier model capability work, stress-testing, and evaluation design. 
                        My current goal is to use agentic systems and formal verification (Lean 4) to contribute to open science in mathematics.
                    </div>
                </div>

                <div class="main-section">
                    <div class="main-title">Selected Research & Formalization</div>
                    
                    <div class="project-item">
                        <div class="item-header">
                            <span class="item-title">Prime Number Theorem And (PNT+)</span>
                            <span class="item-date">Late 2025 - Present</span>
                        </div>
                        <p class="item-desc" style="margin-bottom: 3px;">
                            Active contributor to the Lean 4 formalization project led by Alex Kontorovich and Terence Tao. 
                            Using an AI system called Aristotle, I have formalized multiple intermediate theorems, and I am a recent maintainer of the Aristotle branch alongside Pietro Monticone.
                        </p>
                        <p class="item-desc">
                            My current focus herein is the scaling up of Aristotle and other agentic systems to formalize more mathematics.
                            <a href="https://github.com/AlexKontorovich/PrimeNumberTheoremAnd/pulls?q=is%3Apr+author%3ATomodovodoo" class="link-style">Merged PRs</a>
                        </p>
                    </div>

                    <div class="project-item">
                        <div class="item-header">
                            <span class="item-title">First Proof Problem 9 (Lean-verified Solution)</span>
                            <span class="item-date">Feb 2026</span>
                        </div>
                        <p class="item-desc" style="margin-bottom: 3px;">
                            Produced the only credible formalized solution during the 7 day challenge, recognized by among others <strong>Kevin Buzzard</strong> and <strong>Daniel Litt</strong>, who gave it the context of "gold standard of LLM-aided mathematics." 
                            Created an autonomous agent that worked on the informal proof, and orchestrated multiple LLM agents to formalize it in Lean 4.
                            <a href="https://github.com/Tomodovodoo/firstproof" class="link-style">View Repository</a>
                        </p>
                    </div>
                </div>

                <div class="main-section">
                    <div class="main-title">Engineering Projects</div>
                    <div class="project-item">
                        <div class="item-header">
                            <span class="item-title">BaanSolliciteren (Agentic Job Automation)</span>
                        </div>
                        <p class="item-desc" style="margin-bottom: 4px;">
                            Engineered a semi-agentic system to automate my job search and its documentation. Built a custom <strong>Gmail MCP server</strong> (Model Context Protocol) to enable real-time status tracking and ranking of vacancies.
                        </p>
                        <p class="item-desc">
                            Implemented HTML-to-JSON schema parsing and automated LLM-based fit-scoring. Developed logic to cross-reference vacancy descriptions against personal descriptors, significantly reducing manual review time.
                        </p>
                    </div>
                    
                     <div class="project-item">
                        <div class="item-header">
                            <span class="item-title">Technical Collection & Visualizations</span>
                        </div>
                        <p class="item-desc">
                           Multi-year repository of technical interests and explorations: including from-scratch audio-to-text implementations and interactive visualizations of high-dimensional datasets (e.g., vaccine distribution and water quality metrics). Focused on extracting insights from real-world data.
                           <a href="https://github.com/Tomodovodoo/Collection-of-Projects" class="link-style">GitHub</a>
                        </p>
                    </div>
                </div>

                <div class="main-section">
                    <div class="main-title">Professional Experience</div>
                    
                    <div class="job-item">
                        <div class="item-header">
                            <span class="item-title">Transcom (for Odido)</span>
                            <span class="item-date">2024</span>
                        </div>
                        <p class="item-desc">Demonstrated reliable performance in customer service, maintaining consistent top-tier customer satisfaction ratings and learning to explain at every level.</p>
                    </div>

                    <div class="job-item">
                        <div class="item-header">
                            <span class="item-title">Teamspot (Regional Director)</span>
                            <span class="item-date">2022 - 2024</span>
                        </div>
                        <p class="item-desc">Coordinated regional school projects and taught teachers, performed technical testing/data entry within an Agile/Jira environment, alongside in-depth bug testing and general responsibilities.</p>
                    </div>

                    <div class="job-item">
                        <div class="item-header">
                            <span class="item-title">Chess.com</span>
                            <span class="item-date">2022</span>
                        </div>
                        <p class="item-desc">Moderated and proctored international chess events; recognized as <strong>Member of the Year 2021</strong> for community ownership and chess coaching.</p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Write HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Generated {html_file}")

    # Find Browser (Edge is standard on Windows)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    browser_exe = None
    for path in edge_paths:
        if os.path.exists(path):
            browser_exe = path
            break
    
    if not browser_exe:
        print("Error: Could not find Microsoft Edge executable.")
        return

    # Generate PDF
    print(f"Generating PDF using {browser_exe}...")
    subprocess.run([
        browser_exe,
        "--headless",
        "--print-to-pdf=" + pdf_file,
        "--no-pdf-header-footer",
        html_file
    ], check=True, shell=True)
    
    # Post-process to ensure single page
    print("Post-processing PDF to strict 1-page limit...")
    try:
        reader = PdfReader(pdf_file)
        if len(reader.pages) > 1:
            print(f"PDF has {len(reader.pages)} pages. Trimming to 1 page...")
            writer = PdfWriter()
            writer.add_page(reader.pages[0])
            with open(pdf_file, "wb") as f:
                writer.write(f)
            print("Trimmed to single page.")
        else:
            print("PDF is already 1 page.")
    except Exception as e:
        print(f"Warning: Could not trim PDF: {e}")

    print(f"Generated {pdf_file}")

    # Generate Screenshot (PNG)
    # Dimensions for Sidebar layout: Keep consistent
    print(f"Generating PNG preview...")
    subprocess.run([
        browser_exe,
        "--headless",
        "--screenshot=" + png_file,
        "--window-size=794,1123", 
        "--force-device-scale-factor=2",
        html_file
    ], check=True, shell=True)
    print(f"Generated {png_file}")

if __name__ == "__main__":
    generate_cv()
